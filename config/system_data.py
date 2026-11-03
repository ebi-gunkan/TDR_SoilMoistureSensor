# -*- coding: utf-8 -*-

# ライブラリのインポート
import os
import sys

# NanoVNA
START_FREQ :int = 50000        			# NanoVNAのSTART周波数:50kHz
STOP_FREQ :int	= 1000000000    		# NanoVNAのSTOP周波数:1GHz
RECALL_NO :int = 0              		# NanoVNAのキャリブレーションデータ番号：0
BAUDRATE :int = 57600					# NanoVNAとの通信におけるボーレート
DEV_NAME :str = '/dev/ttyACM0'			# ロガー（ラズパイ）で認識されるNanoVNAのデバイス名
MEASUREMENT_POINT_STANDARD :int= 101	# 測定点数（通常の土壌水分域）
MEASUREMENT_POINT_DRY :int = 51			# 測定点数（極乾燥域）
NANOVNA_READ_OK :int = 0                # NanoVNAからのデータ読み出し成功
NANOVNA_READ_NG :int = 1                # NanoVNAからのデータ読み出し失敗
NANOVNA_INVALID_VALUE :float = 99       # NanoVNAの測定値以上を示すデータ

# 比誘電率の計算
T_DOUBT :int = 1						# 測定された伝搬時間に疑義がある場合
T_OK :int = 0							# 測定された伝搬時間に疑義がない場合
RDC_DOUBT :int = 1						# 測定された比誘電率に疑義がある場合
RDC_OK :int = 0							# 測定された比誘電率に疑義がない場合
C_SPEED :int = 299792458 				# 光速（m/s）
THRESHOLD_VALLEY :float = 0.75          # 地表面での反射とプローブ終端での反射が一体化を判断するための閾値：反射係数の谷の値
THRESHOLD_REFLLECT_COEF :float = 0.01   # 反射係数が0付近でふらつく最初の部分をスキップするための閾値
VELOCITY_FACTOR :float = 1.00           # 速度係数（-）
D_DOUBT :int = 1						# 測定された伝搬距離に疑義がある場合
D_OK :int = 0							# 測定された伝搬距離に疑義がない場合

# 信号処理
FFT_SIZE_STANDARD = 512                 # FFTサイズ（通常の土壌水分域）
FFT_SIZE_DRY = 256                       # FFTサイズ（乾燥域）

if __name__ == '__main__':
    print(PROJECT_HOME_DIR)
    pass
