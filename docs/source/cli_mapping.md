# CLI Command Mapping: Original pydefect → New pydefect

オリジナルの pydefect CLI コマンドと、リファクタリング後の新しいコマンドの対応表です。

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
| `cefm` | `composition_energies_from_mp` | `mce` | ✅ 統合 |
| `u` | `show_u_values` | `util u_values` | ✅ |
| `pl` | `show_pinning_levels` | `util pinning_levels` | ✅ |
| `ai` | `add_interstitials_from_local_extrema` | `util add_interstitials` | ✅ |
| `dvf` | `defect_vesta_file` | `util defect_vesta` | ✅ |
| `gkfo` | `gkfo` | `gkfo` | ✅ |
| `md` | `make_degeneracies` | `util degeneracies` | ✅ |
| `ccc` | `calc_carrier_concentrations` | (未実装) | ❌ |
| `cdc` | `calc_defect_concentrations` | (未実装) | ❌ |
| `pcc` | `plot_carrier_concentrations` | (未実装) | ❌ |
| `pdc` | `plot_defect_concentrations` | (未実装) | ❌ |
| `cccdc` | `calc_ccd_correction` | (未実装) | ❌ |

---

## pydefect_vasp_util → pydefect util

| 旧 (alias) | 旧 (full name) | 新 pydefect | 状態 |
|-----------|----------------|-------------|------|
| `ccs` | `calc_charge_state` | `util charge_state` | ✅ |
| `de` | `make_defect_entry` | `defect_entries` | ✅ 統合 |
| `pd` | `parchg_dir` | (未実装) | ❌ |
| `rdp` | `refine_defect_poscar` | `util refine_poscar` | ✅ |
| `cg` | `calc_grids` | `util grids` | ✅ |
| `cdc` | `calc_defect_charge_info` | (未実装) | ❌ |
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
| `pydefect_util` | `pydefect util` | ✅ 大部分実装 |
| `pydefect_vasp_util` | `pydefect util` | ✅ 大部分実装 |
| `pydefect_print` | `pydefect util print` | ✅ |

---

## 現在の pydefect コマンド一覧 (26コマンド + 10 utilサブコマンド)

```
$ pydefect --help

Main Commands (26):
  # Supercell / Structure
  supercell                        Make supercell
  append_interstitial              Add interstitial site
  pop_interstitial                 Remove interstitial site
  local_extrema                    Find interstitial sites from volumetric data
  
  # Defect Preparation
  defect_set                       Create defect_in.yaml
  defect_entries                   Create defect directories
  
  # Chemical Potential
  mp                               Get MP competing phases
  mce                              Make composition energies from MP
  standard_and_relative_energies   Calculate energies
  cpd_and_vertices                 Make chem pot diagram
  plot_cpd                         Plot diagram
  
  # VASP Parsing
  unitcell                         Create unitcell.yaml
  calc_results                     Parse VASP outputs
  calc_summary                     Create calc summary
  
  # Band Edge
  perfect_band_edge_state          Perfect band edge
  band_edge_orbital_infos          Orbital infos
  band_edge_states                 Defect band edge
  
  # Defect Analysis
  defect_structure_info            Structure analysis
  defect_energy_infos              Energy calculation
  defect_energy_summary            Energy summary
  plot_defect_energy               Plot energies
  
  # Corrections
  efnv                             EFNV correction
  gkfo                             GKFO correction
  
  # Utility
  util                             Utility subcommands

$ pydefect util --help

Utility Subcommands (10):
  print               Print JSON/YAML files
  defect_vesta        Create VESTA files
  u_values            Show U values
  pinning_levels      Show pinning levels
  add_interstitials   Add interstitials from local extrema
  degeneracies        Make degeneracies
  charge_state        Calculate charge state
  refine_poscar       Refine defect POSCAR
  grids               Calculate grids
  total_dos           Make total DOS
```

---

## 未実装コマンド (5つ)

濃度計算関連のコマンドは複雑な依存関係があり、将来の実装予定：

- `calc_carrier_concentrations` (ccc)
- `calc_defect_concentrations` (cdc) 
- `plot_carrier_concentrations` (pcc)
- `plot_defect_concentrations` (pdc)
- `calc_ccd_correction` (cccdc)
- `parchg_dir` (pd)
- `calc_defect_charge_info`
