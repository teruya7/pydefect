CLI Reference
=============

pydefect のコマンドラインインターフェース (CLI) リファレンスです。
すべてのコマンドは ``-h`` または ``--help`` でヘルプを表示できます。

pydefect（メインコマンド）
--------------------------

DFTコードに依存しない汎用コマンドです。

スーパーセル作成 (s)
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # 基本的な使い方
    pydefect s -p CONTCAR

    # 原子数の範囲を指定
    pydefect s -p CONTCAR --min_atoms 64 --max_atoms 128

    # 明示的に変換行列を指定
    pydefect s -p CONTCAR --matrix 2 2 2

**出力ファイル:**
- ``supercell_info.json``: スーパーセル情報
- ``SPOSCAR``: スーパーセルの構造

欠陥セット生成 (ds)
^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # 基本的な使い方（酸化状態を指定）
    pydefect ds -o Mg 2 Al 3 O -2

    # ドーパントを追加
    pydefect ds -o Mg 2 Al 3 O -2 -d Sc Ti Zr

    # 既存の supercell_info.json を使用
    pydefect ds -o Mg 2 Al 3 O -2 -s supercell_info.json

**出力ファイル:**
- ``defect_in.yaml``: 欠陥設定ファイル

侵入原子の追加 (ai)
^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # 侵入サイトを追加
    pydefect ai -s supercell_info.json -p SPOSCAR -c 0.25 0.25 0.25 -i "octahedral_site"

    # 別の構造から侵入サイトを検出
    pydefect ai -s supercell_info.json -p structure_with_H.vasp -e H

**出力:**
- 更新された ``supercell_info.json``

侵入原子の削除 (pi)
^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # インデックスで侵入サイトを削除
    pydefect pi -s supercell_info.json -i 1

    # すべての侵入サイトを削除
    pydefect pi -s supercell_info.json --pop_all

標準・相対エネルギー (sre)
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # composition_energies.yaml から計算
    pydefect sre -y composition_energies.yaml

**出力ファイル:**
- ``standard_energies.yaml``
- ``relative_energies.yaml``

化学ポテンシャル図 (cv)
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # 相対エネルギーから CPD を作成
    pydefect cv -y relative_energies.yaml -t MgAl2O4

**出力ファイル:**
- ``chem_pot_diag.json``
- ``target_vertices.yaml``

CPD のプロット (pc)
^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # 化学ポテンシャル図をプロット
    pydefect pc -cpd chem_pot_diag.json

**出力ファイル:**
- ``cpd.pdf``

欠陥構造情報 (dsi)
^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # 欠陥構造を解析
    pydefect dsi -d Va_O1_0 Va_O1_1 -s supercell_info.json

欠陥エネルギー情報 (dei)
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # 欠陥エネルギーを計算
    pydefect dei \
        -d Va_O1_0 Va_O1_1 Va_O1_2 \
        -u unitcell.yaml \
        -pcr perfect/calc_results.json \
        -se standard_energies.yaml

**出力ファイル:**
- 各ディレクトリに ``defect_energy_info.json``

欠陥エネルギーサマリー (des)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # エネルギーサマリーを作成
    pydefect des \
        -d Va_O1_0 Va_O1_1 Va_O1_2 Va_Mg1_0 Va_Mg1_-1 \
        -u unitcell.yaml \
        -pbes perfect/band_edge_state.json

**出力ファイル:**
- ``defect_energy_summary.json``

計算サマリー (cs)
^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # 計算結果のサマリーを表示
    pydefect cs -d Va_O1_0 Va_O1_1 Va_O1_2 -pcr perfect/calc_results.json

欠陥形成エネルギーのプロット (pe)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # 基本的なプロット
    pydefect pe -d defect_energy_summary.json -l A

    # 複数の化学ポテンシャル条件
    pydefect pe -d defect_energy_summary.json -l A B C

    # フェルミ準位の範囲を指定
    pydefect pe -d defect_energy_summary.json -l A --y_range -2 5

**出力ファイル:**
- ``defect_formation_energy_A.pdf``

EFNV 補正 (efnv)
^^^^^^^^^^^^^^^^

.. code-block:: bash

    # 静電補正を計算
    pydefect efnv \
        -d Va_O1_0 Va_O1_1 Va_O1_2 \
        -pcr perfect/calc_results.json \
        -u unitcell.yaml

**出力ファイル:**
- 各ディレクトリに ``efnv_correction.json``
- ``site_potential.pdf``

バンドエッジ状態 (bes)
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # 欠陥のバンドエッジ状態を解析
    pydefect bes \
        -d Va_O1_0 Va_O1_1 \
        -pbes perfect/band_edge_state.json

pydefect_vasp
-------------

VASP 専用のコマンドです。

ユニットセル作成 (u)
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # バンド計算と誘電定数計算の結果から unitcell.yaml を作成
    pydefect_vasp u \
        -vb band/vasprun.xml \
        -ob band/OUTCAR \
        -odc dielectric_clamped/OUTCAR \
        -odi dielectric_ionic/OUTCAR

**出力ファイル:**
- ``unitcell.yaml``

計算結果のパース (cr)
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # 単一のディレクトリ
    pydefect_vasp cr -d Va_O1_0

    # 複数のディレクトリ
    pydefect_vasp cr -d Va_O1_0 Va_O1_1 Va_O1_2

    # ワイルドカード
    pydefect_vasp cr -d */

