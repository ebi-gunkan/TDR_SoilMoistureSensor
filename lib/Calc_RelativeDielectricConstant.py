# -*- coding: utf-8 -*-
# ライブラリのインポート
import os
import sys
import datetime
import glob
import numpy as np

# プロジェクトのホームディレクトリ
PROJECT_HOME_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 自作ライブラリの場所を追加
sys.path.append(os.path.join(PROJECT_HOME_DIR,'config'))

# 自作ライブラリのインポート
import system_data as system_data
import user_data as user_data

# 定数の定義（configファイルからの読み込み）
C_SPEED = system_data.C_SPEED						                # 光速（m/s）
PROBE_LENGTH = user_data.PROBE_ELECTRIC_LENGTH					    # プローブ電気的の長さ（m）
MEASUREMENT_POINT_STANDARD = system_data.MEASUREMENT_POINT_STANDARD	# 測定点数（通常の土壌水分域）
MEASUREMENT_POINT_DRY = system_data.MEASUREMENT_POINT_DRY		    # 測定点数（極乾燥域）
THRESHOLD_VALLEY = system_data.THRESHOLD_VALLEY                     # 地表面での反射とプローブ終端での反射が一体化を判断するための閾値：反射係数の谷の値
THRESHOLD_REFLECT_COEF = system_data.THRESHOLD_REFLLECT_COEF        # 反射係数が0付近でふらつく最初の部分をスキップするための閾値
T_DOUBT = system_data.T_DOUBT                                       # 伝搬時間の計算結果に疑義がある場合
T_OK = system_data.T_OK                                             # 伝搬時間の計算結果に疑義がない場合
RDC_DOUBT = system_data.RDC_DOUBT                                   # 比誘電率の計算結果に疑義がある場合
RDC_OK = system_data.RDC_OK                                         # 比誘電率の計算結果に疑義がない場合

# グローバル変数の定義
TIME_STEP_RISE_SURFACE: int = 0     # 地表面での反射波の立ち上がりはじめ
TIME_STEP_A: int = 0                # A点のタイムステップ
TIME_STEP_B: int = 0                # B点のタイムステップ
TIME_STEP_C: int = 0                # C点のタイムステップ
TIME_STEP_D: int = 0                # D点のタイムステップ
REFLECT_COEF_A: float = 0           # A点の反射係数
REFLECT_COEF_B: float = 0           # B点の反射係数
REFLECT_COEF_C: float = 0           # C点の反射係数
REFLECT_COEF_D: float = 0           # D点の反射係数
SLOPE_A: float = 0                  # A点の勾配
SLOPE_B: float = 0                  # B点の勾配
SLOPE_C: float = 0                  # C点の勾配
SLOPE_D: float = 0                  # D点の勾配
INTERCEPT_A: float = 0              # A点の切片
INTERCEPT_B: float = 0              # B点の切片
INTERCEPT_C: float = 0              # C点の切片
INTERCEPT_D: float = 0              # D点の切片

def debug():
    global TIME_STEP_RISE_SURFACE, TIME_STEP_A, TIME_STEP_B, TIME_STEP_C, TIME_STEP_D, REFLECT_COEF_A, REFLECT_COEF_B, REFLECT_COEF_C, REFLECT_COEF_D, SLOPE_A, SLOPE_B, SLOPE_C, SLOPE_D, INTERCEPT_A, INTERCEPT_B, INTERCEPT_C, INTERCEPT_D

    print(f"TIME_STEP_RISE_SURFACE = {TIME_STEP_RISE_SURFACE}")
    print(f"TIME_STEP_A = {TIME_STEP_A}")
    print(f"TIME_STEP_B = {TIME_STEP_B}")
    print(f"TIME_STEP_C = {TIME_STEP_C}")
    print(f"TIME_STEP_D = {TIME_STEP_D}")
    print(f"REFLECT_COEF_A = {REFLECT_COEF_A}")
    print(f"REFLECT_COEF_B = {REFLECT_COEF_B}")
    print(f"REFLECT_COEF_C = {REFLECT_COEF_C}")
    print(f"REFLECT_COEF_D = {REFLECT_COEF_D}")
    print(f"SLOPE_A = {SLOPE_A}")
    print(f"SLOPE_B = {SLOPE_B}")
    print(f"SLOPE_C = {SLOPE_C}")
    print(f"SLOPE_D = {SLOPE_D}")
    print(f"INTERCEPT_A = {INTERCEPT_A}")
    print(f"INTERCEPT_B = {INTERCEPT_B}")
    print(f"INTERCEPT_C = {INTERCEPT_C}")
    print(f"INTERCEPT_D = {INTERCEPT_D}")

