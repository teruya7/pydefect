# CLI コマンドリファレンス

pydefect は5つのコマンドラインエントリーポイントを提供します。

---

## エントリーポイント一覧

| コマンド | 説明 |
|---------|------|
| `pydefect` | メインコマンド（DFTコード非依存） |
| `pydefect_vasp` | VASP専用コマンド |
| `pydefect_util` | ユーティリティコマンド |
| `pydefect_vasp_util` | VASP専用ユーティリティ |
| `pydefect_print` | JSONファイルの表示 |

---

## pydefect コマンド

DFTコードに依存しない汎用コマンド。

| コマンド | 説明 |
|---------|------|
| `s` | スーパーセル作成 |
| `ds` | 欠陥セット作成 |
| `ai` | 侵入サイト追加 |
| `pi` | 侵入サイト削除 |
| `sre` | 標準/相対エネルギー計算 |
| `cv` | 化学ポテンシャル図作成 |
| `pc` | 化学ポテンシャル図プロット |
| `dsi` | 欠陥構造情報作成 |
| `dei` | 欠陥エネルギー情報作成 |
| `des` | 欠陥エネルギーサマリー作成 |
| `cs` | 計算サマリー作成 |
| `pe` | 欠陥形成エネルギープロット |
| `efnv` | EFNV補正計算 |
| `bes` | バンドエッジ状態作成 |

---

## pydefect_vasp コマンド

VASP専用のコマンド。

| コマンド | 説明 |
|---------|------|
| `u` | unitcell.yaml 作成 |
| `cr` | calc_results.json 作成 |
| `mce` | 組成エネルギー作成 |
| `mp` | MP競合相取得 |
| `le` | 局所極値検出 |
| `de` | 欠陥エントリ作成 |
| `pbes` | パーフェクトバンドエッジ状態 |
| `beoi` | バンドエッジ軌道情報 |

---

## pydefect_util コマンド

ユーティリティコマンド。

| コマンド | 説明 |
|---------|------|
| `print` | JSONファイル表示 |
| `dvf` | VESTA用ファイル作成 |
| `u` | U値表示 |
| `pl` | ピニングレベル表示 |
| `ai` | 局所極値から侵入サイト追加 |
| `gkfo` | GKFO補正計算 |
| `ccc` | キャリア濃度計算 |
| `cdc` | 欠陥濃度計算 |
| `pcc` | キャリア濃度プロット |
| `pdc` | 欠陥濃度プロット |
| `cccdc` | キャリア・欠陥濃度両方計算 |
| `md` | 縮退度計算 |

---

## pydefect_vasp_util コマンド

VASP専用ユーティリティ。

| コマンド | 説明 |
|---------|------|
| `de` | 欠陥エントリ作成 |
| `rdp` | POSCAR精緻化 |
| `pd` | PARCHGディレクトリ作成 |
| `cg` | グリッド計算 |
| `mtd` | 全状態密度作成 |
| `ccs` | 電荷状態計算 |
| `cdc` | 欠陥電荷情報 |

---

## pydefect_print

JSONファイルを読みやすい形式で表示。

```bash
pydefect_print supercell_info.json
pydefect_print calc_results.json
pydefect_print defect_entry.json
```

---

## 使用例

```bash
# スーパーセル作成
pydefect s -p CONTCAR

# 欠陥セット作成
pydefect ds -o Mg 2 Al 3 O -2

# VASP欠陥エントリ作成
pydefect_vasp de -s supercell_info.json -d defect_in.yaml

# 計算結果パース
pydefect_vasp cr -d Va_O1_0 Va_O1_1

# EFNV補正
pydefect efnv -d Va_O1_0 -pcr perfect/calc_results.json -u unitcell.yaml

# 欠陥形成エネルギープロット
pydefect pe -d defect_energy_summary.json -l A

# JSONファイル表示
pydefect_print calc_results.json
```
