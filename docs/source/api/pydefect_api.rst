Python API Reference
====================

pydefect は CLI と Python API の両方でアクセスできます。
Python API を使用すると、より柔軟なワークフローを構築できます。

API のインポート
----------------

.. code-block:: python

    from pydefect import api

    # または、個別に関数をインポート
    from pydefect.api import make_supercell, make_defect_set

使用可能な関数
--------------

すべての API 関数は ``pydefect.api`` から利用可能です：

.. code-block:: python

    from pydefect import api

    # 利用可能な関数の一覧
    print(api.__all__)

スーパーセル
^^^^^^^^^^^^

``make_supercell``
""""""""""""""""""

スーパーセルを作成します。

.. code-block:: python

    from pydefect import api
    from pymatgen.core import IStructure

    # 構造を読み込み
    unitcell = IStructure.from_file("CONTCAR")

    # スーパーセルを作成（自動で最適なサイズを選択）
    supercell_info, supercell = api.make_supercell(
        unitcell=unitcell,
        min_num_atoms=64,
        max_num_atoms=128,
    )

    # または、明示的に変換行列を指定
    supercell_info, supercell = api.make_supercell(
        unitcell=unitcell,
        matrix=[[2, 0, 0], [0, 2, 0], [0, 0, 2]],
    )

    # 結果を保存
    supercell_info.to_json_file("supercell_info.json")
    supercell.to("SPOSCAR")

**パラメータ:**

- ``unitcell``: ユニットセル構造 (IStructure/Structure)
- ``min_num_atoms``: 最小原子数 (デフォルト: 50)
- ``max_num_atoms``: 最大原子数 (デフォルト: 300)
- ``matrix``: 明示的な変換行列 (指定時は min/max_num_atoms は無視)
- ``analyze_symmetry``: 対称性解析を行うか (デフォルト: True)

**戻り値:**

- ``supercell_info``: SupercellInfo オブジェクト
- ``supercell``: スーパーセル構造

化学ポテンシャル
^^^^^^^^^^^^^^^^

``make_standard_and_relative_energies``
"""""""""""""""""""""""""""""""""""""""

標準エネルギーと相対エネルギーを計算します。

.. code-block:: python

    from pydefect import api
    from pydefect.analysis.chemical_potential.models import CompositionEnergies

    # 組成エネルギーを読み込み
    comp_energies = CompositionEnergies.from_yaml("composition_energies.yaml")

    # 標準・相対エネルギーを計算
    std_energies, rel_energies = api.make_standard_and_relative_energies(
        comp_energies
    )

    # 結果を保存
    std_energies.to_yaml_file("standard_energies.yaml")
    rel_energies.to_yaml_file("relative_energies.yaml")

``make_chem_pot_diag``
""""""""""""""""""""""

化学ポテンシャル図を作成します。

.. code-block:: python

    from pydefect import api
    from pydefect.analysis.chemical_potential.models import RelativeEnergies

    # 相対エネルギーを読み込み
    rel_energies = RelativeEnergies.from_yaml("relative_energies.yaml")

    # CPD を作成
    cpd = api.make_chem_pot_diag(
        rel_energies=rel_energies,
        target="MgAl2O4",
    )

    # 頂点（化学ポテンシャル条件）を確認
    for label, vertex in cpd.target_vertices.items():
        print(f"{label}: {vertex}")

    # 結果を保存
    cpd.to_json_file("chem_pot_diag.json")

欠陥準備
^^^^^^^^

``make_defect_set``
"""""""""""""""""""

欠陥セット（どの欠陥を計算するか）を生成します。

.. code-block:: python

    from pydefect import api
    from monty.serialization import loadfn

    # supercell_info を読み込み
    supercell_info = loadfn("supercell_info.json")

    # 欠陥セットを生成
    defect_set = api.make_defect_set(
        supercell_info=supercell_info,
        oxi_states={"Mg": 2, "Al": 3, "O": -2},
        dopants=["Sc", "Ti"],  # オプション
    )

    # 生成される欠陥を確認
    for name in defect_set.names:
        print(name)  # Va_O1_0, Va_O1_1, Va_O1_2, ...

    # 結果を保存
    defect_set.to_yaml("defect_in.yaml")

``make_defect_entries``
"""""""""""""""""""""""

欠陥エントリ（計算用ディレクトリ）を作成します。

.. code-block:: python

    from pydefect import api
    from monty.serialization import loadfn

    supercell_info = loadfn("supercell_info.json")
    defect_set = loadfn("defect_in.yaml")

    # 各欠陥のディレクトリを作成
    api.make_defect_entries(
        supercell_info=supercell_info,
        defect_set=defect_set,
    )

侵入原子
^^^^^^^^

``append_interstitial``
"""""""""""""""""""""""

