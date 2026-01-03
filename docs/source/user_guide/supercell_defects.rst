Supercell and Defects
=====================

スーパーセルの生成と欠陥の定義について説明します。

Step 1: スーパーセルの作成
--------------------------

緩和されたユニットセルからスーパーセルを作成します。

.. code-block:: bash

    mkdir defect
    cd defect
    
    # 原子数 64-128 の範囲で最適なスーパーセルを自動選択
    pydefect s -p ../unitcell/structure_opt/CONTCAR

生成されるファイル:

- `supercell_info.json`: スーパーセル情報
- `SPOSCAR`: スーパーセル構造

スーパーセル情報を確認：

.. code-block:: bash

    pydefect_print supercell_info.json

出力例：

.. code-block:: text

    Space group: Fd-3m
    Transformation matrix: [-1, 1, 1]  [1, -1, 1]  [1, 1, -1]
    Cell multiplicity: 4

       Irreducible element: Mg1
            Wyckoff letter: b
             Site symmetry: -43m
          Equivalent atoms: 0..7

       Irreducible element: Al1
            Wyckoff letter: c
             Site symmetry: .-3m
          Equivalent atoms: 8..23

       Irreducible element: O1
            Wyckoff letter: e
             Site symmetry: .3m
          Equivalent atoms: 24..55

オプション
^^^^^^^^^^

.. code-block:: bash

    # 原子数の範囲を指定
    pydefect s -p CONTCAR --min_atoms 50 --max_atoms 100

    # 明示的に変換行列を指定
    pydefect s -p CONTCAR --matrix 2 2 2

Step 2: 欠陥セットの生成
------------------------

どの欠陥を計算するかを定義します。

.. code-block:: bash

    # 酸化状態を指定して欠陥セットを生成
    pydefect ds -o Mg 2 Al 3 O -2

生成される `defect_in.yaml`:

.. code-block:: yaml

    Va_O1: [0, 1, 2]
    Va_Mg1: [-2, -1, 0]
    Va_Al1: [-3, -2, -1, 0, 1]
    Al_Mg1: [-1, 0, 1]
    # ...

ドーパントを追加：

.. code-block:: bash

    pydefect ds -o Mg 2 Al 3 O -2 -d Ca Sc

Step 3: 侵入サイトの追加（オプション）
--------------------------------------

侵入欠陥を計算する場合、侵入サイトを追加します。

方法1: 局所極値から検出
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # DOS 計算のディレクトリで
    pydefect_vasp le -c AECCAR0 AECCAR2 -s supercell_info.json
    
    # 検出されたサイトを追加
    pydefect_util ai -s supercell_info.json -le volumetric_data_local_extrema.json -i 1 2

方法2: 座標を直接指定
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    pydefect ai -s supercell_info.json -p SPOSCAR -c 0.25 0.25 0.25 -i "octahedral"

侵入サイトを削除：

.. code-block:: bash

    # インデックスで削除
    pydefect pi -s supercell_info.json -i 1
    
    # すべて削除
    pydefect pi -s supercell_info.json --pop_all

Python API を使う場合
---------------------

.. code-block:: python

    from pydefect import api
    from pymatgen.core import IStructure

    # スーパーセル作成
    unitcell = IStructure.from_file("../unitcell/structure_opt/CONTCAR")
    supercell_info, supercell = api.make_supercell(
        unitcell=unitcell,
        min_num_atoms=64,
        max_num_atoms=128
    )

    # 欠陥セット生成
    defect_set = api.make_defect_set(
        supercell_info=supercell_info,
        oxi_states={"Mg": 2, "Al": 3, "O": -2}
    )

    # 侵入サイト追加
    supercell_info = api.append_interstitial(
        supercell_info=supercell_info,
        base_structure=supercell,
        frac_coords=[0.25, 0.25, 0.25],
        info="octahedral"
    )

次のステップ
------------

:doc:`defect_calculations` へ進んで、VASP 計算を実行します。
