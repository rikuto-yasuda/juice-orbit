from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import pandas as pd
from matplotlib.patches import Arc

from juice_orbit import (
    prepare_juice,
    make_times,
    get_positions,
)


# ============================================================
# Settings
# ============================================================

# SPICE kernels / JUICE orbit data
SPICE_DATA_DIR = Path.home() / "spice_data" / "JUICE"

# Output directory
RESULTS_DIR = Path(
    "/work1/rikutoyasuda/tools/python_JUICE/"
    "orbit_check/juice_flyby_results"
)

# Calculation range around Flyby center
HALF_WINDOW_MINUTES = 60

# Time resolution
STEP_MINUTES = 1


# ============================================================
# Satellite radii [km]
# ============================================================

MOON_RADII_KM = {
    "CALLISTO": 2410.3,
    "EUROPA": 1560.8,
    "GANYMEDE": 2634.1,
}


# ============================================================
# Flyby information
# ============================================================

FLYBYS = [
    {
        "moon": "CALLISTO",
        "flyby": 3,
        "start": "2032-09-10 22:16:50",
        "end": "2032-09-10 22:21:50",
    },
    {
        "moon": "CALLISTO",
        "flyby": 4,
        "start": "2032-09-27 14:50:04",
        "end": "2032-09-27 14:55:04",
    },
    {
        "moon": "CALLISTO",
        "flyby": 6,
        "start": "2032-10-14 07:14:49",
        "end": "2032-10-14 07:21:49",
    },
    {
        "moon": "CALLISTO",
        "flyby": 7,
        "start": "2032-10-30 23:39:26",
        "end": "2032-10-30 23:47:26",
    },
    {
        "moon": "CALLISTO",
        "flyby": 20,
        "start": "2034-02-15 02:32:58",
        "end": "2034-02-15 02:38:58",
    },
    {
        "moon": "EUROPA",
        "flyby": 1,
        "start": "2032-07-02 16:06:43",
        "end": "2032-07-02 16:18:43",
    },
    {
        "moon": "EUROPA",
        "flyby": 2,
        "start": "2032-07-16 22:56:49",
        "end": "2032-07-16 23:09:49",
    },
    {
        "moon": "GANYMEDE",
        "flyby": 1,
        "start": "2031-07-21 07:02:41",
        "end": "2031-07-21 07:06:41",
    },
    {
        "moon": "GANYMEDE",
        "flyby": 2,
        "start": "2032-02-06 19:46:19",
        "end": "2032-02-06 19:52:19",
    },
    {
        "moon": "GANYMEDE",
        "flyby": 3,
        "start": "2032-04-11 04:11:17",
        "end": "2032-04-11 04:15:17",
    },
]


# ============================================================
# Common plot functions
# ============================================================

def add_moon_circle(
    ax,
    moon,
):
    """
    Draw the target moon as a circle with its actual radius.

    The coordinate system is centered on the moon,
    so the moon center is at (0, 0).
    """

    radius = MOON_RADII_KM[moon]

    circle = Circle(
        (0, 0),
        radius,
        fill=False,
        linewidth=2.0,
        label=f"{moon} (R={radius:.1f} km)",
        zorder=5,
    )

    ax.add_patch(circle)


def add_common_markers(
    ax,
    juice,
    x_column,
    y_column,
    center,
    occ_start,
    occ_end,
):
    """
    Add Flyby center, occultation start and end markers.
    """

    # --------------------------------------------------------
    # Flyby center
    # --------------------------------------------------------

    center_row = juice.loc[
        (juice["utc"] - center).abs().idxmin()
    ]

    ax.scatter(
        center_row[x_column],
        center_row[y_column],
        marker="x",
        s=80,
        label="Flyby center",
        zorder=7,
    )

    # --------------------------------------------------------
    # Occultation start
    # --------------------------------------------------------

    start_row = juice.loc[
        (juice["utc"] - occ_start).abs().idxmin()
    ]

    ax.scatter(
        start_row[x_column],
        start_row[y_column],
        marker="^",
        s=60,
        label="Occultation start",
        zorder=7,
    )

    # --------------------------------------------------------
    # Occultation end
    # --------------------------------------------------------

    end_row = juice.loc[
        (juice["utc"] - occ_end).abs().idxmin()
    ]

    ax.scatter(
        end_row[x_column],
        end_row[y_column],
        marker="v",
        s=60,
        label="Occultation end",
        zorder=7,
    )