# 処理概要　時間軸データが格納されたテキストファイルから読み出して配列に格納
# 引数　measurement_point：測定点数
# 戻り値　時間軸データ配列（リスト型）
def Get_TimeDomainData(measurement_point :int):
    # ローカル変数の定義
    time_domain_data :float = []     # 距離軸データ格納用配列

    # ファイルの中身を読み出し
    if measurement_point == MEASUREMENT_POINT_STANDARD:
        f = open(PROJECT_HOME_DIR + "/config/time_domain_std.txt","r",encoding="utf-8")
    elif measurement_point == MEASUREMENT_POINT_DRY:
        f = open(PROJECT_HOME_DIR + "/config/time_domain_dry.txt","r",encoding="utf-8")
    data = f.readlines()
    f.close

    # 配列に格納
    time_domain_data = []
    for i in range(measurement_point):
        time_domain_data.append(float(data[i].replace("\n","")))

    return(time_domain_data)

# 処理概要　測定した波形データが格納されたファイルから読み出して配列に格納
# 引数　file_name：ファイル名
# 戻り値　測定日時、ステップ応答配列（リスト型）
def Get_ReflectionArray(file_name :str):
    # ファイルの中身を読み出し
    f = open(file_name,"r",encoding="utf-8")
    data = f.readlines()
    f.close()

    # 日時データ読み出し
    datetime_data = datetime.datetime.strptime(data[0].replace("\n",""), "%Y/%m/%d %H:%M:%S")

    # 配列に格納
    reflection_array = []
    for i in range(1,len(data),1):
        reflection_array.append(float(data[i].replace("\n","")))
    return(datetime_data,reflection_array)

# 処理概要　土壌表面からの反射波の到達時刻（ns）を取得
# 引数　time_array；時間軸データ、reflection_array：ステップ応答配列、gradient：勾配配列、measurement_point：測定点数
# 戻り値　土壌表面での反射波の到達時刻
def Detect_SoilSurfaceReflect(time_array :list[float],reflection_array :list[float],gradient :list[float],measurement_point :int):
    global TIME_STEP_RISE_SURFACE, TIME_STEP_A, TIME_STEP_B, TIME_STEP_C, TIME_STEP_D, REFLECT_COEF_A, REFLECT_COEF_B, REFLECT_COEF_C, REFLECT_COEF_D, SLOPE_A, SLOPE_B, SLOPE_C, SLOPE_D, INTERCEPT_A, INTERCEPT_B, INTERCEPT_C, INTERCEPT_D

    # ローカル変数の定義
    i :int                      #汎用カウンタ
    inflection_point :float     #変曲点計算に一時的に使う変数

	# A点を取得
    inflection_point = gradient[TIME_STEP_RISE_SURFACE - 1]
    i = TIME_STEP_RISE_SURFACE
    while inflection_point < gradient[i] and i < (measurement_point - 2):
        inflection_point = gradient[i]
        i = i + 1
    TIME_STEP_A = i
    REFLECT_COEF_A = reflection_array[i]

	# B点を取得
    inflection_point = gradient[TIME_STEP_A]
    i = TIME_STEP_A + 1
    while inflection_point > gradient[i] and i < (measurement_point - 2):
        inflection_point = gradient[i]
        i = i + 1
    TIME_STEP_B = i
    REFLECT_COEF_B = reflection_array[i]

	# A点の接線を求める
    temp_x_array = [time_array[TIME_STEP_A-1],time_array[TIME_STEP_A],time_array[TIME_STEP_A+1]]
    temp_y_array = [reflection_array[TIME_STEP_A-1],reflection_array[TIME_STEP_A],reflection_array[TIME_STEP_A+1]]
    SLOPE_A,INTERCEPT_A = np.polyfit(temp_x_array,temp_y_array,1)
    INTERCEPT_A = reflection_array[TIME_STEP_A] - SLOPE_A * time_array[TIME_STEP_A]

	# B点の接線を求める
    temp_x_array = [time_array[TIME_STEP_B-1],time_array[TIME_STEP_B],time_array[TIME_STEP_B+1]]
    temp_y_array = [reflection_array[TIME_STEP_B-1],reflection_array[TIME_STEP_B],reflection_array[TIME_STEP_B+1]]
    SLOPE_B,INTERCEPT_B = np.polyfit(temp_x_array,temp_y_array,1)
    INTERCEPT_B = reflection_array[TIME_STEP_B] - SLOPE_B * time_array[TIME_STEP_B]

    soil_surface_reflect = (INTERCEPT_B - INTERCEPT_A) / (SLOPE_A - SLOPE_B)
    return soil_surface_reflect

