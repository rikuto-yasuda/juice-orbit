"""JUICE CReMA SPICE orbit queries and plots."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
from typing import Iterable, Literal, Sequence
from urllib.request import urlopen

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import spiceypy as spice

ESA_JUICE_KERNELS = "https://spiftp.esac.esa.int/data/SPICE/JUICE/kernels"
JUICE_METAKERNEL = "juice_crema_5_2.tm"
DEFAULT_TARGETS = ("JUICE", "IO", "EUROPA", "GANYMEDE", "CALLISTO")
OutputType = Literal["full", "xyz", "r_lat_lon"]


@dataclass(frozen=True)
class JuiceWorkspace:
    """Absolute paths for one local JUICE SPICE dataset and its results."""

    data_dir: Path
    meta_kernel: Path
    results_dir: Path


def prepare_juice(data_dir: str | Path, *, results_subdir: str = "output",
                  auto_download: bool = True, load: bool = True) -> JuiceWorkspace:
    """Prepare an absolute JUICE data directory, download and load kernels."""
    root = Path(data_dir).expanduser()
    if not root.is_absolute():
        raise ValueError("data_dir must be an absolute path")
    root = root.resolve()
    output_path = Path(results_subdir)
    if not results_subdir or output_path.is_absolute() or ".." in output_path.parts:
        raise ValueError("results_subdir must be a non-empty relative subdirectory")
    meta_kernel = root / "kernels" / "mk" / "juice_crema_5_2_orbit.tm"
    if auto_download:
        meta_kernel = download_orbit_kernels(root)
    elif not meta_kernel.is_file():
        raise FileNotFoundError(f"Orbit meta-kernel not found: {meta_kernel}")
    results_dir = root / output_path
    results_dir.mkdir(parents=True, exist_ok=True)
    if load:
        load_kernels(meta_kernel)
    return JuiceWorkspace(root, meta_kernel, results_dir)


def download_orbit_kernels(destination: str | Path,
                           metakernel: str = JUICE_METAKERNEL) -> Path:
    """Download the CReMA meta-kernel and position-query dependencies."""
    root = Path(destination).expanduser().resolve() / "kernels"
    mk_url = f"{ESA_JUICE_KERNELS}/mk/{metakernel}"
    source_mk_path = root / "mk" / metakernel
    source_mk_path.parent.mkdir(parents=True, exist_ok=True)
    if source_mk_path.is_file():
        text = source_mk_path.read_text(encoding="utf-8")
    else:
        text = _download_text(mk_url)
        source_mk_path.write_text(text, encoding="utf-8")
    required = {
        "fk/juice_v46.tf", "lsk/naif0012.tls", "pck/pck00011.tpc",
        "spk/de432s.bsp", "spk/jup365_19900101_20500101.bsp",
        "spk/noe-5-2023_20200101_20500101.bsp", "spk/juice_crema_5_2_v01.bsp",
    }
    available = set(re.findall(r"\$KERNELS/([^']+)", text))
    missing = required - available
    if missing:
        raise RuntimeError(f"The ESA meta-kernel changed; missing expected entries: {sorted(missing)}")
    for relative_path in sorted(required):
        local_path = root / relative_path
        if local_path.is_file() and local_path.stat().st_size > 0:
            continue
        local_path.parent.mkdir(parents=True, exist_ok=True)
        url = f"{ESA_JUICE_KERNELS}/{relative_path}"
        print(f"Downloading {relative_path}")
        partial = local_path.with_suffix(local_path.suffix + '.part')
        with urlopen(url, timeout=120) as response, partial.open('wb') as stream:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                stream.write(chunk)
        partial.replace(local_path)
    orbit_mk = root / "mk" / "juice_crema_5_2_orbit.tm"
    # Preserve ESA load precedence: later SPKs override earlier segments.
    ordered = [item for item in re.findall(r"\$KERNELS/([^']+)", text) if item in required]
    loads = "\n".join(f"  '$KERNELS/{item}'" for item in ordered)
    orbit_mk.write_text(
        "KPL/MK\n\\begindata\nPATH_VALUES = ( '..' )\nPATH_SYMBOLS = ( 'KERNELS' )\n"
        f"KERNELS_TO_LOAD = (\n{loads}\n)\n\\begintext\n", encoding="utf-8"
    )
    return orbit_mk


def load_kernels(meta_kernel: str | Path, *, clear_first: bool = True) -> None:
    """Load a local JUICE meta-kernel."""
    path = Path(meta_kernel).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Meta-kernel not found: {path}")
    if clear_first:
        spice.kclear()
    # Resolve this dataset's KERNELS paths relative to its mk directory,
    # without changing the process-wide working directory.
    text = path.read_text(encoding="utf-8")
    values = re.search(r"PATH_VALUES\s*=\s*\(\s*'([^']+)'\s*\)", text)
    symbols = re.search(r"PATH_SYMBOLS\s*=\s*\(\s*'KERNELS'\s*\)", text)
    entries = re.search(r"KERNELS_TO_LOAD\s*=\s*\((.*?)\)", text, re.S)
    if values and symbols and entries:
        root = (path.parent / values.group(1)).resolve()
        files = re.findall(r"'([^']+)'", entries.group(1))
        resolved = [Path(item.replace('$KERNELS', str(root))) for item in files]
        resolved = [(path.parent / item).resolve() for item in resolved]
        for item in resolved:
            if not item.is_file():
                raise FileNotFoundError(f"Kernel not found: {item}")
        for item in resolved:
            spice.furnsh(str(item))
    else:
        spice.furnsh(str(path))


def make_times(start: str | datetime, end: str | datetime | None = None,
               step: float = 1,
               unit: Literal["seconds", "minutes", "hours", "days"] = "days") -> list[str]:
    """Return UTC ISO timestamps. With no end, return a one-element list."""
    start_dt = _as_utc_datetime(start)
    if end is None:
        return [start_dt.isoformat().replace("+00:00", "Z")]
    end_dt = _as_utc_datetime(end)
    if step <= 0 or end_dt < start_dt:
        raise ValueError("step must be positive and end must not precede start")
    seconds = step * {"seconds": 1, "minutes": 60, "hours": 3600, "days": 86400}[unit]
    count = int((end_dt - start_dt).total_seconds() // seconds) + 1
    return [
        (start_dt + timedelta(seconds=i * seconds)).isoformat().replace("+00:00", "Z")
        for i in range(count)
    ]


def _jupiter_facing_rotation(state):
    """IAU-to-custom rotation and its time derivative, from Jupiter's state."""
    z = np.array([0., 0., 1.])
    normal = np.cross(z, state[:3])
    norm = np.linalg.norm(normal)
    if norm <= 1e-12 * np.linalg.norm(state[:3]):
        raise ValueError('Jupiter direction is parallel to the IAU pole; axes are undefined')
    y = normal / norm
    dy = (np.eye(3) - np.outer(y, y)) @ np.cross(z, state[3:]) / norm
    x = np.cross(y, z)
    dx = np.cross(dy, z)
    return np.array([x, y, z]), np.array([dx, dy, np.zeros(3)])


