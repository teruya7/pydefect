Quick Start
===========

このガイドでは、pydefect を使って MgAl₂O₄ の点欠陥計算を行う手順を説明します。

概要
----

pydefect は非金属固体の点欠陥計算を自動化するPythonパッケージです：

.. image:: /_images/pydefect.png
   :width: 600px
   :align: center

ワークフローは3つの主要な部分で構成されます：

1. **Unitcell**: 緩和構造、バンドエッジ、誘電定数
2. **Chemical Potential Diagram (CPD)**: 競合相と化学ポテンシャル
3. **Defect**: スーパーセル、欠陥構造、形成エネルギー

インストール
------------

.. code-block:: bash

    pip install pydefect

または開発版をインストール：

.. code-block:: bash

    git clone https://github.com/kumagai-group/pydefect.git
    cd pydefect
    pip install -e .

ディレクトリ構造
----------------

以下のディレクトリ構造を推奨します：

.. code-block:: text

    MgAl2O4/
    ├── pydefect.yaml        # 設定ファイル
    ├── vise.yaml
    ├── unitcell/
    │   ├── structure_opt/   # 緩和構造
    │   ├── band/            # バンド構造
    │   ├── dos/             # 状態密度
    │   └── dielectric/      # 誘電定数
    ├── cpd/                 # 競合相
    │   ├── MgO_mp-xxx/
    │   ├── Al2O3_mp-xxx/
    │   └── ...
    └── defect/              # 欠陥計算
        ├── perfect/
        ├── Va_O1_0/
        ├── Va_O1_1/
        └── ...

CLIコマンド
-----------

pydefect は5つのコマンドラインツールを提供します：

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - コマンド
     - 説明
   * - ``pydefect``
     - メインコマンド（DFTコード非依存）
   * - ``pydefect_vasp``
     - VASP専用コマンド
   * - ``pydefect_util``
     - ユーティリティコマンド
   * - ``pydefect_vasp_util``
     - VASP専用ユーティリティ
   * - ``pydefect_print``
     - JSONファイルを読みやすい形式で表示

``-h`` フラグでヘルプを表示：

.. code-block:: bash

    pydefect s -h
    pydefect_vasp u -h

Python APIを使う場合
--------------------

CLIコマンドの代わりに、Python APIを直接使用することもできます：

.. code-block:: python

    from pydefect import api

    # スーパーセルを作成
    supercell_info, supercell = api.make_supercell(
        unitcell=structure,
        min_num_atoms=64,
        max_num_atoms=128
    )

    # 欠陥セットを生成
    defect_set = api.make_defect_set(
        supercell_info=supercell_info,
        oxi_states={"Mg": 2, "Al": 3, "O": -2}
    )

完全なワークフロー例 (MgAl₂O₄)
-------------------------------

Step 1: スーパーセルの作成
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    cd MgAl2O4/defect

    # 緩和された unitcell からスーパーセルを作成
    pydefect s -p ../unitcell/structure_opt/CONTCAR

これにより ``supercell_info.json`` と ``SPOSCAR`` が生成されます：

.. code-block:: bash

    $ ls
    supercell_info.json
    SPOSCAR

スーパーセル情報を確認：

.. code-block:: bash

    $ pydefect_print supercell_info.json
    Space group: Fd-3m
    Trans. matrix: [[-2, 2, 2], [2, -2, 2], [2, 2, -2]]
    Number of atoms: 112
    Sites:
      Mg1: Wyckoff a, Site sym. -43m, indices: [0, 1, 2, ...]
      Al1: Wyckoff d, Site sym. -3m, indices: [8, 9, 10, ...]
      O1:  Wyckoff e, Site sym. 3m, indices: [24, 25, 26, ...]

Step 2: 欠陥セットの生成
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # デフォルトの酸化状態で欠陥セットを生成
    pydefect ds -o Mg 2 Al 3 O -2

特定のドーパントを追加する場合：

.. code-block:: bash

    # Sc と Ti をドーパントとして追加
    pydefect ds -o Mg 2 Al 3 O -2 -d Sc Ti

生成された ``defect_in.yaml`` を確認：

.. code-block:: yaml

    # defect_in.yaml （抜粋）
    Va_O1:
      - 0  # 中性
      - 1  # +1
      - 2  # +2
    Va_Mg1:
      - 0
      - -1
      - -2
    Al_Mg1:  # 反サイト欠陥
      - 0
      - 1

Step 3: 欠陥エントリの作成
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # VASP入力ファイルを含む欠陥ディレクトリを作成
    pydefect_vasp de -s supercell_info.json -d defect_in.yaml

これにより各欠陥のディレクトリが作成されます：

.. code-block:: bash

    $ ls
    Va_O1_0/
    Va_O1_1/
    Va_O1_2/
    Va_Mg1_0/
    Va_Mg1_-1/
    Va_Mg1_-2/
    perfect/
    ...

各ディレクトリには VASP 入力ファイルが含まれています：

.. code-block:: bash

    $ ls Va_O1_0/
    defect_entry.json
    POSCAR
    INCAR
    KPOINTS
    POTCAR

Step 4: VASP計算の実行
^^^^^^^^^^^^^^^^^^^^^^

各ディレクトリでVASP計算を実行します（このステップはpydefect外で行います）：

.. code-block:: bash

    for d in */; do
        cd $d
        # VASP計算を投入
        sbatch run_vasp.sh
        cd ..
    done

Step 5: 計算結果の解析
^^^^^^^^^^^^^^^^^^^^^^

VASP計算が完了したら、結果を解析します：

.. code-block:: bash

    # 各欠陥ディレクトリの計算結果をパース
    pydefect_vasp cr -d Va_O1_0 Va_O1_1 Va_O1_2 Va_Mg1_0 ...

    # または、ワイルドカードで全ディレクトリを指定
    pydefect_vasp cr -d */

各ディレクトリに ``calc_results.json`` が生成されます。

Step 6: 補正の計算
^^^^^^^^^^^^^^^^^^

静電的補正（EFNV補正）を計算：

.. code-block:: bash

    pydefect efnv \
        -d Va_O1_0 Va_O1_1 Va_O1_2 \
        -pcr perfect/calc_results.json \
        -u ../unitcell/unitcell.yaml

各ディレクトリに ``efnv_correction.json`` と補正プロットが生成されます。

Step 7: 欠陥形成エネルギーの計算
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

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

Step 8: 結果のプロット
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # 欠陥形成エネルギー図をプロット
    pydefect pe -d defect_energy_summary.json -l A

    # 複数のラベル（化学ポテンシャル条件）でプロット
    pydefect pe -d defect_energy_summary.json -l A B C

.. image:: /_images/formation_energy.png
   :width: 500px
   :align: center
   :alt: Defect formation energy diagram

よくある問題
------------

Q: supercell_info.json が生成されない
    スーパーセル作成時にエラーが発生していないか確認してください。
    POSCAR/CONTCAR ファイルが正しい形式であることを確認してください。

Q: 欠陥が認識されない
    酸化状態 (``-o``) が正しく指定されているか確認してください。
    すべての元素の酸化状態を指定する必要があります。

Q: 補正値が異常に大きい
    スーパーセルのサイズが十分大きいか確認してください（最低64原子推奨）。
    誘電定数が正しく計算されているか確認してください。

次のステップ
------------

- :doc:`/user_guide/index` - 詳細なステップバイステップチュートリアル
- :doc:`/explanation/index` - 理論的背景
- :doc:`/api/index` - Python API リファレンス
