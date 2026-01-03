Unit Cell Calculations
======================

ホスト材料の準備について説明します。

Step 1: 構造緩和
----------------

まず、ユニットセルの構造緩和を行います。

.. code-block:: bash

    mkdir -p unitcell/structure_opt
    cd unitcell/structure_opt
    
    # vise を使って VASP 入力を生成
    vise vs -x pbesol

構造最適化が完了したら、`CONTCAR` が緩和された構造になります。

Step 2: バンド構造計算
----------------------

VBM と CBM を取得するためにバンド構造を計算します。

.. code-block:: bash

    mkdir ../band
    cd ../band
    cp ../structure_opt/CONTCAR POSCAR
    
    vise vs -x pbesol -t band -pd ../structure_opt

Step 3: 誘電定数計算
--------------------

EFNV 補正に必要な誘電定数を計算します。

.. code-block:: bash

    mkdir ../dielectric
    cd ../dielectric
    cp ../structure_opt/CONTCAR POSCAR
    
    # イオン固定とイオン誘電両方を計算
    vise vs -x pbesol -t dielectric_dfpt -pd ../structure_opt

Step 4: unitcell.yaml の作成
----------------------------

上記の計算結果から `unitcell.yaml` を作成します。

.. code-block:: bash

    cd ..  # unitcell/ に移動
    
    pydefect_vasp u \
        -vb band/vasprun.xml \
        -ob band/OUTCAR \
        -odc dielectric/OUTCAR \
        -odi dielectric/OUTCAR

生成される `unitcell.yaml`:

.. code-block:: yaml

    vbm: 4.0183
    cbm: 9.2376
    ele_dielectric_const:
      - [3.08, 0.0, 0.0]
      - [0.0, 3.08, 0.0]
      - [0.0, 0.0, 3.08]
    ion_dielectric_const:
      - [5.04, 0.0, 0.0]
      - [0.0, 5.04, 0.0]
      - [0.0, 0.0, 5.04]

Python API を使う場合
---------------------

.. code-block:: python

    from pydefect import api
    from pymatgen.io.vasp import Vasprun, Outcar

    unitcell = api.make_unitcell_from_vasp(
        vasprun_band=Vasprun("band/vasprun.xml"),
        outcar_band=Outcar("band/OUTCAR"),
        outcar_dielectric_clamped=Outcar("dielectric/OUTCAR"),
        outcar_dielectric_ionic=Outcar("dielectric/OUTCAR"),
    )

次のステップ
------------

:doc:`chemical_potential` へ進んで、化学ポテンシャル図を作成します。
