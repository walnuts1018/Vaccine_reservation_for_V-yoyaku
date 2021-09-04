# Vaccine_reservation_for_V-yoyaku
  新型コロナウイルスワクチン予約システム V-yoyaku (https://v-yoyaku.jp/) を自動化するプログラムです。
  とりあえず広島県において動作確認をしております。

## ■インストール
python3をインストール(テスト環境は3.8)

ライブラリをインストール

```
sudo pip install -r requirements.txt
```

## ■使用方法

### □準備
[config.json](config/config.json)に必要情報を登録します。
[account]の **** の部分に接種券番号とパスワードを入力してください。

また、動作モードや日付、会場指定の方法は [README.md](config/README.md) に書いてあります。


### □実行
reservation.pyを実行    
```
python3 reservation.py
```

これで予約が取れるといいね。 
