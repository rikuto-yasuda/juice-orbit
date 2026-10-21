from pathlib import Path
from juice_orbit import prepare_juice, make_times, get_positions, save_csv, plot_orbits

# 全OSで利用できる絶対パス。任意の絶対パスに変更できます。
SPICE_DATA_DIR = Path.home() / "spice_data" / "JUICE"
RESULTS_SUBDIR = "results/example01"
SAVE_CSV = True
SAVE_PNG = True

workspace = prepare_juice(SPICE_DATA_DIR, results_subdir=RESULTS_SUBDIR)
times = make_times(
    "2035-06-01T00:00:00Z", "2035-06-01T06:00:00Z",
    step=2, unit="minutes",
)
data = get_positions(
    times, targets=["JUICE", "JUPITER"],
    observer="GANYMEDE", frame="JUPITER_FACING", output="full",
)
print(data.head())

if SAVE_CSV:
    print(save_csv(data, workspace.results_dir / "orbit.csv"))
if SAVE_PNG:
    # 近傍軌道が見やすいよう、図にはJUICEだけを表示します。
    print(plot_orbits(
        data[data["target"] == "JUICE"], workspace.results_dir / "orbit.png",
        plane="xy", time_markers=3,
        title="JUICE / Ganymede center / Jupiter-facing (+X)",
    ))
print("Results:", workspace.results_dir)