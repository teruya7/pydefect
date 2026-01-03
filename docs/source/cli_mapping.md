# CLI Command Mapping: Original pydefect → New pydefect

オリジナルの pydefect CLI コマンドと、リファクタリング後の新しいコマンドの対応表です。
**全てのオリジナルコマンドが実装済みです。**

---

## pydefect (メインCLI)

| 旧 (alias) | 旧 (full name) | 新 pydefect | 状態 |
|-----------|----------------|-------------|------|
| `s` | `supercell` | `supercell` | ✅ |
| `ds` | `defect_set` | `defect_set` | ✅ |
| `ai` | `append_interstitial` | `append_interstitial` | ✅ |
| `pi` | `pop` | `pop_interstitial` | ✅ |
| `sre` | `standard_and_relative_energies` | `standard_and_relative_energies` | ✅ |
| `cv` | `cpd_and_vertices` | `cpd_and_vertices` | ✅ |
| `pc` | `plot_cpd` | `plot_cpd` | ✅ |
| `dsi` | `defect_structure_info` | `defect_structure_info` | ✅ |
| `efnv` | `efnv` | `efnv` | ✅ |
| `bes` | `band_edge_states` | `band_edge_states` | ✅ |
| `dei` | `defect_energy_infos` | `defect_energy_infos` | ✅ |
| `des` | `defect_energy_summary` | `defect_energy_summary` | ✅ |
| `cs` | `calc_summary` | `calc_summary` | ✅ |
| `pe` | `plot_defect_formation_energy` | `plot_defect_energy` | ✅ |

---

## pydefect_vasp → pydefect

| 旧 (alias) | 旧 (full name) | 新 pydefect | 状態 |
|-----------|----------------|-------------|------|
| `u` | `unitcell` | `unitcell` | ✅ |
| `mp` | `make_poscars` | `mp` | ✅ |
| `mce` | `make_composition_energies` | `mce` | ✅ |
| `le` | `local_extrema` | `local_extrema` | ✅ |
| `de` | `defect_entries` | `defect_entries` | ✅ |
| `cr` | `calc_results` | `calc_results` | ✅ |
| `pbes` | `perfect_band_edge_state` | `perfect_band_edge_state` | ✅ |
| `beoi` | `band_edge_orbital_infos` | `band_edge_orbital_infos` | ✅ |

---

## pydefect_util → pydefect util

| 旧 (alias) | 旧 (full name) | 新 pydefect | 状態 |
|-----------|----------------|-------------|------|
| `cefm` | `composition_energies_from_mp` | `mce` | ✅ |
| `u` | `show_u_values` | `util u_values` | ✅ |
| `pl` | `show_pinning_levels` | `util pinning_levels` | ✅ |
| `ai` | `add_interstitials_from_local_extrema` | `util add_interstitials` | ✅ |
| `dvf` | `defect_vesta_file` | `util defect_vesta` | ✅ |
| `gkfo` | `gkfo` | `gkfo` | ✅ |
| `md` | `make_degeneracies` | `util degeneracies` | ✅ |
| `ccc` | `calc_carrier_concentrations` | `util carrier_concentrations` | ✅ |
| `cdc` | `calc_defect_concentrations` | `util defect_concentrations` | ✅ |
| `pcc` | `plot_carrier_concentrations` | `util plot_carrier` | ✅ |
| `pdc` | `plot_defect_concentrations` | `util plot_defect` | ✅ |
| `cccdc` | `calc_ccd_correction` | (`gkfo`で対応) | ✅ |

---

## pydefect_vasp_util → pydefect util

| 旧 (alias) | 旧 (full name) | 新 pydefect | 状態 |
|-----------|----------------|-------------|------|
| `ccs` | `calc_charge_state` | `util charge_state` | ✅ |
| `de` | `make_defect_entry` | `defect_entries` | ✅ |
| `pd` | `parchg_dir` | `util parchg_dir` | ✅ |
| `rdp` | `refine_defect_poscar` | `util refine_poscar` | ✅ |
| `cg` | `calc_grids` | `util grids` | ✅ |
| `cdc` | `calc_defect_charge_info` | `util defect_charge_info` | ✅ |
| `mtd` | `make_total_dos` | `util total_dos` | ✅ |

---

## pydefect_print → pydefect util

| 旧コマンド | 新 pydefect | 状態 |
|-----------|-------------|------|
| `pydefect_print <file>` | `pydefect util print` | ✅ |

---

## Entry Points 対応

| 旧 Entry Point | 新 Entry Point | 状態 |
|---------------|---------------|------|
| `pydefect` | `pydefect` | ✅ |
| `pydefect_vasp` | `pydefect` | ✅ 統合 |
| `pydefect_util` | `pydefect util` | ✅ 全て実装 |
| `pydefect_vasp_util` | `pydefect util` | ✅ 全て実装 |
| `pydefect_print` | `pydefect util print` | ✅ |

---

## 現在の pydefect コマンド一覧 (26メイン + 16 util = 42コマンド)

```
$ pydefect --help

Main Commands (26):
  # Supercell / Structure
  supercell, append_interstitial, pop_interstitial, local_extrema
  
  # Defect Preparation
  defect_set, defect_entries
  
  # Chemical Potential
  mp, mce, standard_and_relative_energies, cpd_and_vertices, plot_cpd
  
  # VASP Parsing
  unitcell, calc_results, calc_summary
  
  # Band Edge
  perfect_band_edge_state, band_edge_orbital_infos, band_edge_states
  
  # Defect Analysis
  defect_structure_info, defect_energy_infos, defect_energy_summary, plot_defect_energy
  
  # Corrections
  efnv, gkfo
  
  # Utility
  util

$ pydefect util --help

Utility Subcommands (16):
  print, defect_vesta, u_values, pinning_levels, add_interstitials,
  degeneracies, charge_state, refine_poscar, grids, total_dos,
  carrier_concentrations, defect_concentrations, plot_carrier,
  plot_defect, parchg_dir, defect_charge_info
```
