# CLI Command Mapping: Original → New

オリジナルの pydefect CLI コマンドと、リファクタリング後の新しいコマンドの対応表です。

## pydefect_vasp → pydefect

| オリジナル | 新 pydefect | 説明 |
|-----------|-------------|------|
| `pydefect_vasp u` | `pydefect make_unitcell_from_vasp` | unitcell.yaml 作成 |
| `pydefect_vasp mp` | `pydefect_vasp mp` | MP競合相取得 (維持) |
| `pydefect_vasp mce` | `pydefect_vasp mce` | MP組成エネルギー (維持) |
| `pydefect_vasp le` | `pydefect make_local_extrema` | 格子間サイト探索 |
| `pydefect_vasp de` | `pydefect defect_entries` | 欠陥エントリ作成 |
| `pydefect_vasp cr` | `pydefect make_calc_results_from_vasp` | calc_results 作成 |
| `pydefect_vasp pbes` | `pydefect make_perfect_band_edge_state` | バンド端状態 |
| `pydefect_vasp beoi` | `pydefect make_band_edge_orbital_infos` | 軌道情報 |
| `pydefect_vasp efnv` | `pydefect make_efnv_correction` | eFNV補正 |

## pydefect (維持)

| オリジナル | 新 pydefect | 説明 |
|-----------|-------------|------|
| `pydefect s` | `pydefect make_supercell` | スーパーセル作成 |
| `pydefect ds` | `pydefect defect_set` | 欠陥セット作成 |
| `pydefect ai` | `pydefect append_interstitial` | 格子間追加 |
| `pydefect pi` | `pydefect pop_interstitial` | 格子間削除 |
| `pydefect sre` | `pydefect standard_and_relative_energies` | 標準/相対エネルギー |
| `pydefect cv` | `pydefect cpd_and_vertices` | 化学ポテンシャル図 |
| `pydefect pc` | `pydefect plot_cpd` | CPDプロット |
| `pydefect dsi` | `pydefect defect_structure_info` | 欠陥構造解析 |
| `pydefect dei` | `pydefect defect_energy_infos` | 欠陥エネルギー計算 |
| `pydefect des` | `pydefect defect_energy_summary` | エネルギーサマリー |
| `pydefect bes` | `pydefect make_band_edge_states` | バンド端状態 |

## Entry Points

| オリジナル | 新 | 状態 |
|-----------|-----|------|
| `pydefect` | `pydefect` | ✅ 維持 |
| `pydefect_vasp` | `pydefect_vasp` | ✅ 維持 (mp, mce) |
| `pydefect_util` | なし | 統合予定 |
| `pydefect_vasp_util` | なし | 統合予定 |
| `pydefect_print` | `pydefect util print_json` | util サブコマンド |
