# JUICE orbit tools

Query and plot the ESA JUICE CReMA 5.2 planning trajectory with Python.
From the source folder, run `python -m pip install -e .` in a virtual environment.
Dependencies are installed automatically. Use that environment for scripts and
notebooks. Examples below use portable absolute paths based on `Path.home()`.

The guide covers macOS, Linux and Windows. This project has been tested on
macOS / Apple Silicon / Python 3.9; other platforms have not yet been tested.
Compatibility depends on dependency support for your OS, CPU and Python version.
This is a planning scenario, not a reconstructed operational orbit.

---

# 日本語ガイド

JUICE、木星、4つのガリレオ衛星の位置・速度を計算し、CSVとPNGを出力する
Pythonパッケージです。以下の手順で自分のパソコンに導入できます。

## 1. 必要なもの

- Python 3.9以上（パッケージの指定条件）。依存ライブラリの対応状況はOS・CPU・Python版によって異なります。
- 初回インストールとカーネル取得のためのインターネット接続。
- 書き込み可能な保存先。位置計算用カーネルは合計約220 MB、別途Python環境と出力の容量が必要です。

macOS・Linux・Windows向けの手順を掲載しています。実機で確認した環境は
macOS / Apple Silicon / Python 3.9です。すべての環境での動作保証ではありません。