supercell_info に侵入サイトを追加します。

.. code-block:: python

    from pydefect import api
    from pymatgen.core import Structure
    from monty.serialization import loadfn

    supercell_info = loadfn("supercell_info.json")
    base_structure = Structure.from_file("SPOSCAR")

    # 侵入サイトを追加
    updated_info = api.append_interstitial(
        supercell_info=supercell_info,
        base_structure=base_structure,
        frac_coords=[0.25, 0.25, 0.25],
        info="octahedral_site",
    )

    # 結果を保存
    updated_info.to_json_file("supercell_info.json")

``pop_interstitial``
""""""""""""""""""""

supercell_info から侵入サイトを削除します。

.. code-block:: python

    from pydefect import api
    from monty.serialization import loadfn

    supercell_info = loadfn("supercell_info.json")

    # インデックスで削除
    updated_info = api.pop_interstitial(
        supercell_info=supercell_info,
        index=1,
    )

    # または、すべて削除
    updated_info = api.pop_interstitial(
        supercell_info=supercell_info,
        pop_all=True,
    )

欠陥解析
^^^^^^^^

``make_defect_structure_info``
""""""""""""""""""""""""""""""

欠陥構造を解析し、変位情報を取得します。

.. code-block:: python

    from pydefect import api
    from pymatgen.core import Structure

    perfect = Structure.from_file("perfect/CONTCAR")
    initial = Structure.from_file("Va_O1_0/POSCAR")
    final = Structure.from_file("Va_O1_0/CONTCAR")

    # 欠陥構造情報を作成
    dsi = api.make_defect_structure_info(
        perfect_structure=perfect,
        initial_defect_structure=initial,
        final_defect_structure=final,
    )

    # 結果を確認
    print(f"サイト差分: {dsi.site_diff}")
    print(f"変位: {len(dsi.displacements)} 原子")
    print(f"対称性: {dsi.initial_site_sym} -> {dsi.final_site_sym}")

``make_defect_energy_info``
"""""""""""""""""""""""""""

欠陥のエネルギー情報を計算します。

.. code-block:: python

    from pydefect import api
    from monty.serialization import loadfn

    defect_entry = loadfn("Va_O1_0/defect_entry.json")
    calc_results = loadfn("Va_O1_0/calc_results.json")
    correction = loadfn("Va_O1_0/efnv_correction.json")
    perfect_cr = loadfn("perfect/calc_results.json")
    unitcell = loadfn("unitcell.yaml")
    std_energies = loadfn("standard_energies.yaml")

    # エネルギー情報を計算
    energy_info = api.make_defect_energy_info(
        defect_entry=defect_entry,
        calc_results=calc_results,
        correction=correction,
        perfect_calc_results=perfect_cr,
        unitcell=unitcell,
        standard_energies=std_energies,
    )

    print(f"形成エネルギー: {energy_info.formation_energy} eV")

``plot_defect_energy``
""""""""""""""""""""""

欠陥形成エネルギー図をプロットします。

.. code-block:: python

    from pydefect import api
    from monty.serialization import loadfn

    summary = loadfn("defect_energy_summary.json")

    # プロットを作成
    api.plot_defect_energy(
        defect_energy_summary=summary,
        label="A",  # 化学ポテンシャル条件
        filename="formation_energy_A.pdf",
    )

補正
^^^^

``make_efnv_correction``
""""""""""""""""""""""""

EFNV（Extended Freysoldt-Neugebauer-Van de Walle）補正を計算します。

.. code-block:: python

    from pydefect import api
    from monty.serialization import loadfn

    calc_results = loadfn("Va_O1_1/calc_results.json")
    perfect_cr = loadfn("perfect/calc_results.json")
    unitcell = loadfn("unitcell.yaml")

    # EFNV 補正を計算
    efnv = api.make_efnv_correction(
        charge=1,  # 欠陥の電荷
        calc_results=calc_results,
        perfect_calc_results=perfect_cr,
        dielectric_tensor=unitcell.dielectric_constant,
    )

    print(f"点電荷補正: {efnv.point_charge_correction} eV")

    # 結果を保存
    efnv.to_json_file("Va_O1_1/efnv_correction.json")

``make_gkfo_correction``
""""""""""""""""""""""""

GKFO 補正を計算します（電荷遷移の補正）。