def setup_axes(
    ax,
    x_label,
    y_label,
):
    """
    Common axis settings.

    aspect='equal' guarantees that the physical scale is identical
    in both directions:
        1 km in X/Y/Z = same physical length on the figure.
    """

    ax.axhline(
        0,
        linewidth=0.5,
        linestyle=":",
    )

    ax.axvline(
        0,
        linewidth=0.5,
        linestyle=":",
    )

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    # --------------------------------------------------------
    # IMPORTANT:
    # Equal physical scale in X and Y directions.
    # --------------------------------------------------------

    ax.set_aspect(
        "equal",
        adjustable="datalim",
    )

    ax.grid(
        True,
        alpha=0.3,
    )

    ax.legend()


# ============================================================
# XY plot
# ============================================================

def plot_xy(
    juice,
    moon,
    flyby,
    center,
    occ_start,
    occ_end,
    output_path,
):
    """
    JUICE trajectory in the satellite-centered
    Jupiter-facing XY plane.

    X: Jupiter-facing direction
    Y: perpendicular direction in the equatorial plane
    """

    fig, ax = plt.subplots(
        figsize=(8, 8),
    )

    # --------------------------------------------------------
    # JUICE trajectory
    # --------------------------------------------------------

    ax.plot(
        juice["x_km"],
        juice["y_km"],
        linewidth=1.5,
        label="JUICE",
        zorder=3,
    )

    # --------------------------------------------------------
    # Moon
    # --------------------------------------------------------

    add_moon_circle(
        ax,
        moon,
    )

    # --------------------------------------------------------
    # Event markers
    # --------------------------------------------------------

    add_common_markers(
        ax=ax,
        juice=juice,
        x_column="x_km",
        y_column="y_km",
        center=center,
        occ_start=occ_start,
        occ_end=occ_end,
    )

    # --------------------------------------------------------
    # Axis settings
    # --------------------------------------------------------

    setup_axes(
        ax,
        "X [km] — Jupiter-facing direction",
        "Y [km]",
    )

    ax.set_title(
        f"JUICE — {moon} Flyby {flyby:02d}\n"
        "Jupiter-facing frame (XY)"
    )

    fig.tight_layout()

    fig.savefig(
        output_path,
        dpi=200,
    )

    plt.close(fig)


# ============================================================
# XZ plot
# ============================================================

