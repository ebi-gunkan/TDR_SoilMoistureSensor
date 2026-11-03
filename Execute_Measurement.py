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
import system_data as system_data
import user_data as user_data
import NanoVNA as nanovna

# 処理概要　測定データをテキストファイルに書き出す
# 引数　step_response：測定データ、data_point：測定点数、measurement_point：測定点数
# 戻り値　なし
def Record_MeasurementData(step_response :[float],file_name :str,measurement_point :int):
    # ファイルがなければ新規作成
    if not os.path.isfile(PROJECT_HOME_DIR + "/raw_data/" + file_name):
        f = open(PROJECT_HOME_DIR + "/raw_data/" + file_name,"w")
        f.close()

    # データを書き込み
    now = datetime.datetime.now()
    f = open(PROJECT_HOME_DIR + "/raw_data/" + file_name,"a")
    f.write(now.strftime('%04Y/%m/%d %H:%M:%S') + str("\n"))
    for i in range(measurement_point):
        f.write(str(step_response[i]) + "\n")
    f.close()

# 処理概要　測定実行
# 引数　なし
# 戻り値　測定成否（0：成功、1：失敗）
def Execute():
    # ローカル変数の定義
    step_response :float = []               # ステップ応答
    ans :int = system_data.NANOVNA_READ_NG  # ステップ応答測定結果
    measurement_point_suffix :str           # 測定点数を示す接尾語

    # 現在時刻を取得
    now = datetime.datetime.now()

    # 書き込み先のファイル名を取得（yyyymmddhh00.txt）
    file_name_base = format(now.year,"#04d") \
                    + format(now.month,"#02d") \
                    + format(now.day,"#02d") + "_" \
                    + format(now.hour,"#02d") \
                    + format(now.minute,"#02d") + "00_"

    # 接尾語を定義
    for measurement_point in [system_data.MEASUREMENT_POINT_STANDARD,system_data.MEASUREMENT_POINT_DRY]:
        if measurement_point == system_data.MEASUREMENT_POINT_STANDARD:
            measurement_point_suffix = "std"
        else:
            measurement_point_suffix = "dry"

        # 測定開始通知
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "," + str(measurement_point) + "point :measurement start.")

        # ステップ応答の測定
        step_response = []
        ans,step_response = nanovna.Get_StepResponse(measurement_point)

        if ans == 0:
            # ステップ応答の記録
            file_name = file_name_base + measurement_point_suffix +".txt"
            Record_MeasurementData(step_response,file_name,measurement_point)

        # 測定終了通知
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "," + str(measurement_point) + "point :measurement finished.")

    return(ans)

if __name__ == '__main__':
    # プログラム実行直後に1回測定し、その後は1hに1回測定
    try:
        # 権限付与
        os.chmod(system_data.DEV_NAME,0o666)

        Execute()
        while True:
            now = datetime.datetime.now()
            if now.minute == 0 and now.second <= 3:
                Execute()
                time.sleep(3)
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
