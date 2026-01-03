Analysis and Plotting
=====================

欠陥形成エネルギーの計算と可視化について説明します。

Step 1: EFNV 補正の計算
-----------------------

帯電欠陥の静電的補正を計算します。

.. code-block:: bash

    pydefect efnv \
        -d Va_O1_0 Va_O1_1 Va_O1_2 \
        -pcr perfect/calc_results.json \
        -u ../unitcell/unitcell.yaml

各ディレクトリに以下が生成されます：

- `efnv_correction.json`: 補正データ
- `site_potential.pdf`: ポテンシャルプロット

補正値を確認：

.. code-block:: bash

    pydefect_print Va_O1_1/efnv_correction.json

出力例：

.. code-block:: text

    point_charge_correction: 0.25 eV
    alignment_correction: 0.03 eV
    total_correction: 0.28 eV

Step 2: 欠陥エネルギー情報の作成
--------------------------------

各欠陥のエネルギー情報を計算します。

.. code-block:: bash

    pydefect dei \
        -d Va_O1_0 Va_O1_1 Va_O1_2 \
        -u ../unitcell/unitcell.yaml \
        -pcr perfect/calc_results.json \
        -se ../cpd/standard_energies.yaml

各ディレクトリに `defect_energy_info.json` が生成されます。

Step 3: エネルギーサマリーの作成
--------------------------------

全欠陥のエネルギーをまとめます。

.. code-block:: bash

    pydefect des \
        -d Va_O1_0 Va_O1_1 Va_O1_2 Va_Mg1_0 Va_Mg1_-1 \
        -u ../unitcell/unitcell.yaml \
        -pbes perfect/band_edge_state.json

`defect_energy_summary.json` が生成されます。

Step 4: 形成エネルギーのプロット
--------------------------------

欠陥形成エネルギー図をプロットします。

.. code-block:: bash

    # 単一の化学ポテンシャル条件
    pydefect pe -d defect_energy_summary.json -l A

    # 複数の条件
    pydefect pe -d defect_energy_summary.json -l A B C

    # Y軸範囲を指定
    pydefect pe -d defect_energy_summary.json -l A --y_range -2 5

出力ファイル：`defect_formation_energy_A.pdf`

Step 5: GKFO 補正（オプション）
-------------------------------

電荷遷移の補正が必要な場合：

.. code-block:: bash

    pydefect_util gkfo \
        -efnv Va_O1_1/efnv_correction.json \
        -icr Va_O1_0/calc_results.json \
        -fcr Va_O1_2/calc_results.json \
        -u ../unitcell/unitcell.yaml

追加の解析
----------

U値の計算
^^^^^^^^^

.. code-block:: bash

    pydefect_util u -d defect_energy_summary.json

ピンニングレベル
^^^^^^^^^^^^^^^^

.. code-block:: bash

    pydefect_util pl -d defect_energy_summary.json

VESTA用ファイル
^^^^^^^^^^^^^^^

.. code-block:: bash

    pydefect_util dvf -d Va_O1_0

Python API を使う場合
---------------------

.. code-block:: python

    from pydefect import api
    from monty.serialization import loadfn

    # EFNV 補正
    efnv = api.make_efnv_correction(
        charge=1,
        calc_results=loadfn("Va_O1_1/calc_results.json"),
        perfect_calc_results=loadfn("perfect/calc_results.json"),
        dielectric_tensor=unitcell.dielectric_constant
    )

    # 形成エネルギーのプロット
    summary = loadfn("defect_energy_summary.json")
    api.plot_defect_energy(summary, label="A")

おわりに
--------

これで pydefect を使った点欠陥計算の基本的なワークフローは完了です。

詳細については以下を参照してください：

- :doc:`/api/cli_reference`: 全 CLI コマンドのリファレンス
- :doc:`/api/pydefect_api`: Python API リファレンス
- :doc:`/explanation/index`: 理論的背景