def plot_xz(
    juice,
    moon,
    flyby,
    center,
    occ_start,
    occ_end,
    output_path,
    jupiter_row,
):
    """
    JUICE trajectory in the satellite-centered
    Jupiter-facing XZ plane.

    X: Jupiter-facing direction
    Z: satellite north direction
    """

    fig, ax = plt.subplots(
        figsize=(8, 8),
    )

    # --------------------------------------------------------
    # JUICE trajectory
    # --------------------------------------------------------

    ax.plot(
        juice["x_km"],
        juice["z_km"],
        linewidth=1.5,
        label="JUICE",
        zorder=3,
    )

    # --------------------------------------------------------
    # Moon
    # --------------------------------------------------------

    add_moon_circle(
        ax,
        moon,
    )

    # --------------------------------------------------------
    # Event markers
    # --------------------------------------------------------

    add_common_markers(
        ax=ax,
        juice=juice,
        x_column="x_km",
        y_column="z_km",
        center=center,
        occ_start=occ_start,
        occ_end=occ_end,
    )


    # --------------------------------------------------------
    # Jupiter direction in the XZ plane
    # --------------------------------------------------------

    jx = float(jupiter_row["x_km"])
    jz = float(jupiter_row["z_km"])

    norm = np.hypot(jx, jz)

    if norm > 0:
        # Jupiter direction unit vector
        ux = jx / norm
        uz = jz / norm

        # Set a visible arrow length based on the trajectory scale
        scale = max(
            float(juice["x_km"].abs().max()),
            float(juice["z_km"].abs().max()),
            MOON_RADII_KM[moon],
        )

        length = 0.25 * scale

        end_x = ux * length
        end_z = uz * length

        # Draw the arrow shaft as a real data line.
        # This also includes the arrow endpoint in autoscaling.
        ax.plot(
            [0, end_x],
            [0, end_z],
            color="red",
            linestyle="--",
            linewidth=1.8,
            label="Jupiter direction (not to scale)",
            zorder=6,
        )

        # Draw the arrowhead.
        ax.annotate(
            "",
            xy=(end_x, end_z),
            xytext=(0, 0),
            arrowprops=dict(
                arrowstyle="->",
                color="red",
                linewidth=1.8,
            ),
            zorder=7,
        )

        # Explicitly include the origin and arrow endpoint in the limits.
        ax.update_datalim(
            np.array([
                [0, 0],
                [end_x, end_z],
            ])
        )
        ax.autoscale_view()
        # 凡例用
        ax.plot(
            [],
            [],
            color="red",
            linestyle="--",
            label="Jupiter direction (not to scale)",
        )

    # --------------------------------------------------------
    # Axis settings
    # --------------------------------------------------------

    setup_axes(
        ax,
        "X [km] — Jupiter-facing direction",
        "Z [km] — North",
    )

    ax.set_title(
        f"JUICE — {moon} Flyby {flyby:02d}\n"
        "Jupiter-facing frame (XZ)"
    )

    fig.tight_layout()

    fig.savefig(
        output_path,
        dpi=200,
    )

    plt.close(fig)


# ============================================================
# YZ plot
# ============================================================

def plot_yz(
    juice,
    moon,
    flyby,
    center,
    occ_start,
    occ_end,
    output_path,
):
    """
    JUICE trajectory in the satellite-centered
    Jupiter-facing YZ plane.

    Y: perpendicular to Jupiter-facing direction
    Z: satellite north direction
    """

    fig, ax = plt.subplots(
        figsize=(8, 8),
    )

    # --------------------------------------------------------
    # JUICE trajectory
    # --------------------------------------------------------

    ax.plot(
        juice["y_km"],
        juice["z_km"],
        linewidth=1.5,
        label="JUICE",
        zorder=3,
    )

    # --------------------------------------------------------
    # Moon
    # --------------------------------------------------------

    add_moon_circle(
        ax,
        moon,
    )

    # --------------------------------------------------------
    # Event markers
    # --------------------------------------------------------

    add_common_markers(
        ax=ax,
        juice=juice,
        x_column="y_km",
        y_column="z_km",
        center=center,
        occ_start=occ_start,
        occ_end=occ_end,
    )

    # --------------------------------------------------------
    # Axis settings
    # --------------------------------------------------------

    setup_axes(
        ax,
        "Y [km]",
        "Z [km] — North",
    )

    ax.set_title(
        f"JUICE — {moon} Flyby {flyby:02d}\n"
        "Jupiter-facing frame (YZ)"
    )

    fig.tight_layout()

    fig.savefig(
        output_path,
        dpi=200,
    )

    plt.close(fig)