Pythonがない場合は [Python公式サイト](https://www.python.org/downloads/) から
自分のOS用のPythonを導入してください。LinuxではOSのパッケージ管理機能も使えます。

### 必要なライブラリ

| ライブラリ | 用途 | 指定範囲 |
|---|---|---|
| SpiceyPy | SPICEによる位置・速度計算 | `>=6,<8` |
| NumPy | 配列・ベクトル計算 | `>=1.24,<3` |
| pandas | 表形式データ・CSV出力 | `>=2,<3` |
| Matplotlib | 軌道のPNG出力 | `>=3.7,<4` |

下記の `pip install -e .` で、これらも自動インストールされます。
依存関係は `pyproject.toml` に記載されています。ビルド用setuptoolsもpipが
必要に応じて取得します。対応するSpiceyPyバイナリ配布にはCSPICEが含まれるため、
通常はSPICE Toolkitの別途インストールは不要です。バイナリ配布のない環境では
ビルド設定が必要になる場合があります。

依存ライブラリだけを導入する場合は、プロジェクト直下で以下を実行します。
このコマンドだけでは `juice_orbit` 自体はインストールされません。

```sh
python -m pip install -r requirements.txt
```

## 2. プロジェクトを用意する

配布されたZIPを展開するか、フォルダをコピーします。GitリポジトリのURLを
受け取っている場合はcloneでも構いません。次の構成を保ってください。

```text
orbit_plot/
├── pyproject.toml
├── README.md
├── requirements.txt
├── src/
│   └── juice_orbit/
│       ├── __init__.py
│       └── core.py
└── tests/
```

別PCの `.venv` はコピーせず、移動先で作り直します。
以下の `path/to` は自分の保存先に置き換えてください。

## 3. インストールする

### macOS・Linux

ターミナルで `pyproject.toml` のあるフォルダに移動して実行します。

```sh
cd "/path/to/orbit_plot"
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Linuxで `venv` がない場合はOSの仮想環境用パッケージが必要です。
例えばUbuntu/Debianでは、管理権限がある場合に
`sudo apt install python3-venv` で導入できます。

### Windows（PowerShell）

```powershell
cd "C:\path\to\orbit_plot"
py --version
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .
```

この方法は仮想環境の有効化を必要としません。以降の `python` コマンドは
`.\.venv\Scripts\python.exe` に読み替えて実行できます。
PowerShellで実行が許可されていれば `.\.venv\Scripts\Activate.ps1` で
有効化しても構いません。`py` がなければ `python --version` を確認して、
`py` を `python` に置き換えます。

### 導入確認

```sh
python -c "import juice_orbit; print(juice_orbit.__version__)"
```

`0.1.0` と表示されれば成功です。`-e` は編集可能インストールです。
コード修正後は実行中のPythonやNotebookカーネルを再起動してください。
元のプロジェクトフォルダは残しておく必要があります。
コードを編集しない利用者は `python -m pip install .` でも導入できます。

## 4. 最初の計算・CSV・PNG出力

次を `run_juice.py` として保存します。保存先はプロジェクト内でも別フォルダでも
構いません。インストールした環境のPythonで実行してください。

```python
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
```

```sh
python run_juice.py
```

初回はESAから不足カーネルを取得するため時間がかかります。
結果はホームディレクトリの `spice_data/JUICE/results/example01/` に保存されます。
`SAVE_CSV` や `SAVE_PNG` を `False` にすると、それぞれ保存しません。
結果はpandasのDataFrameとしてメモリ上に残るので、そのまま解析できます。

## 5. 日時・対象・座標系・出力形式

上の例で `prepare_juice()` を実行した後、次のように変更できます。

### 指定日時1点・木星中心

```python
data = get_positions(
    "2032-01-01T00:00:00Z",
    targets=["JUICE", "IO", "EUROPA", "GANYMEDE", "CALLISTO"],
    observer="JUPITER", frame="IAU_JUPITER", output="full",
)
```

| 原点 `observer` | 固定座標系 `frame` |
|---|---|
| `JUPITER` | `IAU_JUPITER` |
| `IO` | `IAU_IO` |
| `EUROPA` | `IAU_EUROPA` |
| `GANYMEDE` | `IAU_GANYMEDE` |
| `CALLISTO` | `IAU_CALLISTO` |

`observer` は原点、`frame` は軸の向きです。
期間指定には `make_times(start, end, step, unit)` を使います。
`unit` は `seconds` / `minutes` / `hours` / `days`。
終了日時は刻みに一致するときだけ含まれます。タイムゾーンがない日時はUTC扱いです。
時刻生成はPythonのdatetimeを使うため、うるう秒の `23:59:60` は入力できません。

### 木星方向を向く衛星中心座標系

`frame="JUPITER_FACING"` は4衛星を `observer` に指定して使います。
各時刻で、以下の単位ベクトルから右手系を構成します。

- z軸：IAU衛星系の北極軸。
- y軸：z軸 × 衛星から木星への方向を正規化。
- x軸：y軸 × z軸。木星方向の衛星赤道面への投影。

木星のx座標は正、y座標はゼロです。z座標は一般にはゼロではありません。
本パッケージ専用の名前で、SPICE本体に登録されるフレームではありません。
現在は `aberration="NONE"` のみ対応しています。

### その他の衛星中心座標系

以下も4衛星を `observer` に指定して使います。条件（`aberration="NONE"`、
幾何学的ベクトル、速度に回転の効果を含む）は `JUPITER_FACING` と同じです。

| `frame` | 定義 |
|---|---|
| `SUN_FACING` | +X：衛星→太陽方向そのもの。+Z：衛星のIAU北極軸のうち+Xに直交する成分。+Y：Z×X。 |
| `EARTH_FACING` | +X：衛星→地球の視線方向そのもの。+Z・+Yは `SUN_FACING` と同様。yz面が地球から見た天球面になります。 |
| `PHI_ORB` | +Y：衛星→木星方向そのもの。+X：木星に対する衛星の公転速度（J2000慣性系）のうち+Yに直交する成分。+Z：X×Y（公転軌道面の法線）。 |

`PHI_ORB` はJUICE公式のフレームカーネル `juice_sci_v21.tf` にある
`JUICE_<衛星>_PHI_ORB`（JUICE MAGチームのSPhiZ）と同じ定義です。
Europa・Ganymede・Callistoでは公式フレームと数値が一致することを
`tests/verify_real_kernels.py` で確認しています。公式にはIo用の定義がありませんが、
本パッケージではIoにも同じ定義を適用します。
地球方向・太陽方向には光の伝搬時間による補正を入れていません。

### 戻り値とプロット

すべての形式に日時・対象・原点・座標系の列が付いています。

| `output` | 数値列 |
|---|---|
| `xyz` | `x_km`, `y_km`, `z_km` |
| `r_lat_lon` | `r_km`, `lat_deg`, `lon_deg` |
| `full` | 上記すべてと `vx_km_s`, `vy_km_s`, `vz_km_s`, `speed_km_s` |

距離はkm、速度はkm/s、角度は度です。rは中心からの距離で、高度ではありません。
緯度は惑星中心緯度、経度は東向き正（−180〜180度）です。
速度は指定座標系での位置の時間変化で、回転座標系では自転の効果を含みます。
デフォルトの光行差補正は `NONE` です。

NumPy配列が必要なら `data[["x_km", "y_km", "z_km"]].to_numpy()` とします。
PNG出力には `full` または `xyz` の結果が必要です。
`plane="xy"` / `"xz"` / `"yz"` で表示面を選びます。現在は2次元投影です。

## 6. Notebook・VS Code（任意）

Notebookは必須ではありません。利用する場合だけ同じ仮想環境に追加します。

```sh
python -m pip install jupyterlab ipykernel
python -m ipykernel install --user --name juice-orbit --display-name "Python (JUICE orbit)"
python -m jupyterlab
```

Notebookでは **Python (JUICE orbit)** カーネルを選んでください。
VS Codeでも、このプロジェクトの `.venv` をPythonインタープリターに選びます。

## 7. 再利用・別PCへの移動・オフライン利用

新しいターミナルでは、macOS/Linuxならインストール先の `.venv/bin/activate` を
`source` するか、`.venv/bin/python` を直接使います。
Windowsではインストール先の `.venv\Scripts\python.exe` を直接使えます。
同じPython環境なら、どの作業ディレクトリからもimportできます。

別PCへはプロジェクトをコピーして、手順3から環境を作り直します。
カーネルもコピーする場合は `JUICE/kernels/` の構造を保ってください。
ローカルメタカーネルを含め、必要なファイルが揃っていれば以下で利用できます。

```python
workspace = prepare_juice(SPICE_DATA_DIR, auto_download=False)
```

この指定はカーネル取得の通信を禁止します。Pythonと依存ライブラリの導入は別途
必要です。完全オフラインPCへの導入には、移動先のOS・CPU・Python版に合う
依存パッケージとビルド用パッケージを事前に用意してください。

既存カーネルと元メタカーネルは再利用し、自動で最新版へ置換しません。
現在の自動取得はCReMA 5.2用の指定ファイル群に限定しています。

## 8. 動作確認・トラブル対処

プロジェクト直下で実行します。単体テスト用の追加ライブラリは不要です。

```sh
python -m unittest discover -s tests -v
python tests/verify_real_kernels.py
```

2つ目は実カーネルを使用し、必要なら取得します。検証専用の保存先はプロジェクト内の
`data/JUICE/`、出力先は `data/JUICE/output/verification/` です。
上の利用例のホーム配下とは異なります。木星・4衛星の固定系と独自座標系の
整合性を検証します。別データとの比較による軌道精度の保証ではありません。

| 症状 | 確認・対処 |
|---|---|
| `No module named juice_orbit` | `python -c "import sys; print(sys.executable)"` で環境を確認。同じPythonでプロジェクト直下から `python -m pip install -e .` を実行。 |
| Notebookだけimportに失敗 | 手順6のカーネルを選び直す。 |
| 依存パッケージが見つからない・ビルド失敗 | pipを更新し、OS・CPU・Python版に対応する配布があるか確認。 |
| ESAへの接続エラー | 接続・プロキシ・証明書設定を確認して再実行。取得済みファイルは再利用します。 |
| `Kernel not found` | 配置先を確認し、`prepare_juice(..., auto_download=True)` で不足ファイルを取得。 |
| `SPKINSUFFDATA` | 日時・対象がカーネルの収録範囲内か確認。 |
| 画面のないサーバーで描画に失敗 | `juice_orbit` のimport前に `import matplotlib; matplotlib.use("Agg")` を追加。 |

確認したJUICE軌道SPKの収録期間はUTCで2023-04-14 12:42:14.222〜
2035-10-14 14:28:04.166です。計算できる範囲は必要なカーネルの共通範囲によります。
ESAの計画シナリオであり、確定した実運用軌道ではありません。

## 出典

- [ESA JUICE CReMA 5.2メタカーネル](https://spiftp.esac.esa.int/data/SPICE/JUICE/kernels/mk/juice_crema_5_2.tm)
- [ESA SPICEデータ案内](https://www.cosmos.esa.int/web/spice/data)
