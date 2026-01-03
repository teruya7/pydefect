Defect Calculations
===================

欠陥計算の実行と結果のパースについて説明します。

Step 1: 欠陥ディレクトリの作成
------------------------------

VASP 入力ファイルを含む欠陥ディレクトリを作成します。

.. code-block:: bash

    pydefect_vasp de -s supercell_info.json -d defect_in.yaml

作成されるディレクトリ構造：

.. code-block:: text

    defect/
    ├── perfect/
    │   ├── defect_entry.json
    │   ├── POSCAR
    │   ├── INCAR
    │   ├── KPOINTS
    │   └── POTCAR
    ├── Va_O1_0/
    ├── Va_O1_1/
    ├── Va_O1_2/
    ├── Va_Mg1_0/
    └── ...

欠陥エントリを確認：

.. code-block:: bash

    pydefect_print Va_O1_1/defect_entry.json

出力例：

.. code-block:: text

    name: Va_O1_1
    charge: 1
    defect_center: (0.250, 0.250, 0.250)
    corrections: {}

Step 2: VASP 計算の実行
-----------------------

各ディレクトリで VASP 計算を実行します（pydefect 外の操作）：

.. code-block:: bash

    for d in */; do
        cd $d
        # VASP 計算を投入
        sbatch run_vasp.sh
        cd ..
    done

重要な注意点：

- すべての欠陥と `perfect/` で同じ ENCUT を使用
- 十分な k 点サンプリング
- 適切な収束条件

Step 3: 計算結果のパース
------------------------

計算完了後、結果をパースします。

.. code-block:: bash

    # 個別のディレクトリを指定
    pydefect_vasp cr -d Va_O1_0 Va_O1_1 Va_O1_2

    # ワイルドカードで全ディレクトリを処理
    pydefect_vasp cr -d */

各ディレクトリに `calc_results.json` が生成されます。

結果を確認：

.. code-block:: bash

    pydefect_print Va_O1_0/calc_results.json

出力例：

.. code-block:: text

    energy: -385.456
    magnetization: 0.0
    electronic_conv: True
    ionic_conv: True
    site_potentials: [1.23, 1.25, ...]

Step 4: 欠陥構造情報の作成
--------------------------

緩和後の構造解析を行います。

.. code-block:: bash

    pydefect dsi -d Va_O1_0 Va_O1_1 -s supercell_info.json

各ディレクトリに `defect_structure_info.json` が生成されます。

Python API を使う場合
---------------------

.. code-block:: python

    from pydefect import api
    from pymatgen.core import Structure
    
    perfect = Structure.from_file("perfect/CONTCAR")
    initial = Structure.from_file("Va_O1_0/POSCAR")
    final = Structure.from_file("Va_O1_0/CONTCAR")
    
    dsi = api.make_defect_structure_info(
        perfect_structure=perfect,
        initial_defect_structure=initial,
        final_defect_structure=final
    )
    
    print(f"対称性変化: {dsi.initial_site_sym} -> {dsi.final_site_sym}")

次のステップ
------------

:doc:`analysis` へ進んで、補正とエネルギー解析を行います。
