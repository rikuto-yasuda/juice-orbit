from pathlib import Path
import pandas as pd


# ============================================================
# 設定
# ============================================================

OCC_FILE = Path(
    "/work1/rikutoyasuda/tools/python_JUICE/orbit_check/occ.xls"
)

GAP_THRESHOLD = pd.Timedelta(minutes=30)


# ============================================================
# 1. Excel読み込み
# ============================================================

df = pd.read_excel(
    OCC_FILE,
    sheet_name=0,
    engine="xlrd",
)

print("Columns:")
print(df.columns.tolist())

print()
print("Event types:")
print(df["ev_type"].unique())


# ============================================================
# 2. occultation eventだけ取り出す
# ============================================================

occ = df[
    df["ev_type"].isin(["src_occ_start", "src_occ_end"])
].copy()

occ["ev_utc"] = pd.to_datetime(
    occ["ev_utc"],
    format="%d-%b-%YT%H:%M:%S"
)

# 同一イベントの完全な重複があれば削除
occ = occ.drop_duplicates(
    subset=[
        "moon",
        "frequency_MHz",
        "source_type",
        "ev_type",
        "ev_utc",
    ]
)

# 時刻順
occ = occ.sort_values(
    ["moon", "frequency_MHz", "source_type", "ev_utc"]
).reset_index(drop=True)


# ============================================================
# 3. frequency + source_type + moon ごとに
#    src_occ_start と src_occ_end をペアにする
# ============================================================

group_keys = [
    "moon",
    "frequency_MHz",
    "source_type",
]

occultations = []

for keys, group in occ.groupby(group_keys, sort=False):

    # startを時間順に処理するためのリスト
    pending_starts = []

    group = group.sort_values(
        ["ev_utc", "ev_type"],
        key=lambda x: (
            x.map({
                "src_occ_start": 0,
                "src_occ_end": 1
            })
            if x.name == "ev_type"
            else x
        )
    )

    for _, row in group.iterrows():

        if row["ev_type"] == "src_occ_start":

            pending_starts.append(row["ev_utc"])

        elif row["ev_type"] == "src_occ_end":

            if len(pending_starts) == 0:
                print(
                    "WARNING: startがないend:",
                    keys,
                    row["ev_utc"]
                )
                continue

            # start/start/end/end の場合も
            # 古いstartから順番に対応させる
            start = pending_starts.pop(0)

            occultations.append({
                "moon": row["moon"],
                "frequency_MHz": row["frequency_MHz"],
                "source_type": row["source_type"],
                "occ_start": start,
                "occ_end": row["ev_utc"],
            })

    # 対応するendがなかったstart
    if pending_starts:
        print(
            "WARNING: endがないstart:",
            keys,
            pending_starts
        )


# DataFrame化
occ = pd.DataFrame(occultations)


# ============================================================
# 4. 個々の掩蔽イベントを確認
# ============================================================

occ = occ.sort_values(
    ["moon", "occ_start"]
).reset_index(drop=True)

print()
print("=" * 100)
print("Individual occultation events")
print("=" * 100)

print(
    occ[
        [
            "moon",
            "frequency_MHz",
            "source_type",
            "occ_start",
            "occ_end",
        ]
    ].to_string(index=False)
)

# ============================================================
# 5. moonごとに、30分以内の掩蔽を同じFlybyにまとめる
# ============================================================

occ["flyby"] = 0

for moon, indices in occ.groupby("moon").groups.items():

    flyby_number = 1
    current_flyby_end = None

    for index in indices:

        start = occ.loc[index, "occ_start"]
        end = occ.loc[index, "occ_end"]

        if current_flyby_end is None:

            occ.loc[index, "flyby"] = flyby_number
            current_flyby_end = end
            continue

        gap = start - current_flyby_end

        if gap > GAP_THRESHOLD:
            flyby_number += 1

        occ.loc[index, "flyby"] = flyby_number

        current_flyby_end = max(
            current_flyby_end,
            end
        )


# ============================================================
# 6. Flybyごとの結果だけ表示
# ============================================================

print()
print("=" * 100)
print("Flyby summary")
print("=" * 100)

for (moon, flyby), group in occ.groupby(
    ["moon", "flyby"],
    sort=True
):

    flyby_start = group["occ_start"].min()
    flyby_end = group["occ_end"].max()

    print(
        f"{moon:10s} "
        f"Flyby {flyby:02d}: "
        f"{flyby_start} - {flyby_end}"
    )