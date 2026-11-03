# -*- coding: utf-8 -*-
# ライブラリのインポート
import os
import sys
import datetime
import time

# プロジェクトのホームディレクトリ
PROJECT_HOME_DIR = os.path.dirname(os.path.abspath(__file__))

# 自作ライブラリの場所を追加
sys.path.append(os.path.join(PROJECT_HOME_DIR,'config'))
sys.path.append(os.path.join(PROJECT_HOME_DIR,'lib'))

# 自作ライブラリのインポート
import Calc_RelativeDielectricConstant as calc_rdc

# 処理概要　生データ（ステップ応答）から比誘電率を計算するラッパー関数
# 引数　なし
# 戻り値　なし
def Convert_StepResponse2RelativeDielectricConstant():
    calc_rdc.Calc_RelativeDielectricConstant()

if __name__ == '__main__':
    Convert_StepResponse2RelativeDielectricConstant()