def get_positions(times: str | datetime | Sequence[str | datetime], *,
                  targets: Iterable[str] = DEFAULT_TARGETS,
                  observer: str = "JUPITER", frame: str = "IAU_JUPITER",
                  output: OutputType = "full", aberration: str = "NONE") -> pd.DataFrame:
    """Get target states relative to ``observer`` in ``frame``.

    JUPITER_FACING uses the moon's IAU north pole and points +X along the
    equatorial projection of the moon-to-Jupiter vector. It requires a
    Galilean moon observer and aberration='NONE'. Velocities include the
    derivative of this time-dependent rotation.
    """
    custom = frame.upper() == 'JUPITER_FACING'
    if custom:
        observer = observer.upper()
        if observer not in ('IO', 'EUROPA', 'GANYMEDE', 'CALLISTO'):
            raise ValueError('JUPITER_FACING requires a Galilean moon observer')
        if aberration.upper() != 'NONE':
            raise ValueError('JUPITER_FACING currently requires aberration=NONE')
        frame = 'JUPITER_FACING'
    base_frame = 'IAU_' + observer if custom else frame
    time_list = [times] if isinstance(times, (str, datetime)) else list(times)
    target_list = [targets] if isinstance(targets, str) else list(targets)
    if not time_list:
        raise ValueError("times cannot be empty")
    rows: list[dict[str, object]] = []
    for timestamp in time_list:
        utc = _as_utc_string(timestamp)
        et = spice.str2et(utc)
        if custom:
            jupiter, _ = spice.spkezr('JUPITER', et, base_frame, 'NONE', observer)
            rotation, derivative = _jupiter_facing_rotation(jupiter)
        for target in target_list:
            state, _ = spice.spkezr(target, et, base_frame, aberration, observer)
            if custom:
                state = np.concatenate((rotation @ state[:3],
                                        rotation @ state[3:] + derivative @ state[:3]))
            r, lon_rad, lat_rad = spice.reclat(state[:3])
            rows.append({
                "utc": utc, "target": target.upper(), "observer": observer.upper(), "frame": frame,
                "x_km": state[0], "y_km": state[1], "z_km": state[2], "r_km": r,
                "lon_deg": np.degrees(lon_rad), "lat_deg": np.degrees(lat_rad),
                "vx_km_s": state[3], "vy_km_s": state[4], "vz_km_s": state[5],
                "speed_km_s": float(np.linalg.norm(state[3:])),
            })
    data = pd.DataFrame(rows)
    common = ["utc", "target", "observer", "frame"]
    columns = {
        "full": common + ["x_km", "y_km", "z_km", "r_km", "lon_deg", "lat_deg",
                          "vx_km_s", "vy_km_s", "vz_km_s", "speed_km_s"],
        "xyz": common + ["x_km", "y_km", "z_km"],
        "r_lat_lon": common + ["r_km", "lat_deg", "lon_deg"],
    }
    try:
        return data[columns[output]]
    except KeyError as error:
        raise ValueError(f"output must be one of {tuple(columns)}") from error


