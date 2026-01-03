API Reference
=============

pydefect の API リファレンスです。

.. toctree::
   :maxdepth: 2

   pydefect_api
   cli_reference
   preparation
   analysis

概要
----

pydefect は以下の2つの方法でアクセスできます：

1. **コマンドラインインターフェース (CLI)**
   - 5つのメインコマンド: pydefect, pydefect_vasp, pydefect_util, pydefect_vasp_util, pydefect_print
   - 42以上のサブコマンド
   - 詳細は :doc:`cli_reference` を参照

2. **Python API**
   - ``pydefect.api`` モジュール
   - 25以上の関数
   - 詳細は :doc:`pydefect_api` を参照

クイックリファレンス
--------------------

CLI コマンドと API 関数の対応表：

.. list-table::
   :widths: 30 30 40
   :header-rows: 1

   * - 機能
     - CLI
     - API
   * - スーパーセル作成
     - ``pydefect s``
     - ``api.make_supercell()``
   * - 欠陥セット生成
     - ``pydefect ds``
     - ``api.make_defect_set()``
   * - 欠陥エントリ作成
     - ``pydefect_vasp de``
     - ``api.make_defect_entries()``
   * - 標準・相対エネルギー
     - ``pydefect sre``
     - ``api.make_standard_and_relative_energies()``
   * - CPD 作成
     - ``pydefect cv``
     - ``api.make_chem_pot_diag()``
   * - 欠陥構造解析
     - ``pydefect dsi``
     - ``api.make_defect_structure_info()``
   * - EFNV 補正
     - ``pydefect efnv``
     - ``api.make_efnv_correction()``
   * - 欠陥エネルギープロット
     - ``pydefect pe``
     - ``api.plot_defect_energy()``