# 処理概要　プローブ終端からの反射波の到達時刻（ns）を取得
# 引数　time_array；時間軸データ、reflection_array：ステップ応答配列、gradient：勾配配列、measurement_point：測定点数
# 戻り値　プローブ終端での反射波の到達時刻
def Detect_ProbeEndReflect(time_array :list[float],reflection_array :list[float],gradient :list[float],measurement_point :int):
    global TIME_STEP_RISE_SURFACE, TIME_STEP_A, TIME_STEP_B, TIME_STEP_C, TIME_STEP_D, REFLECT_COEF_A, REFLECT_COEF_B, REFLECT_COEF_C, REFLECT_COEF_D, SLOPE_A, SLOPE_B, SLOPE_C, SLOPE_D, INTERCEPT_A, INTERCEPT_B, INTERCEPT_C, INTERCEPT_D

    # ローカル変数の定義
    i :int                      #汎用カウンタ
    inflection_point :float     #変曲点計算に一時的に使う変数

    # D点を取得
    inflection_point = gradient[TIME_STEP_B]
    i = TIME_STEP_B + 1
    while i < (measurement_point - 2):
        if inflection_point < gradient[i]:
            inflection_point = gradient[i]
            TIME_STEP_D = i
        i = i + 1
    REFLECT_COEF_D = reflection_array[TIME_STEP_D]

	# C点を取得
    # 起算点をA点とするのは地表面での反射とプローブ終端での反射が一体化したときにTIME_STEP_A==TIME_STEP_Cになり、異常判定できるから
    TIME_STEP_C = TIME_STEP_D
    REFLECT_COEF_C = REFLECT_COEF_D
    i = TIME_STEP_C - 1
    while i > TIME_STEP_A:
        if reflection_array[i] > REFLECT_COEF_C:
            TIME_STEP_C = i + 1
            break
        REFLECT_COEF_C = reflection_array[i]
        i = i - 1
    if i == TIME_STEP_A:
        TIME_STEP_C = TIME_STEP_A

	# C点の接線を求める
    SLOPE_C = 0
    INTERCEPT_C = reflection_array[TIME_STEP_C]

	# D点の接線を求める
    temp_x_array = [time_array[TIME_STEP_D-1],time_array[TIME_STEP_D],time_array[TIME_STEP_D+1]]
    temp_y_array = [reflection_array[TIME_STEP_D-1],reflection_array[TIME_STEP_D],reflection_array[TIME_STEP_D+1]]
    SLOPE_D,INTERCEPT_D = np.polyfit(temp_x_array,temp_y_array,1)
    INTERCEPT_D = reflection_array[TIME_STEP_D] - SLOPE_D * time_array[TIME_STEP_D]

	# 反射波の到達時刻を求める
    probe_end_reflect = (INTERCEPT_D - INTERCEPT_C) / (SLOPE_C - SLOPE_D)

    return probe_end_reflect

