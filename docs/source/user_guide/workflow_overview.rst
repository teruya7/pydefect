Workflow Overview
=================

pydefect を使った点欠陥計算の全体的なワークフローを説明します。

概要図
------

.. image:: /_images/pydefect.png
   :width: 600px
   :align: center

点欠陥計算は3つの主要な部分で構成されます：

1. **Unitcell 計算**: バンド構造と誘電定数
2. **Chemical Potential Diagram (CPD)**: 競合相と化学ポテンシャル
3. **Defect 計算**: 欠陥形成エネルギー

Step 1: Unitcell 計算
---------------------

まず、緩和されたユニットセル構造から以下を計算します：

.. code-block:: text

    unitcell/
    ├── structure_opt/   # 構造緩和
    ├── band/            # バンド構造（バンドエッジ）
    ├── dos/             # 状態密度
    ├── dielectric_clamped/   # イオン固定誘電定数
    └── dielectric_ionic/     # イオン誘電定数

unitcell.yaml の作成
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    cd unitcell
    
    # VASP出力からunitcell.yamlを作成
    pydefect_vasp u \
        -vb band/vasprun.xml \
        -ob band/OUTCAR \
        -odc dielectric_clamped/OUTCAR \
        -odi dielectric_ionic/OUTCAR

生成される ``unitcell.yaml``:

.. code-block:: yaml

    vbm: 4.0
    cbm: 8.0
    ele_dielectric_const:
      - [5.0, 0.0, 0.0]
      - [0.0, 5.0, 0.0]
      - [0.0, 0.0, 5.0]
    ion_dielectric_const:
      - [10.0, 0.0, 0.0]
      - [0.0, 10.0, 0.0]
      - [0.0, 0.0, 10.0]

Step 2: Chemical Potential Diagram
----------------------------------

欠陥形成エネルギーは化学ポテンシャルに依存するため、
安定な化学ポテンシャル範囲を計算します。

競合相の取得
^^^^^^^^^^^^

.. code-block:: bash

    cd cpd
    
    # Materials Project から競合相を取得
    pydefect_vasp mp -e Mg Al O
    
    # 各相でVASP計算を実行
    # ...
    
    # 組成エネルギーを計算
    pydefect_vasp mce -d MgO Al2O3 MgAl2O4 ...

CPD の計算
^^^^^^^^^^

.. code-block:: bash

    # 標準・相対エネルギーを計算
    pydefect sre -y composition_energies.yaml
    
    # 化学ポテンシャル図を作成
    pydefect cv -y relative_energies.yaml -t MgAl2O4
    
    # CPD をプロット
    pydefect pc -cpd chem_pot_diag.json

Step 3: Defect 計算
-------------------

スーパーセルを作成し、各欠陥の計算を実行します。

スーパーセル作成
^^^^^^^^^^^^^^^^

.. code-block:: bash

    cd defect
    
    # スーパーセルを作成
    pydefect s -p ../unitcell/structure_opt/CONTCAR

欠陥セット生成と計算準備
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # 欠陥セットを生成
    pydefect ds -o Mg 2 Al 3 O -2
    
    # 侵入サイトを追加（オプション）
    pydefect ai -s supercell_info.json -p SPOSCAR -c 0.25 0.25 0.25 -i oct
    
    # 欠陥エントリを作成
    pydefect_vasp de -s supercell_info.json -d defect_in.yaml

VASP 計算と結果解析
^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # (VASP計算を実行)
    
    # 計算結果をパース
    pydefect_vasp cr -d */
    
    # 欠陥構造情報を作成
    pydefect dsi -d Va_O1_0 Va_O1_1 -s supercell_info.json

補正と形成エネルギー
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # EFNV 補正を計算
    pydefect efnv \
        -d Va_O1_0 Va_O1_1 Va_O1_2 \
        -pcr perfect/calc_results.json \
        -u ../unitcell/unitcell.yaml
    
    # 欠陥エネルギー情報を計算
    pydefect dei \
        -d Va_O1_0 Va_O1_1 Va_O1_2 \
        -u ../unitcell/unitcell.yaml \
        -pcr perfect/calc_results.json \
        -se ../cpd/standard_energies.yaml
    
    # エネルギーサマリーを作成
    pydefect des \
        -d Va_O1_0 Va_O1_1 Va_O1_2 \
        -u ../unitcell/unitcell.yaml

結果のプロット
^^^^^^^^^^^^^^

.. code-block:: bash

    # 欠陥形成エネルギー図
    pydefect pe -d defect_energy_summary.json -l A B C

完全なスクリプト例
------------------

上記のワークフローをスクリプト化した例：

.. code-block:: bash

    #!/bin/bash
    # defect_workflow.sh
    
    set -e  # エラー時に停止
    
    # 0. 設定
    TARGET="MgAl2O4"
    UNITCELL_DIR="../unitcell"
    CPD_DIR="../cpd"
    
    # 1. スーパーセル作成
    echo "Creating supercell..."
    pydefect s -p ${UNITCELL_DIR}/structure_opt/CONTCAR
    
    # 2. 欠陥セット生成
    echo "Generating defect set..."
    pydefect ds -o Mg 2 Al 3 O -2
    
    # 3. 欠陥エントリ作成
    echo "Creating defect entries..."
    pydefect_vasp de -s supercell_info.json -d defect_in.yaml
    
    echo "Done! Now run VASP calculations for each defect directory."

Python APIを使った自動化
------------------------

より複雑なワークフローの自動化には Python API を使用できます。
詳細は :doc:`/api/pydefect_api` を参照してください。

.. code-block:: python

    from pydefect import api
    from pathlib import Path
    
    def run_workflow():
        # スーパーセル作成
        unitcell = IStructure.from_file("unitcell/CONTCAR")
        supercell_info, supercell = api.make_supercell(
            unitcell=unitcell,
            min_num_atoms=64
        )
        
        # 欠陥セット生成
        defect_set = api.make_defect_set(
            supercell_info=supercell_info,
            oxi_states={"Mg": 2, "Al": 3, "O": -2}
        )
        
        # 欠陥エントリ作成
        api.make_defect_entries(supercell_info, defect_set)
        
        print(f"Created {len(defect_set.names)} defect directories")

次のステップ
------------

- :doc:`supercell_defects` - スーパーセルと欠陥の詳細
- :doc:`chemical_potential` - 化学ポテンシャルの詳細
- :doc:`analysis` - 解析の詳細
- :doc:`/explanation/index` - 理論的背景