def save_csv(data: pd.DataFrame, path: str | Path) -> Path:
    """Save orbit data as UTF-8 CSV."""
    output = Path(path).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output, index=False)
    return output


def plot_orbits(data: pd.DataFrame, path: str | Path, *,
                plane: Literal["xy", "xz", "yz"] = "xy",
                time_markers: int = 6, title: str | None = None) -> Path:
    """Plot trajectories, start/end points, direction arrows, and UTC labels."""
    needed = {"utc", "target", "x_km", "y_km", "z_km"}
    if not needed.issubset(data.columns):
        raise ValueError("plot_orbits requires data from get_positions(..., output='full' or 'xyz')")
    first, second = {"xy": ("x_km", "y_km"), "xz": ("x_km", "z_km"),
                     "yz": ("y_km", "z_km")}[plane]
    fig, ax = plt.subplots(figsize=(10, 8), layout="constrained")
    for target, group in data.groupby("target", sort=False):
        group = group.sort_values("utc")
        x, y = group[first].to_numpy(), group[second].to_numpy()
        line, = ax.plot(x, y, label=target)
        color = line.get_color()
        ax.scatter(x[0], y[0], s=34, marker="o", color=color)
        ax.scatter(x[-1], y[-1], s=42, marker="x", color=color)
        if len(group) > 1:
            mid = (len(group) - 2) // 2
            ax.annotate("", xy=(x[mid + 1], y[mid + 1]), xytext=(x[mid], y[mid]),
                        arrowprops={"arrowstyle": "->", "lw": 1.5, "color": color})
        marker_count = min(time_markers, len(group))
        for index in np.unique(np.linspace(0, len(group) - 1, marker_count, dtype=int)):
            label = str(group.iloc[index]["utc"])[:19].replace('T', '\n') + ' UTC'
            ax.annotate(label, (x[index], y[index]),
                        fontsize=7, xytext=(4, 4), textcoords="offset points")
    ax.scatter(0, 0, c="gold", edgecolors="black", s=95, marker="o", label="observer")
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(f"{first} (km)")
    ax.set_ylabel(f"{second} (km)")
    ax.set_title(title or f"JUICE geometry ({plane.upper()} plane)", fontsize=11)
    ax.text(0.01, 0.01, 'o: start   x: end   arrow: direction', transform=ax.transAxes, fontsize=8)
    ax.grid(True, alpha=.3)
    ax.legend()
    output = Path(path).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)
    return output


def _download_text(url: str) -> str:
    with urlopen(url, timeout=120) as response:
        return response.read().decode("utf-8")


def _as_utc_datetime(value: str | datetime) -> datetime:
    if isinstance(value, str):
        # Python 3.9 accepts 3 or 6 fractional digits; normalize ISO fractions.
        value = re.sub(r"(\d{2}:\d{2}:\d{2})\.(\d{1,6})(?=Z|[+-]|$)",
                       lambda match: match[1] + '.' + match[2].ljust(6, '0'), value)
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _as_utc_string(value: str | datetime) -> str:
    return _as_utc_datetime(value).isoformat(timespec="microseconds").replace("+00:00", "Z")
