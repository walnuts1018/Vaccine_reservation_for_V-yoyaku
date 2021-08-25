# Vaccine_reservation_for_Hiroshima
  広島の新型コロナウイルスワクチン予約システム(https://v-yoyaku.jp/341002-hiroshima )を自動化するプログラムです。
  
## ■インストール
python3をインストール(テスト環境は3.8)

seleniumをインストール

```
sudo apt install python3-selenium
```

## ■使用方法

### □準備
config.jsonに必要情報を登録します。
[ID]の **** の部分に接種券番号とパスワードを入力してください。

また、日付や会場指定の方法は [date][$comment] に書いてあります。

__バグにより[place]は一つしか書けません__ ~~誰か直しといて~~

__あと[mode]も__  ~~実装がめんどくさくて~~ __意味をなしていませんずっと0モードのままです__


    
### □実行
reservation.pyを実行    
```
python3 reservation.py
```

自動で00:00と一時間ごとに予約処理が行われます
一回目の予約が取れたらプログラムが停止します。
それまでは無限ループします。

これで予約が取れるといいね。 
