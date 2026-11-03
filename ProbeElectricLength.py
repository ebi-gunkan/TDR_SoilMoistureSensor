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
import Calc_RelativeDielectricConstant as calc_rdc

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

# 処理概要　距離軸データが格納されたテキストファイルから読み出して配列に格納
# 引数　measurement_point：測定点数
# 戻り値　距離軸データ配列（リスト型）
def Get_DistanceDomainData(measurement_point :int):
    # ローカル変数の定義
    distance_domain_data :float = []     # 距離軸データ格納用配列

    # ファイル読み出し
    if measurement_point == system_data.MEASUREMENT_POINT_STANDARD:
        f = open(PROJECT_HOME_DIR + "/config/distance_domain_std.txt","r",encoding="utf-8")
    elif measurement_point == system_data.MEASUREMENT_POINT_DRY:
        f = open(PROJECT_HOME_DIR + "/config/distance_domain_dry.txt","r",encoding="utf-8")
    data = f.readlines()
    f.close

    distance_domain_data = []
    for i in range(measurement_point):
        distance_domain_data.append(float(data[i].replace("\n","")))

    return(distance_domain_data)

# 処理概要　測定データをテキストファイルに書き出す
# 引数　step_response：測定データ、data_point：測定点数、measurement_point：測定点数
# 戻り値　なし
def Record_MeasurementData(step_response :[float],file_name :str,measurement_point :int):
    # ファイルがなければ新規作成
    if not os.path.isfile(PROJECT_HOME_DIR + "/probe_electirc_length/" + file_name):
        f = open(PROJECT_HOME_DIR + "/probe_electric_length/" + file_name,"w")
        f.close()

    # データを書き込み
    now = datetime.datetime.now()
    f = open(PROJECT_HOME_DIR + "/probe_electric_length/" + file_name,"a")
    f.write(now.strftime('%04Y/%m/%d %H:%M:%S') + str("\n"))
    for i in range(measurement_point):
        f.write(str(step_response[i]) + "\n")
    f.close()

# 処理概要　ステップ応答の測定
# 引数　sample_name：標準試料の名前
# 戻り値　測定成否（0：成功、1：失敗）
def Measure_StepResponse(sample_name :str):
    # ローカル変数の定義
    step_response :float = []               # ステップ応答
    ans :int = system_data.NANOVNA_READ_NG  # ステップ応答測定結果
    measurement_point_suffix :str           # 測定点数を示す接尾語

    # 現在時刻を取得
    now = datetime.datetime.now()

    # 書き込み先のファイル名を取得（yyyymmddhh00.txt）
    file_name_base = sample_name + "_"

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


# 処理概要　伝搬時間を計算
# 引数　標準試料の名前
# 戻り値　計算成否、伝搬距離
def Calc_PropagationDistance(sample_name :str):
    # ローカル変数の定義
    d_calc_result :int = system_data.D_DOUBT    # 伝搬の計算成否
    d :float                                    # 伝搬時間（ns）
    measurement_point :int                      # 測定点数
    adopted_measurement_point :int              # 伝搬時間の計算に使用したデータの測定点数
    reflection_array_std :float = []            # ステップ応答（通常の土壌水分域）
    reflection_array_dry :float = []            # ステップ応答（乾燥域）
    sample_surface_reflect :float               # 標準試料表面での反射波の到達時刻に相当する距離
    probe_end_reflect :float                    # プローブ終端での反射波の到達時刻に相当する距離

    # 距離軸データ一覧を取得（101点（通常）と51点（乾燥域用））
    distance_domain_std = Get_DistanceDomainData(system_data.MEASUREMENT_POINT_STANDARD)
    distance_domain_dry = Get_DistanceDomainData(system_data.MEASUREMENT_POINT_DRY)

    # ステップ応答を取得（通常の土壌水分域と乾燥域）
    datetime_data,reflection_array_std = calc_rdc.Get_ReflectionArray(PROJECT_HOME_DIR + "/probe_electric_length/" + sample_name +"_std.txt")
    datetime_data,reflection_array_dry = calc_rdc.Get_ReflectionArray(PROJECT_HOME_DIR + "/probe_electric_length/" + sample_name +"_dry.txt")

    # 伝搬距離を計算（伝搬時間計算用の関数を流用）
    sample_surface_reflect,probe_end_reflect,d,d_calc_result = calc_rdc.Get_t(distance_domain_std,reflection_array_std,system_data.MEASUREMENT_POINT_STANDARD)

    # 101点（通常）で伝搬時間を正しく計算できた場合は比誘電率を計算する
    if d_calc_result == system_data.D_OK:
        adopted_measurement_point = system_data.MEASUREMENT_POINT_STANDARD

    #伝搬時間を正しく計算できてない可能性があれば51点（乾燥域用）のデータを使う
    else:
        # 51点（乾燥域用）のデータをつかって伝搬時間tを計算
        sample_surface_reflect,probe_end_reflect,d,d_calc_result = calc_rdc.Get_t(distance_domain_dry,reflection_array_dry,system_data.MEASUREMENT_POINT_DRY)
        adopted_measurement_point = system_data.MEASUREMENT_POINT_DRY

    return(d_calc_result,d)