# 処理概要　伝搬時間tを取得
# 引数　time_array；時間軸データ、reflection_array：ステップ応答配列、measurement_point：測定点数
# 戻り値　測定成否、土壌表面からの反射波の到達時刻、プローブ終端からの反射波の到達時刻、伝搬時間(ns)、伝搬時間計算成否
def Get_t(time_array :list[float],reflection_array :list[float],measurement_point :int):
    global TIME_STEP_RISE_SURFACE, TIME_STEP_A, TIME_STEP_B, TIME_STEP_C, TIME_STEP_D, REFLECT_COEF_A, REFLECT_COEF_B, REFLECT_COEF_C, REFLECT_COEF_D, SLOPE_A, SLOPE_B, SLOPE_C, SLOPE_D, INTERCEPT_A, INTERCEPT_B, INTERCEPT_C, INTERCEPT_D

    # ローカル変数の定義
    i :int                  # 汎用カウンタ
    j :int                  # 汎用カウンタ
    time_step :int          # タイムステップ
    t_calc_result :int      # 伝搬時間の計算成否

    # 定数の定義
    gradient_data_num = measurement_point - 2

    # 反射係数の勾配を求める
    i = 1
    j = 0
    gradient = []
    while i <= gradient_data_num:
        # 中心差分法で使用するデータを配列に格納
        temp_x_array = [time_array[i-1],time_array[i],time_array[i+1]]
        temp_y_array = [reflection_array[i-1],reflection_array[i],reflection_array[i+1]]
        # 接線勾配を求める
        a,b = np.polyfit(temp_x_array,temp_y_array,1)
        gradient.append(a)
        # カウンタインクリメント
        i = i + 1
        j = j + 1

    # 反射係数が0付近でふらつく最初の部分をスキップするために反射係数が閾値以上になるまでタイムステップを進める
    time_step = 1       #0から初めていきなり閾値超えるとA点導出時に勾配配列インデックスがマイナスになって都合が悪いため
    while True:
        if reflection_array[time_step] > THRESHOLD_REFLECT_COEF:
            break

	    # ケーブル未接続など、ずっと0付近のまま終端まで言った場合も異常値とする
        if time_step == measurement_point - 1:
            # 測定された比誘電率に疑義があるとして処理を終了
            t_calc_result = T_DOUBT
            return 0,0,0,t_calc_result
        # カウンタインクリメント
        time_step = time_step + 1

    # 地表面での反射波の立ち上がりはじめを格納
    TIME_STEP_RISE_SURFACE = time_step

    # 土壌表面からの反射波の到達時刻を取得
    soil_surface_reflect = Detect_SoilSurfaceReflect(time_array,reflection_array,gradient,measurement_point)

    # プローブ終端からの反射波の到達時刻を取得
    probe_end_reflect = Detect_ProbeEndReflect(time_array,reflection_array,gradient,measurement_point)

    # B点の反射係数が閾値以上の場合は地表面での反射とプローブ終端での反射が一体化しているとみなす
    if system_data.THRESHOLD_VALLEY <= REFLECT_COEF_B:
        t_calc_result = T_DOUBT
        return 0,0,0,t_calc_result

    # A点以降で反射係数が最小の時のタイムステップがA点のそれと等しい場合は地表面での反射とプローブ終端での反射が一体化しているとみなす
    if TIME_STEP_A == TIME_STEP_C:
        t_calc_result = T_DOUBT
        return 0,0,0,t_calc_result

    # 伝搬時間tを計算
    t = probe_end_reflect - soil_surface_reflect
    t_calc_result = T_OK

    return soil_surface_reflect,probe_end_reflect,t,t_calc_result