.. code-block:: python

    from pydefect import api
    from monty.serialization import loadfn

    efnv = loadfn("Va_O1_1/efnv_correction.json")
    initial_cr = loadfn("Va_O1_0/calc_results.json")
    final_cr = loadfn("Va_O1_2/calc_results.json")
    unitcell = loadfn("unitcell.yaml")

    # GKFO 補正を計算
    gkfo = api.make_gkfo_correction(
        efnv_correction=efnv,
        additional_charge=1,
        initial_calc_results=initial_cr,
        final_calc_results=final_cr,
        diele_tensor=unitcell.dielectric_constant,
        ion_clamped_diele_tensor=unitcell.ele_dielectric_constant,
    )

バンドエッジ
^^^^^^^^^^^^

``make_perfect_band_edge_state``
""""""""""""""""""""""""""""""""

パーフェクトスーパーセルのバンドエッジ状態を作成します。

.. code-block:: python

    from pydefect import api
    from pymatgen.io.vasp import Vasprun, Outcar, Procar

    vasprun = Vasprun("perfect/vasprun.xml")
    outcar = Outcar("perfect/OUTCAR")
    procar = Procar("perfect/PROCAR")

    # バンドエッジ状態を作成
    pbes = api.make_perfect_band_edge_state(
        vasprun=vasprun,
        outcar=outcar,
        procar=procar,
    )

    pbes.to_json_file("perfect_band_edge_state.json")

``make_band_edge_states``
"""""""""""""""""""""""""

欠陥系のバンドエッジ状態を判定します。

.. code-block:: python

    from pydefect import api
    from monty.serialization import loadfn

    orb_infos = loadfn("Va_O1_0/band_edge_orbital_infos.json")
    pbes = loadfn("perfect_band_edge_state.json")

    # バンドエッジ状態を判定
    bes = api.make_band_edge_states(
        band_edge_orbital_infos=orb_infos,
        perfect_band_edge_state=pbes,
    )

    print(f"浅い準位か: {bes.is_shallow}")

ユーティリティ
^^^^^^^^^^^^^^

``print_json``
""""""""""""""

JSON オブジェクトの内容を読みやすい形式で出力します。

.. code-block:: python

    from pydefect import api
    from monty.serialization import loadfn

    obj = loadfn("supercell_info.json")
    api.print_json(obj)

完全なワークフロー例
--------------------

MgAl₂O₄ の欠陥計算を Python API で実行する完全な例：

.. code-block:: python

    from pydefect import api
    from pymatgen.core import IStructure, Structure
    from monty.serialization import loadfn, dumpfn

    # 1. ユニットセルを読み込み
    unitcell = IStructure.from_file("unitcell/CONTCAR")

    # 2. スーパーセルを作成
    print("スーパーセルを作成中...")
    supercell_info, supercell = api.make_supercell(
        unitcell=unitcell,
        min_num_atoms=64,
        max_num_atoms=128,
    )
    supercell_info.to_json_file("supercell_info.json")
    supercell.to("SPOSCAR")
    print(f"  原子数: {len(supercell)}")

    # 3. 欠陥セットを生成
    print("欠陥セットを生成中...")
    defect_set = api.make_defect_set(
        supercell_info=supercell_info,
        oxi_states={"Mg": 2, "Al": 3, "O": -2},
    )
    defect_set.to_yaml("defect_in.yaml")
    print(f"  欠陥数: {len(defect_set.names)}")

    # 4. 欠陥エントリを作成
    print("欠陥ディレクトリを作成中...")
    api.make_defect_entries(
        supercell_info=supercell_info,
        defect_set=defect_set,
    )

    # 5. (VASP計算を実行)
    print("VASP計算を実行してください...")

    # 6. 計算後の解析（例: Va_O1_0）
    print("結果を解析中...")
    perfect = Structure.from_file("perfect/CONTCAR")
    initial = Structure.from_file("Va_O1_0/POSCAR")
    final = Structure.from_file("Va_O1_0/CONTCAR")

    dsi = api.make_defect_structure_info(
        perfect_structure=perfect,
        initial_defect_structure=initial,
        final_defect_structure=final,
    )
    print(f"  対称性変化: {dsi.initial_site_sym} -> {dsi.final_site_sym}")

    print("完了！")

設計思想
--------

pydefect の API は以下の原則に基づいて設計されています：

1. **CLI と API の分離**
   
   - CLI は API のラッパーとして実装
   - 同じ機能が CLI と Python 両方から利用可能

2. **関数型スタイル**
   
   - 入力を受け取り、結果を返す純粋関数
   - 副作用（ファイル出力）は呼び出し側で制御

3. **型安全性**
   
   - すべての関数に型ヒントを提供
   - dataclass ベースのモデルクラス

4. **ドキュメント**
   
   - すべての関数に Google スタイルの docstring
   - 引数と戻り値の詳細な説明