# 処理概要　電気的長さの計算
# 引数　標準試料1の名前、標準試料1の比誘電率、標準試料2の名前、標準試料2の比誘電率
# 戻り値　計算成否（0：成功、1：失敗）
def Cacl_ElectricLength(sample1_name :str,sample1_rdc :float,sample2_name :str,sample2_rdc :float):
    # ローカル変数の定義
    proagation_distance1 :float     # 標準試料1の伝搬距離
    proagation_distance2 :float     # 標準試料2の伝搬距離
    d_calc_result1 :float           # 標準試料1の伝搬距離の計算成否
    d_calc_result2 :float           # 標準試料2の伝搬距離の計算成否
    electric_length :float = 0      # ロッドの電気的長さ

    # 伝搬距離を計算
    d_calc_result1,propagation_distance1 = Calc_PropagationDistance(sample1_name)
    d_calc_result2,propagation_distance2 = Calc_PropagationDistance(sample2_name)

    # 伝搬距離を計算できなかった場合は異常終了
    if d_calc_result1 == system_data.D_DOUBT \
    or d_calc_result2 == system_data.D_DOUBT:
        print("Could not calculate the electric length of probe.")
        if d_calc_result1 == system_data.D_DOUBT:
            print("The step response of " + sample1_name + "is invalid.")
        if d_calc_result1 == system_data.D_DOUBT:
            print("The step response of " + sample1_name + "is invalid.")
        sys.exit()

    # 電気的長さを計算
    electric_length = (propagation_distance2 - propagation_distance1) / \
        ((sample2_rdc ** 0.5)*system_data.VELOCITY_FACTOR - (sample1_rdc ** 0.5)*system_data.VELOCITY_FACTOR)

    # 計算結果を表示
    print("\nThe electric length of probe : " + str(electric_length) + " mm")
    print("Modify a parameter 'PROBE_ELECTRIC_LENGTH' in TDR_SoilMoistureSensor/config/user_data.py to " + str(int(electric_length + 0.5) / 1000))

if __name__ == '__main__':
    # ローカル変数の定義
    sample1_name :str = ""      # 電気的長さの決定に使用する標準試料1の名前
    sample1_rdc :float = 0      # 電気的長さの決定に使用する標準試料1の比誘電率（-）
    sample2_name :str = ""      # 電気的長さの決定に使用する標準試料2の名前
    sample2_rdc :float = 0      # 電気的長さの決定に使用する標準試料2の比誘電率（-）
    ans :int                    # 計算結果

    # コマンドライン引数の受け取り
    args = sys.argv[1:]

    # 標準試料のステップ応答測定コマンドの場合
    if len(args) == 2 and args[0] == "-measure":
        # コマンドライン引数を格納
        sample1_name = args[1]

        # 権限付与
        os.chmod(system_data.DEV_NAME,0o666)

        # 標準試料のステップ応答を測定
        Measure_StepResponse(sample1_name)

    elif len(args) == 5 and args[0] == "-calc":
        # 比誘電率が実数として与えられていなければコマンドライン引数異常で終了
        if isfloat(args[2]) == False or isfloat(args[4]) == False:
            print("\nInvalid arguments.")
            print("Use -help or --help or -h.")
            print("  e.g. sudo python3 ./ProbeElectricLength.py -help")
            print
            sys.exit()
        else:
            if float(args[2]) < 0 or float(args[4]) < 0:
                print("\nInvalid arguments.")
                print("Use -help or --help or -h.")
                print("  e.g. sudo python3 ./ProbeElectricLength.py -help")
                sys.exit()

        # コマンドライン引数を格納
        sample1_name = args[1]
        sample1_rdc = float(args[2])
        sample2_name = args[3]
        sample2_rdc = float(args[4])

        Cacl_ElectricLength(sample1_name,sample1_rdc,sample2_name,sample2_rdc)

    elif len(args) == 1 and args[0] in ("-help","-h","--help"):
        print("\nUsage:")
        print("  Measure step response of a standard resolution")
        print("    sudo python3 ProbeElectricLength.py -measure name")
        print("    e.g. python3 ProbeElectricLength.py -measure ethanol")
        print("  Calculate the electric length of a probe with 2 different standard resolutions")
        print("    sudo python3 ProbeElectricLength.py -calc name1 RDC1 name2 RDC2")
        print("    e.g. python3 ProbeElectricLength.py -measure ethanol 25.17 water 82.46")
        sys.exit()

    else:
        print("\nInvalid arguments.")
        print("Use -help or --help or -h.")
        print("  e.g. sudo python3 ./ProbeElectricLength.py -help")
        sys.exit()
