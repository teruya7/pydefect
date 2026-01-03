Chemical Potential Diagram
==========================

化学ポテンシャル図 (CPD) の構築について説明します。

Step 1: 競合相の取得
--------------------

Materials Project から競合相を取得します。

.. code-block:: bash

    mkdir cpd
    cd cpd
    
    # MgAl2O4 の競合相を取得
    pydefect_vasp mp -e Mg Al O --e_above_hull 0.0005

これにより以下のようなディレクトリが作成されます：

.. code-block:: text

    cpd/
    ├── Al2O3_mp-1143/
    ├── MgO_mp-1265/
    ├── MgAl2O4_mp-3536/
    ├── Al_mp-134/
    ├── Mg_mp-1056702/
    └── mol_O2/

Step 2: VASP 計算の実行
-----------------------

各相でエネルギー計算を実行します。

.. code-block:: bash

    # 共通の ENCUT を設定（最大の 1.3 倍）
    for d in *_*/; do
        cd $d
        vise vs -uis ENCUT 520.0 -x pbesol
        # VASP 計算を投入
        cd ..
    done

Step 3: 組成エネルギーの作成
----------------------------

計算完了後、組成エネルギーを作成します。

.. code-block:: bash

    pydefect_vasp mce -d *_*/

生成される `composition_energies.yaml`:

.. code-block:: yaml

    Al: -4.084
    Mg: -1.710
    O: -5.139
    Al2O3: -20.416
    MgO: -9.680
    MgAl2O4: -35.325

Step 4: 標準・相対エネルギーの計算
----------------------------------

.. code-block:: bash

    pydefect sre -y composition_energies.yaml

生成されるファイル:

- `standard_energies.yaml`: 標準状態のエネルギー
- `relative_energies.yaml`: 相対エネルギー

Step 5: CPD の作成
------------------

.. code-block:: bash

    pydefect cv -y relative_energies.yaml -t MgAl2O4

生成されるファイル:

- `chem_pot_diag.json`: 化学ポテンシャル図データ
- `target_vertices.yaml`: 頂点（化学ポテンシャル条件）

Step 6: CPD のプロット
----------------------

.. code-block:: bash

    pydefect pc -cpd chem_pot_diag.json

`cpd.pdf` が生成されます。

Python API を使う場合
---------------------

.. code-block:: python

    from pydefect import api
    from pydefect.analysis.chemical_potential.models import (
        CompositionEnergies, RelativeEnergies
    )

    # 組成エネルギーを読み込み
    comp_energies = CompositionEnergies.from_yaml("composition_energies.yaml")
    
    # 標準・相対エネルギーを計算
    std_energies, rel_energies = api.make_standard_and_relative_energies(
        comp_energies
    )
    
    # CPD を作成
    cpd = api.make_chem_pot_diag(
        rel_energies,
        target="MgAl2O4"
    )

次のステップ
------------

:doc:`supercell_defects` へ進んで、スーパーセルと欠陥を設定します。
