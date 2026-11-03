# 概要
NanoVNAを使ったTDR土壌水分測定システムの測定プログラムです。

# 環境
|項目|内容|
|:------|:------|
|ロガー|Raspberry Pi Zero 2 W|
|OS|Raspberry Pi OS(64-bit)|
|OS バージョン|Linux raspberrypi 6.18.50+rpt-rpi-v8 #1 SMP PREEMPT Debian 1:6.18.50-1+rpt1 (2026-09-11) aarch64 GNU/Linux|
|ライター|Raspberry Imager v1.8.5|

# 環境構築
* インターネットに接続し、再起動
```
~$ nmcli radio wifi on
~$ nmtui
~$ sudo reboot
```

* アップデート、アップグレード、再起動

```
~$ sudo apt update 
~$ sudo apt upgrade -y
~$ sudo reboot
```
* NanoVNAのファームウェア書き換え用ツールインストール

```
$ sudo apt install -y dfu-util
```
 
* プログラムのクローン

```
~$ sudo apt install git -y
~$ git clone https://github.com/ebi-gunkan/TDR_SoilMoistureSensor.git
```

* ライブラリのインストール

```
~$ sudo apt install python3-numpy python3-serial -y
```

* 再起動

```
~$ sudo reboot
```

# 使い方
### NanoVNAのファームウェア書き換え
NanoVNA本体右上のレバースイッチを押し込んだ状態でNanoVNAを投入し、ファームウェア書き込みモードで起動する。
ファームウェア書き込みモードで起動したらレバースイッチを解放する。
なお、ファームウェア書き込みモードでの起動に成功すると画面が黒いままになる。

下記コマンドでNanoVNAのファームウェアを更新する。

```
~$ cd TDR_SoilMoistureSensor
~/TDR_SoilMoistureSensor$ dfu-util -d 0483:df11 -a 0 -s 0x08000000:leave -D firmware/firmware.bin
```

### 電気的長さの決定
電気的長さの決定に用いる標準試料にプローブを入れる。
以下のコマンドを実行して標準試料のステップ応答を取得する。

```
~/TDR_SoilMoistureSensor$ sudo python3 ./ProbeElectricLength.py -measure （標準試料の名前）
```

また、以下のコマンドで電気的長さを決定する。

```
~/TDR_SoilMoistureSensor$ sudo python3 ./ProbeElectricLength.py -cal （標準試料1の名前） （標準試料1の比誘電率） （標準試料2の名前） （標準試料2の比誘電率）
```

例としてエタノールと水を使って比誘電率を決定する場合のコマンドを示す。
まず、プローブをエタノールに入れ下記コマンドを実行する。

```
~/TDR_SoilMoistureSensor$ sudo python3 ./ProbeElectricLength.py -measure ethanol
```

次に、プローブを水に入れ下記コマンドを実行する。

```
~/TDR_SoilMoistureSensor$ sudo python3 ./ProbeElectricLength.py -measure water
```

最後に、下記コマンドを実行して比誘電率を決定する。
コマンドライン引数として与えた比誘電率に関して、ここではエタノールでは試料の濃度から、水では水温から計算した。

```
~/TDR_SoilMoistureSensor$ sudo python3 ./ProbeElectricLength.py -calc ethanol 25.17 water 82.46
```

### 電気的長さをユーザーパラメータファイルに反映
~/TDR_SoilMoistureSensor/config/user_data.pyにある電気的長さを表す変数「PROBE_ELECTRIC_LENGTH」に求めた電気的長さ（mm）を記入する。

```
PROBE_ELECTRIC_LENGTH :float = 0.119    #プローブのロッド部の電気的長さ（m）
```

### ステップ応答の定時測定
コマンド実行直後にステップ応答を取得し、それ以降は正時にステップ応答を取得する。
取得したステップ応答は~/TDR_SoilMoistureSensor/raw_dataに格納される。
```
~/TDR_SoilMoistureSensor$ sudo python3 ./Execute_Measurement.py
```

### ステップ応答を比誘電率に変換
コマンド実行後に比誘電率をステップ応答に変換する。
変換結果は~/TDR_SoilMoistureSensor/relative_dielectric_constantに格納される。

```
~/TDR_SoilMoistureSensor$ sudo python3 ./Convert_StepResponse2RelativeDielectricConstant.py
```