def plot_x_ryz(
    juice,
    moon,
    flyby,
    center,
    occ_start,
    occ_end,
    output_path,
):
    """Plot JUICE trajectory in the X-RYZ plane."""

    radius = MOON_RADII_KM[moon]

    fig, ax = plt.subplots(figsize=(8, 8))

    # JUICE trajectory
    ax.plot(
        juice["x_km"],
        juice["ryz"],
        linewidth=1.5,
        label="JUICE",
    )

    # Satellite cross-section:
    # RYZ is always non-negative, so show the upper semicircle.
    ax.add_patch(
        Arc(
            (0, 0),
            width=2 * radius,
            height=2 * radius,
            theta1=0,
            theta2=180,
            linewidth=2.0,
            label=f"{moon} (R={radius:.1f} km)",
            zorder=5,
        )
    )

    # Flyby center
    center_row = juice.loc[
        (juice["utc"] - center).abs().idxmin()
    ]

    ax.scatter(
        center_row["x_km"],
        center_row["ryz"],
        marker="x",
        s=80,
        label="Flyby center",
        zorder=7,
    )

    # Occultation start
    start_row = juice.loc[
        (juice["utc"] - occ_start).abs().idxmin()
    ]

    ax.scatter(
        start_row["x_km"],
        start_row["ryz"],
        marker="^",
        s=60,
        label="Occultation start",
        zorder=7,
    )

    # Occultation end
    end_row = juice.loc[
        (juice["utc"] - occ_end).abs().idxmin()
    ]

    ax.scatter(
        end_row["x_km"],
        end_row["ryz"],
        marker="v",
        s=60,
        label="Occultation end",
        zorder=7,
    )

    ax.axhline(0, linewidth=0.5, linestyle=":", color="gray")
    ax.axvline(0, linewidth=0.5, linestyle=":", color="gray")

    ax.set_xlabel("X [km] — Jupiter-facing direction")
    ax.set_ylabel(r"RYZ [km] = $\sqrt{Y^2 + Z^2}$")

    ax.set_title(
        f"JUICE — {moon} Flyby {flyby:02d}\n"
        "Jupiter-facing frame (X-RYZ)"
    )

    # Equal physical scale on both axes
    ax.set_aspect("equal", adjustable="datalim")

    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)

# ============================================================
# Process one Flyby
# ============================================================