# 処理概要　比誘電率を計算
# 引数　なし
# 戻り値　なし
def Calc_RelativeDielectricConstant():
    # ローカル変数の定義
    t_calc_result :int                  # 比誘電率の計算成否
    t :float                            # 伝搬時間（ns）
    er :float                           # 比誘電率（-）
    measurement_point :int              # 測定点数
    rdc_calc_result :int = RDC_DOUBT    # 比誘電率の計算成否
    adopted_measurement_point :int      # 比誘電率の計算に使用したデータの測定点数

    # 波形データ一覧を取得
    files = sorted(glob.glob(PROJECT_HOME_DIR + "/raw_data/*_std.txt"))

    # 時間軸データ一覧を取得（101点（通常）と51点（乾燥域用））
    time_domain_std = Get_TimeDomainData(MEASUREMENT_POINT_STANDARD)
    time_domain_dry = Get_TimeDomainData(MEASUREMENT_POINT_DRY)

    rdc_data_array = []
    for i in range(len(files)):
        # 波形データ一覧を取得（101点（通常）と51点（乾燥域用））
        datetime_data,reflection_array_std = Get_ReflectionArray(files[i])
        datetime_data,reflection_array_dry = Get_ReflectionArray(files[i].replace("_std.txt","_dry.txt"))

        # 101点（通常）のデータをつかって伝搬時間tを計算
        measurement_point = MEASUREMENT_POINT_STANDARD
        soil_surface_reflect,probe_end_reflect,t,t_calc_result = Get_t(time_domain_std,reflection_array_std,measurement_point)

        #print(files[i])
        #debug()

        # 101点（通常）で伝搬時間を正しく計算できた場合は比誘電率を計算する
        if t_calc_result == T_OK:
            rdc_calc_result = RDC_OK
            adopted_measurement_point = measurement_point

        #伝搬時間を正しく計算できてない可能性があれば51点（乾燥域用）のデータを使う
        else:
            # 51点（乾燥域用）のデータをつかって伝搬時間tを計算
            measurement_point = MEASUREMENT_POINT_DRY
            soil_surface_reflect,probe_end_reflect,t,t_calc_result = Get_t(time_domain_dry,reflection_array_dry,measurement_point)
            adopted_measurement_point = measurement_point

            #print(files[i].replace("_std.txt","_dry.txt"))
            #debug()

            # 51点（乾燥域用）で伝搬時間を正しく計算できた場合は比誘電率を計算する
            if t_calc_result == T_OK:
                rdc_calc_result = RDC_OK

        # 比誘電率を計算
        if rdc_calc_result == RDC_DOUBT:
            rdc_data_array.append([str(datetime_data),"#N/A","#N/A","#N/A",str(adopted_measurement_point)])
        else:
            er = ((C_SPEED * t * (10 ** (-9))) / (2 * PROBE_LENGTH)) ** 2
            rdc_data_array.append([ \
                str(datetime_data), \
                str(int(soil_surface_reflect * 100000 + 0.5) / 100000), \
                str(int(probe_end_reflect * 100000 + 0.5) / 100000), \
                str(int(er * 100000 + 0.5) / 100000), \
                str(adopted_measurement_point)])

    # テキストファイルに書き出し
    f = open(PROJECT_HOME_DIR + "/relative_dielectric_constant_data/result.txt","w",encoding="utf-8")
    print("Relative dielectric donstant data has saved as result.csv in directory 'relative_dielectric_constant_data'.")
    print("data:")
    print(" yyyy-mm-dd hh:mm:ss,        t1,        t2,        er,  point")
    print("-------------------------------------------------------------")
    f.write("datetime,reflect time at soil surface(ns),reflect time at probe end(ns),relative dielectrice constant(-),measurement point\n")
    for i in range(len(rdc_data_array)):
        f.write(f"{rdc_data_array[i][0]},{rdc_data_array[i][1]},{rdc_data_array[i][2]},{rdc_data_array[i][3]},{rdc_data_array[i][4]}\n")
        print(f"{rdc_data_array[i][0]:>20},{rdc_data_array[i][1]:>10},{rdc_data_array[i][2]:>10},{rdc_data_array[i][3]:>10},{rdc_data_array[i][4]:>7}")
    f.close()
    print("-------------------------------------------------------------")
    print("                           t1:time at soil surface reflect   ")
    print("                           t2:time at probe end reflect      ")
    print("                           er:relative dielectric constant   ")
    print("                           point:measurement point to calc er\n")

if __name__ == '__main__':
    Calc_RelativeDielectricConstant()