**出力ファイル:**
- 各ディレクトリに ``calc_results.json``

欠陥エントリ作成 (de)
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # VASP 入力ファイルを含む欠陥ディレクトリを作成
    pydefect_vasp de -s supercell_info.json -d defect_in.yaml

**出力:**
- 各欠陥のディレクトリ（POSCAR, INCAR, KPOINTS, POTCAR 含む）

Materials Project から構造取得 (mp)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # 化学系の安定相を取得
    pydefect_vasp mp -e Mg Al O

**出力:**
- 各相のディレクトリ（POSCAR 含む）

組成エネルギー作成 (mce)
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # vasprun.xml から組成エネルギーを計算
    pydefect_vasp mce -d MgO Al2O3 MgAl2O4

**出力ファイル:**
- ``composition_energies.yaml``

局所極値の検出 (le)
^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # CHGCARから侵入サイト候補を検出
    pydefect_vasp le -c CHGCAR -s supercell_info.json

パーフェクトバンドエッジ状態 (pbes)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # パーフェクトスーパーセルのバンドエッジ状態
    pydefect_vasp pbes \
        -v perfect/vasprun.xml \
        -o perfect/OUTCAR \
        -p perfect/PROCAR

**出力ファイル:**
- ``perfect_band_edge_state.json``

バンドエッジ軌道情報 (beoi)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # 欠陥系の軌道情報を解析
    pydefect_vasp beoi \
        -d Va_O1_0 Va_O1_1 \
        -pbes perfect/band_edge_state.json

pydefect_util
-------------

ユーティリティコマンドです。

JSON ファイルの表示 (print)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # 任意の JSON ファイルの内容を表示
    pydefect_util print supercell_info.json
    pydefect_util print defect_entry.json
    pydefect_util print calc_results.json
    pydefect_util print efnv_correction.json

VESTA ファイル作成 (dvf)
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # 欠陥構造の VESTA ファイルを作成
    pydefect_util dvf -d Va_O1_0

U 値の表示 (u)
^^^^^^^^^^^^^^

.. code-block:: bash

    # 遷移準位から U 値を計算
    pydefect_util u -d defect_energy_summary.json

ピニング準位の表示 (pl)
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # ピニング準位を表示
    pydefect_util pl -d defect_energy_summary.json

局所極値からの侵入原子追加 (ai)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # 局所極値解析から侵入サイトを追加
    pydefect_util ai -s supercell_info.json -le local_extrema.json

GKFO 補正 (gkfo)
^^^^^^^^^^^^^^^^

.. code-block:: bash

    # GKFO 補正を計算（電荷遷移の補正）
    pydefect_util gkfo \
        -efnv Va_O1_1/efnv_correction.json \
        -icr Va_O1_0/calc_results.json \
        -fcr Va_O1_2/calc_results.json \
        -u unitcell.yaml

キャリア濃度計算 (ccc)
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # キャリア濃度を計算
    pydefect_util ccc -t total_dos.json -T 300 600 900

欠陥濃度計算 (cdc)
^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # 欠陥濃度を計算
    pydefect_util cdc \
        -dc defect_concentrations.json \
        -cc carrier_concentrations.json \
        -T 300

pydefect_vasp_util
------------------

VASP 専用ユーティリティコマンドです。

欠陥エントリ作成 (de)
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # 手動で欠陥エントリを作成
    pydefect_vasp_util de \
        -s supercell_info.json \
        -n Va_O1_0

POSCAR の精緻化 (rdp)
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # 欠陥 POSCAR を精緻化
    pydefect_vasp_util rdp -d Va_O1_0 -s supercell_info.json

PARCHG ディレクトリ作成 (pd)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # PARCHG 計算用のディレクトリを作成
    pydefect_vasp_util pd -d Va_O1_0 -b "60:65"

グリッド計算 (cg)
^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # K点グリッドを計算
    pydefect_vasp_util cg -p POSCAR

全状態密度作成 (mtd)
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # vasprun.xml から全状態密度を作成
    pydefect_vasp_util mtd -v vasprun.xml

**出力ファイル:**
- ``total_dos.json``

電荷状態計算 (ccs)
^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # 電荷状態を計算（PARCHG 解析）
    pydefect_vasp_util ccs -d Va_O1_0

欠陥電荷情報計算 (cdc)
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # 欠陥電荷情報を PARCHG から計算
    pydefect_vasp_util cdc -d Va_O1_0

pydefect_print
--------------

JSON ファイルを人が読みやすい形式で表示します。

.. code-block:: bash

    # 使用例
    pydefect_print supercell_info.json
    pydefect_print defect_entry.json
    pydefect_print calc_results.json
    pydefect_print efnv_correction.json
    pydefect_print defect_energy_summary.json

出力例：

.. code-block:: text

    $ pydefect_print supercell_info.json
    -- SupercellInfo --
    Space group: Fd-3m (227)
    Transformation matrix: [[-2, 2, 2], [2, -2, 2], [2, 2, -2]]
    Number of sites: 112
    
    Sites:
      Mg1: Wyckoff a, Site sym: -43m, Indices: [0, 1, 2, 3, 4, 5, 6, 7]
      Al1: Wyckoff d, Site sym: -3m, Indices: [8, 9, 10, ..., 23]
      O1: Wyckoff e, Site sym: 3m, Indices: [24, 25, 26, ..., 111]
    
    Interstitials: None