def process_flyby(
    workspace,
    flyby_info,
):
    """
    Calculate JUICE trajectory for one Flyby.

    Calculation:
        Flyby center ±30 minutes

    Time resolution:
        1 minute

    Coordinate system:
        observer = target moon
        frame    = JUPITER_FACING

    Targets:
        JUICE + target moon

    Jupiter is intentionally excluded.
    """

    moon = flyby_info["moon"]
    flyby = flyby_info["flyby"]

    # --------------------------------------------------------
    # UTC-aware timestamps
    # --------------------------------------------------------

    start = pd.Timestamp(
        flyby_info["start"],
        tz="UTC",
    )

    end = pd.Timestamp(
        flyby_info["end"],
        tz="UTC",
    )

    # --------------------------------------------------------
    # Flyby center
    # --------------------------------------------------------

    center = start + (end - start) / 2

    # --------------------------------------------------------
    # Calculation range
    # --------------------------------------------------------

    calc_start = (
        center
        - pd.Timedelta(
            minutes=HALF_WINDOW_MINUTES
        )
    )

    calc_end = (
        center
        + pd.Timedelta(
            minutes=HALF_WINDOW_MINUTES
        )
    )

    # --------------------------------------------------------
    # Print information
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print(f"{moon} Flyby {flyby:02d}")
    print("=" * 80)

    print(
        f"Occultation : "
        f"{start.strftime('%Y-%m-%d %H:%M:%S')} - "
        f"{end.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    print(
        f"Center      : "
        f"{center.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    print(
        f"Calculation : "
        f"{calc_start.strftime('%Y-%m-%d %H:%M:%S')} - "
        f"{calc_end.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    # --------------------------------------------------------
    # Generate time array
    # --------------------------------------------------------

    times = make_times(
        calc_start.strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        calc_end.strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        step=STEP_MINUTES,
        unit="minutes",
    )

    # --------------------------------------------------------
    # Get positions
    # --------------------------------------------------------

    data = get_positions(
        times,
        targets=[
            "JUICE",
            moon,
            "JUPITER"
        ],
        observer=moon,
        frame="JUPITER_FACING",
        output="full",
    )

    # --------------------------------------------------------
    # Make UTC column timezone-aware
    # --------------------------------------------------------

    data["utc"] = pd.to_datetime(
        data["utc"],
        utc=True,
    )

    # 木星の位置を取得（Flyby中心に最も近い時刻）
    jupiter_data = data[data["target"] == "JUPITER"].copy()

    jupiter_idx = (
        jupiter_data["utc"] - center
    ).abs().idxmin()

    jupiter_row = jupiter_data.loc[jupiter_idx]

    # 木星の行はCSVと軌道プロットから除外
    data = data[data["target"] != "JUPITER"].copy()

    # YZ平面内の距離を計算
    data["ryz"] = np.sqrt(
        data["y_km"] ** 2 + data["z_km"] ** 2
    )

    # --------------------------------------------------------
    # Output directory
    # --------------------------------------------------------

    output_dir = (
        RESULTS_DIR
        / moon
        / f"Flyby_{flyby:02d}"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Save CSV
    # --------------------------------------------------------

    csv_path = output_dir / "orbit.csv"

    data.to_csv(
        csv_path,
        index=False,
    )

    # --------------------------------------------------------
    # JUICE only for trajectory plots
    #
    # The satellite itself is represented by a circle
    # centered at the origin.
    # --------------------------------------------------------

    juice = data[
        data["target"] == "JUICE"
    ].copy()



    # --------------------------------------------------------
    # XY plot
    # --------------------------------------------------------

    xy_path = output_dir / "orbit_xy.png"

    plot_xy(
        juice=juice,
        moon=moon,
        flyby=flyby,
        center=center,
        occ_start=start,
        occ_end=end,
        output_path=xy_path,
    )

    # --------------------------------------------------------
    # XZ plot
    # --------------------------------------------------------

    xz_path = output_dir / "orbit_xz.png"

    plot_xz(
        juice=juice,
        moon=moon,
        flyby=flyby,
        center=center,
        occ_start=start,
        occ_end=end,
        output_path=xz_path,
        jupiter_row=jupiter_row,
    )

    # --------------------------------------------------------
    # YZ plot
    # --------------------------------------------------------

    yz_path = output_dir / "orbit_yz.png"

    plot_yz(
        juice=juice,
        moon=moon,
        flyby=flyby,
        center=center,
        occ_start=start,
        occ_end=end,
        output_path=yz_path,
    )


    plot_x_ryz(
    juice=juice,
    moon=moon,
    flyby=flyby,
    center=center,
    occ_start=start,
    occ_end=end,
    output_path=output_dir / "orbit_x_ryz.png",
  )

    # --------------------------------------------------------
    # Print output paths
    # --------------------------------------------------------

    print(
        f"CSV         : {csv_path}"
    )

    print(
        f"XY plot     : {xy_path}"
    )

    print(
        f"XZ plot     : {xz_path}"
    )

    print(
        f"YZ plot     : {yz_path}"
    )

    print(
        f"Data points : {len(juice)} JUICE points"
    )

    return data


# ============================================================
# Main
# ============================================================

def main():

    # --------------------------------------------------------
    # Create output directory
    # --------------------------------------------------------

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Prepare JUICE SPICE data
    # --------------------------------------------------------

    print("=" * 80)
    print("Preparing JUICE SPICE data")
    print("=" * 80)

    workspace = prepare_juice(
        SPICE_DATA_DIR,
        results_subdir="flyby_orbit",
    )

    print()

    print(
        f"Output directory: {RESULTS_DIR}"
    )

    # --------------------------------------------------------
    # Process all Flybys
    # --------------------------------------------------------

    for flyby_info in FLYBYS:

        process_flyby(
            workspace,
            flyby_info,
        )

    # --------------------------------------------------------
    # Finished
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("ALL FLYBYS COMPLETED")
    print("=" * 80)

    print(
        f"Results saved to:\n{RESULTS_DIR}"
    )


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    main()