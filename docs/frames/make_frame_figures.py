"""Schematic figures explaining each coordinate frame supported by juice_orbit.

Each figure shows the XY, XZ and YZ planes used by ``plot_orbits`` plus the
frame definition. Figures are schematic: sizes and tilts are not to scale.
Run with the package environment: ``python docs/frames/make_frame_figures.py``.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle, Wedge

plt.rcParams["font.family"] = ["Hiragino Sans", "Arial Unicode MS", "DejaVu Sans"]
OUT = Path(__file__).resolve().parent
AXIS_COLORS = {"X": "#d62728", "Y": "#2ca02c", "Z": "#1f77b4"}
BODY_COLORS = {"木星": "#d9a066", "衛星": "#9e9e9e", "太陽": "#f5c518", "地球": "#3b7dd8"}
LIM = 3.0
AXIS_LEN = 1.45
# (horizontal index, vertical index, out-of-screen axis, sign, viewer note)
VIEWS = {
    "xy": (0, 1, "Z", +1, "+Z 側から見下ろした図"),
    "xz": (0, 2, "Y", -1, "−Y 側から見た図"),
    "yz": (1, 2, "X", +1, "+X 側から見た図"),
}
UNIT = {"X": np.array([1., 0, 0]), "Y": np.array([0., 1, 0]), "Z": np.array([0., 0, 1])}


def unit(vector):
    vector = np.asarray(vector, float)
    return vector / np.linalg.norm(vector)


def project(vector, view):
    h, v, *_ = VIEWS[view]
    return np.array([vector[h], vector[v]])


def setup_panel(ax, view):
    ax.set_xlim(-LIM, LIM)
    ax.set_ylim(-LIM, LIM)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color("#bbbbbb")
    h, v, normal, sign, note = VIEWS[view]
    ax.set_title(f"{view} 面（{note}）", fontsize=12)
    ax.set_xlabel(f"{'xyz'[h]}_km →", fontsize=10)
    ax.set_ylabel(f"{'xyz'[v]}_km →", fontsize=10)
    # Symbol for the axis normal to the screen: ⊙ toward viewer, ⊗ away.
    x0, y0 = -LIM + 0.35, -LIM + 0.35
    color = AXIS_COLORS[normal]
    ax.scatter(x0, y0, s=170, facecolors="white", edgecolors=color, linewidths=1.6, zorder=6)
    ax.scatter(x0, y0, s=40 if sign > 0 else 60, marker="." if sign > 0 else "x",
               color=color, linewidths=1.6, zorder=7)
    ax.text(x0 + 0.3, y0, f"+{normal}：画面の{'手前' if sign > 0 else '奥'}向き",
            va="center", fontsize=9, color=color)


def draw_axes(ax, view):
    for name, vector in UNIT.items():
        p = project(vector, view)
        if np.linalg.norm(p) < 1e-9:
            continue
        ax.add_patch(FancyArrowPatch((0, 0), tuple(AXIS_LEN * p), arrowstyle="-|>",
                                     mutation_scale=18, lw=2.4, color=AXIS_COLORS[name], zorder=5))
        ax.text(*(AXIS_LEN * p + 0.22 * p), f"+{name}", color=AXIS_COLORS[name],
                fontsize=13, fontweight="bold", ha="center", va="center", zorder=6)


def draw_center(ax, name, label=None):
    ax.add_patch(Circle((0, 0), 1, facecolor=BODY_COLORS[name], edgecolor="#555555",
                        lw=1, alpha=.9, zorder=2))
    ax.text(0.0, -0.55, label or name, ha="center", va="center", fontsize=10, zorder=4)


def draw_direction(ax, view, direction, name, *, exact=True, text=None, alpha=1.0, below=False):
    """Dashed line toward a distant body; marker at the panel edge."""
    p = project(unit(direction), view)
    norm = np.linalg.norm(p)
    if norm < 0.5:
        _, _, normal, sign, _ = VIEWS[view]
        depth = unit(direction)["XYZ".index(normal)] * sign
        ax.text(LIM - 0.15, LIM - 0.3, f"{name}は画面の{'手前' if depth > 0 else '奥'}側",
                ha="right", fontsize=9, color="#444444")
        return
    tip = p / norm * 2.55
    # Start beyond the axis label so the line does not cross it.
    start = p / norm * 2.0
    ax.plot([start[0], tip[0]], [start[1], tip[1]], ls="--" if exact else ":", lw=1.4,
            color="#555555", alpha=alpha, zorder=3)
    ax.add_patch(Circle(tuple(tip), 0.2, facecolor=BODY_COLORS[name], edgecolor="#555555",
                        alpha=alpha, zorder=4))
    if abs(tip[0]) > abs(tip[1]):
        offset = np.array([-0.1, -0.42 if below else 0.42])
    else:
        offset = np.array([0.55, 0])
    ax.text(*(tip + offset), text or name, ha="center", va="center", fontsize=9.5, alpha=alpha)


def flow_arrows(ax, start, end, label, color="#8c564b", label_at=None):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=15,
                                 lw=1.8, color=color, zorder=4))
    ax.text(*(label_at or end), label, fontsize=9, color=color, ha="center", va="center")


def define_text(fig, lines, notes):
    ax = fig.add_axes([0.04, 0.03, 0.92, 0.27])
    ax.axis("off")
    ax.text(0, 1, "定義", fontsize=12, fontweight="bold", va="top")
    for i, (label, body) in enumerate(lines):
        color = AXIS_COLORS.get(label.strip("+")[:1], "#222222") if label.startswith("+") else "#222222"
        ax.text(0.0, 0.84 - i * 0.15, label, fontsize=11, fontweight="bold", color=color, va="top")
        ax.text(0.07, 0.84 - i * 0.15, body, fontsize=11, va="top")
    ax.text(0.53, 1, "読み方・注意", fontsize=12, fontweight="bold", va="top")
    for i, note in enumerate(notes):
        ax.text(0.53, 0.84 - i * 0.15, "・" + note, fontsize=10.5, va="top")


def figure(frame, subtitle, draw, lines, notes):
    fig = plt.figure(figsize=(16, 9))
    fig.suptitle(f"frame=\"{frame}\"　{subtitle}", fontsize=16, fontweight="bold", y=0.975)
    fig.text(0.5, 0.925, "模式図：天体の大きさ・距離・傾きは実際の縮尺ではありません", ha="center",
             fontsize=9.5, color="#666666")
    for i, view in enumerate(("xy", "xz", "yz")):
        ax = fig.add_axes([0.035 + i * 0.322, 0.33, 0.29, 0.56])
        setup_panel(ax, view)
        draw(ax, view)
        draw_axes(ax, view)
    define_text(fig, lines, notes)
    path = OUT / f"frame_{frame.replace('<衛星>', 'MOON')}.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


TILT = np.radians(14)  # exaggerated small angle used to show projections


def draw_iau_jupiter(ax, view):
    draw_center(ax, "木星")
    if view == "xy":
        ax.add_patch(Circle((0, 0), 2.35, fill=False, ls=":", color="#777777", zorder=1))
        ax.text(-1.7, 1.95, "衛星の軌道（例）", fontsize=9, color="#555555")
        ax.add_patch(FancyArrowPatch((1.25, -0.25), (0.35, 1.2), connectionstyle="arc3,rad=0.4",
                                     arrowstyle="-|>", mutation_scale=14, color="#444444", zorder=4))
        ax.text(1.0, 1.3, "自転", fontsize=9)
        ax.add_patch(FancyArrowPatch((-1.6, -1.75), (-2.25, -0.6), connectionstyle="arc3,rad=-0.25",
                                     arrowstyle="-|>", mutation_scale=14, color="#7f7f7f", zorder=4))
        ax.text(-2.85, -1.55, "衛星の\n見かけの動き", fontsize=8.5, color="#555555")
        ax.plot([1, 1.15], [0, 0], color="k", lw=3, zorder=6)
        ax.text(0.15, 0.3, "経度 0°", fontsize=8.5, zorder=6)
    else:
        ax.plot([-2.6, 2.6], [0, 0], ls=":", color="#777777", zorder=1)
        ax.text(1.35, -0.3, "赤道面", fontsize=9, color="#555555")
        ax.text(0.15, 1.15, "北極", fontsize=9, zorder=6)


def draw_iau_moon(ax, view):
    draw_center(ax, "衛星", "衛星\n（例：ガニメデ）")
    jupiter = np.array([np.cos(np.radians(-6)), np.sin(np.radians(-6)), 0])
    draw_direction(ax, view, jupiter, "木星", exact=False, text="木星（ほぼ +X）", below=True)
    if view == "xy":
        flow_arrows(ax, (-1.35, 0.6), (-1.35, -1.6), "公転方向", label_at=(-2.1, -1.0))
        flow_arrows(ax, (2.0, 2.6), (2.0, 1.2), "共回転\nプラズマ", color="#9467bd", label_at=(2.55, 1.9))
    elif view == "xz":
        ax.text(0.15, 1.15, "北極", fontsize=9, zorder=6)


def draw_jupiter_facing(ax, view):
    draw_center(ax, "衛星", "衛星")
    jupiter = np.array([np.cos(TILT), 0, np.sin(TILT)])
    draw_direction(ax, view, jupiter, "木星")
    if view == "xz":
        tip = 2.45 * np.array([np.cos(TILT), np.sin(TILT)])
        ax.plot([tip[0], tip[0]], [tip[1], 0], ls=":", color="#d62728", lw=1.2)
        ax.plot([0, tip[0]], [0, tip[1]], ls="--", lw=1.0, color="#999999", zorder=3)
        ax.text(1.2, -0.8, "木星方向を赤道面に\n投影した向き = +X", fontsize=8.5, color="#d62728")
        ax.text(0.15, 1.15, "北極", fontsize=9, zorder=6)
    if view == "xy":
        flow_arrows(ax, (-1.35, 0.6), (-1.35, -1.6), "公転方向", label_at=(-2.1, -1.0))
        flow_arrows(ax, (2.0, 2.6), (2.0, 1.2), "共回転\nプラズマ", color="#9467bd", label_at=(2.55, 1.9))


def draw_line_of_sight(ax, view, body, below=False):
    draw_center(ax, "衛星", "衛星")
    draw_direction(ax, view, np.array([1., 0, 0]), body, below=below)
    if view == "xz":
        pole = np.array([np.sin(TILT), np.cos(TILT)])
        ax.plot([0, 1.85 * pole[0]], [0, 1.85 * pole[1]], ls=":", color="#555555", lw=1.4, zorder=3)
        ax.text(1.85 * pole[0] + 0.05, 1.85 * pole[1] + 0.25, "衛星の北極軸", fontsize=8.5, color="#555555")
        ax.text(0.95, 2.45, "+Z は北極軸のうち\n+X に直交する成分", fontsize=8.5, color="#1f77b4")


def draw_sun_facing(ax, view):
    draw_line_of_sight(ax, view, "太陽")
    if view in ("xy", "xz"):
        ax.add_patch(Wedge((0, 0), 1, -90, 90, facecolor="#fff3b0", edgecolor="none", zorder=2.5, alpha=.95))
        ax.add_patch(Wedge((0, 0), 1, 90, 270, facecolor="#555555", edgecolor="none", zorder=2.5, alpha=.55))
        ax.text(0.5, 0.45, "昼", fontsize=10, ha="center", zorder=6)
        ax.text(-0.5, 0.45, "夜", fontsize=10, ha="center", color="white", zorder=6)
    else:
        ax.add_patch(Circle((0, 0), 1, facecolor="#fff3b0", edgecolor="#555555", zorder=2.5))
        ax.text(0, -1.4, "太陽から見ると全面が昼側", fontsize=9, ha="center", zorder=6)


def draw_earth_facing(ax, view):
    draw_line_of_sight(ax, view, "地球", below=(view == "xy"))
    if view in ("xy", "xz"):
        ax.add_patch(Rectangle((-LIM, -1), LIM, 2, facecolor="none", edgecolor="#d62728",
                               hatch="//", lw=0, alpha=.45, zorder=1))
        ax.text(-2.85, 1.15, "掩蔽域（地球から見えない）", fontsize=9, color="#d62728")
    if view == "xy":
        sun = np.array([np.cos(np.radians(12)), np.sin(np.radians(12)), 0])
        draw_direction(ax, view, sun, "太陽", exact=False, text="太陽（最大 約12°）", alpha=0.55)
    if view == "yz":
        ax.add_patch(Circle((0, 0), 1, facecolor="none", edgecolor="#d62728", hatch="//",
                            lw=1.5, alpha=.6, zorder=3))
        ax.text(0, -1.4, "地球から見た天球面", fontsize=9.5, ha="center", color="#333333")
        ax.text(0, -1.8, "円の内側かつ x<0 → 掩蔽", fontsize=9, ha="center", color="#d62728")


def draw_phi_orb(ax, view):
    draw_center(ax, "衛星", "衛星")
    draw_direction(ax, view, np.array([0., 1, 0]), "木星")
    if view == "xy":
        flow_arrows(ax, (-0.6, -1.5), (1.6, -1.5), "公転方向・共回転プラズマの流れ", label_at=(0.5, -1.9))
        ax.text(-2.85, 0.35, "後行半球\n（プラズマが\n当たる側）", fontsize=8.5, color="#9467bd")
    if view == "xz":
        ax.text(0.15, 1.15, "公転軌道面の法線\n（木星自転軸に近い）", fontsize=8.5, zorder=6)
        flow_arrows(ax, (-0.6, -1.5), (1.6, -1.5), "公転方向", label_at=(0.5, -1.85))


FIGURES = [
    ("IAU_JUPITER", "木星中心・木星固定（自転する）座標系", draw_iau_jupiter,
     [("原点", "木星の中心（observer=\"JUPITER\"）"),
      ("+Z", "木星の自転軸（IAU 北極）"),
      ("+X", "赤道上の経度 0°（本初子午線）の方向"),
      ("+Y", "Z × X（右手系）"),
      ("出典", "SPICE 組み込みフレーム／pck00011.tpc の IAU 自転モデル")],
     ["座標軸が木星と一緒に約 9.93 時間で自転する",
      "衛星や JUICE は見かけ上、時計回りに回って見える",
      "lon_deg は東経（−180〜180°）、lat_deg は惑星中心緯度",
      "木星中心で4衛星の位置関係を見るときに使う"]),
    ("IAU_<衛星>", "衛星中心・衛星固定（自転する）座標系", draw_iau_moon,
     [("原点", "衛星の中心（IO / EUROPA / GANYMEDE / CALLISTO）"),
      ("+Z", "衛星の自転軸（IAU 北極）"),
      ("+X", "赤道上の経度 0°（本初子午線）の方向"),
      ("+Y", "Z × X（右手系）"),
      ("例", "frame=\"IAU_GANYMEDE\"、observer=\"GANYMEDE\"")],
     ["衛星は同期自転のため、木星は常に +X 付近（実測で 3° 以内）",
      "公転方向（先行半球）はおよそ −Y、後行半球はおよそ +Y",
      "共回転プラズマは +Y 側から当たり −Y 向きに流れる",
      "経度・緯度は衛星表面の地理座標と一致する"]),
    ("JUPITER_FACING", "衛星中心・木星方向を基準にした座標系", draw_jupiter_facing,
     [("原点", "衛星の中心（4衛星のみ）"),
      ("+Z", "衛星の自転軸（IAU 北極）"),
      ("+X", "衛星→木星の方向を衛星の赤道面に投影した方向"),
      ("+Y", "Z × X（右手系）"),
      ("基準", "IAU_<衛星>（光行差補正なし）")],
     ["木星は常に x>0, y=0（z は一般に 0 ではない）",
      "実際の木星の z 方向のずれは 0.01° 未満（図では誇張）",
      "公転方向・共回転プラズマの流れはおよそ −Y",
      "IAU_<衛星> から、木星方向とのわずかなずれを取り除いたもの"]),
    ("SUN_FACING", "衛星中心・太陽方向を主軸にした座標系", draw_sun_facing,
     [("原点", "衛星の中心（4衛星のみ）"),
      ("+X", "衛星→太陽の方向そのもの（厳密に一致）"),
      ("+Z", "衛星の北極軸のうち +X に直交する成分"),
      ("+Y", "Z × X（右手系）"),
      ("基準", "IAU_<衛星>（光行差・光路時間の補正なし）")],
     ["x>0 が昼側、x<0 が夜側",
      "太陽天頂角 = arccos(x / r)",
      "yz 面の図は太陽から見た像（+Y が右、+Z が上）",
      "北極軸と +Z のずれは小さい（ガニメデで 3° 程度、図では誇張）"]),
    ("EARTH_FACING", "衛星中心・地球方向を主軸にした座標系", draw_earth_facing,
     [("原点", "衛星の中心（4衛星のみ）"),
      ("+X", "衛星→地球の視線方向そのもの（厳密に一致）"),
      ("+Z", "衛星の北極軸のうち +X に直交する成分"),
      ("+Y", "Z × X（右手系）"),
      ("基準", "IAU_<衛星>（光行差・光路時間の補正なし）")],
     ["yz 面の図は地球から見た天球面（+Y が右、+Z が上）",
      "x<0 かつ √(y²+z²) < 衛星半径 → 地球から見て衛星の裏（幾何学的な掩蔽）",
      "電波掩蔽観測の幾何を確かめるときに使う",
      "太陽方向は地球方向から最大約 12° 離れる"]),
    ("PHI_ORB", "衛星中心・木星方向を主軸にした Phi 座標系（JUICE 公式準拠）", draw_phi_orb,
     [("原点", "衛星の中心（4衛星のみ）"),
      ("+Y", "衛星→木星の方向そのもの（厳密に一致）"),
      ("+X", "木星に対する衛星の公転速度のうち +Y に直交する成分"),
      ("+Z", "X × Y（公転軌道面の法線）"),
      ("出典", "JUICE_<衛星>_PHI_ORB（juice_sci_v21.tf、SPhiZ）と同じ定義")],
     ["木星は常に x=0, z=0, y>0",
      "公転方向・共回転プラズマの流れは +X（上流は −X 側）",
      "+Z と木星自転軸のずれは 0.5° 以内（実測）",
      "公式フレームとの差は位置 1e-9 km 以下（Io は公式定義なし）"]),
]


if __name__ == "__main__":
    for spec in FIGURES:
        print(figure(*spec))
