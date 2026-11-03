# -*- coding: utf-8 -*-
#ライブラリインポート
import serial
import serial.tools.list_ports
import datetime
import time
import re
import sys
import os

# プロジェクトのホームディレクトリ
PROJECT_HOME_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 自作ライブラリの場所を追加
sys.path.append(os.path.join(PROJECT_HOME_DIR,'config'))

# 自作ライブラリのインポート
import system_data as system_data
import user_data as user_data

# 処理概要　実数かどうか判定する
# 引数　s：判定したい文字列
# 戻り値　実数：True、実数以外：False
def isfloat(s :str):
    try:
        float(s)
    except ValueError:
        return False
    else:
        return True

# 処理概要　シリアル通信で受信したデータを全て破棄する
# 引数　ser_port：シリアルポート、th_to：タイムアウトまでの時間(sec）
# 戻り値　なし
def Read_AllDataAndDump(ser_port :str,th_to :int):
    # ローカル変数の定義と初期化
    tic     = time.time()           #時刻
    buff    = ser_port.readline()   #データ格納用バッファ

    # タイムアウトするまでデータを読み出し続ける
    while ((time.time() - tic) < -1 * th_to):
       buff += ser.readline()

# 処理概要　NanoVNAからTDR波形データを取得する
# 引数　測定点数
# 戻り値　測定成否（1：失敗、0：成功）、S11（Re）、S11（Im）
def Get_StepResponse(measurement_point :int):
    # ローカル変数の定義
    data :str = ""              # NanoVNAとの読み書きデータ
    status :int = 0             # 測定ステータス
    step_response :float = []   # ステップ応答

    try:
        # シリアルポートを開く
        Serial_Port=serial.Serial(port=system_data.DEV_NAME, baudrate=system_data.BAUDRATE, parity= 'N',timeout = 3)

        # 接続直後の不要なデータを削除
        data = "dummy"
        while not (data == "" or data == "ch>"):
            Serial_Port.write('\r\n'.encode('utf-8'))
            data = Serial_Port.readline()
            data = data.strip()
            data = data.decode('utf-8')

        # リコール時のレスポンスを読み出して破棄
        data = ""
        Serial_Port.write(('recall ' + str(system_data.RECALL_NO) + '\r\n').encode('utf-8'))
        while data != "ch>":
            data = Serial_Port.readline()
            data = data.strip()
            data = data.decode('utf-8')

        # 測定点数変換時のレスポンスを読み出して破棄
        data = ""
        Serial_Port.write(('sweep ' + str(system_data.START_FREQ) + ' ' + \
        str(system_data.STOP_FREQ) + ' ' + str(measurement_point) + '\r\n').encode('utf-8'))
        while data != "ch>":
            data = Serial_Port.readline()
            data = data.strip()
            data = data.decode('utf-8')

        # 測定ステータスを失敗として初期化
        status = 1

        # 測定データを格納する配列を初期化
        step_reponse = []
        for i in range(measurement_point):
            step_response.append(99)

        time.sleep(1)	# 安定待ち
        cnt = 0
        while status == 1:
            # 測定コマンド送信
            data = 'data 0\r\n'
            data = data.encode('utf-8')
            Serial_Port.write(data)

            for i in range(measurement_point):
                # 測定データを1行分読み出し
                data=Serial_Port.readline()
                data=data.strip()
                data=data.decode('utf-8')
                while isfloat(data) == False:
                    data=Serial_Port.readline()
                    data=data.strip()
                    data=data.decode('utf-8')


                #測定データが正しいか確認する
                if isfloat(data) == True:
                    if -2 < float(data) and float(data) < 2:
                        step_response[i] = float(data)

            #測定データの異常チェック
            status = 0
            for i in range(measurement_point):
                if step_response[i] == system_data.NANOVNA_INVALID_VALUE:
                    status = system_data.NANOVNA_READ_NG
                    break

            cnt += 1

            # 異常がありかつ4の倍数回ならリセットかける
            if status == system_data.NANOVNA_READ_NG:
                print("retry")
                if cnt % 4 == 0:
                    # リセット
                    data = 'reset\r\n'
                    data = data.encode('utf-8')
                    Serial_Port.write(data)

                    data = "dummy"
                    while not (data == "" or data == "ch>"):
                        data = Serial_Port.readline()
                        data=data.strip()
                        data=data.decode('utf-8')

                    time.sleep(3)
                    break

    finally:
        # 測定が終了したら切断する
        data = '~.\n'
        data = data.encode('utf-8')
        Serial_Port.write(data)

        if Serial_Port.is_open:
            data = '~.\n'
            data = data.encode('utf-8')
            Serial_Port.write(data)

            Serial_Port.close()

        return(status,step_response)

if __name__ == '__main__':
    #ローカル変数の定義
    step_response :float = []       # ステップ応答
    ans :int = 0                    # 戻り値

    ans,step_response = Get_StepResponse(system_data.MEASUREMENT_POINT_STANDARD)
    for i in range(system_data.MEASUREMENT_POINT_STANDARD):
        print("data[" + str(i) + "]=" + str(freq_re[i]) + "," + str(freq_im[i]))

    if ans == system_data.NANOVNA_READ_NG:
        print("NG")
    else:
        print("OK")
