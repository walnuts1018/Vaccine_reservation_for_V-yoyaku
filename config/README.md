# config.json 記述方法

## headless

ブラウザを非表示状態で実行する場合は```true```を、表示状態で実行する場合は```false```を記述してください。

```json
"headless":true,
```

## url

ログインページのURLを記述してください。

```json
"url":"https://v-yoyaku.jp/341002-hiroshima",
```

## timeout

Webページの情報を取得する処理のタイムアウト時間(秒)を記述してください。  

```json
"timeout":10,
```

## account

アカウント情報を記述してください。

| key | 説明 |
| --- | --- |
| number  | 接種券番号 |
| pass    | パスワード |

```json
"account":{
    "number":"**********",
    "pass":"****"
},
```

## mode

以下```mode```のいずれかを記述してください。   
尚、```mode```によって ```予約可能な接種会場のみを対象とします。```のチェック状態を変えて検索します。(```チェック```列参照)

| mode | 説明 | チェック |
| --- | --- | --- | 
| 0 | ブラウザ起動->ログイン->検索->ブラウザ終了 を繰り返すモード<br>自動で00:00と一時間ごとに予約処理が行われる<br> | なし |
| 1 | 空きのある会場が出てくるのを待ち続けるモード(予約開放タイミングを狙う使い方を想定) | あり |
| 2 | 特定の会場に空きが出てくるのを待ち続けるモード(キャンセル待ちを狙う使い方を想定) | なし |

```json
"mode":0,
```

## interval

繰り返し処理の実行間隔(秒)を記述してください。  
```mode```の値によって意味が異なります。

| mode | 説明 |
| --- | --- |
| 1 | 会場を検索する処理の実行間隔 |
| 2 | カレンダーを確認する処理の実行間隔 |

```json
"interval":60,
```

## limit

繰り返し処理の上限回数を記述してください。  
```mode```の値によって意味が異なります。

| mode | 説明 |
| --- | --- |
| 1 | 会場を検索する処理の繰り返し回数 |
| 2 | カレンダーを確認する処理の繰り返し回数 |

```json
"limit":100,
```

## medical

選択したい会場の情報をリスト形式記述してください。  
```mode```の値が```1```の場合は0番目の要素のみに対して検索処理を実行し、```index```は```0```固定となります。

| key | 説明 |
| --- | --- |
| name | ```接種会場名```に入力する検索キーワード |
| index | ```条件に該当する接種会場```に出力される会場の内、何番目(0始まり)のラジオボタンを選択するかを記述<br> 例:2ページ目の上から3番目 ⇒ 12 |

```json
"medical":[
    {"name":"集団接種会場A","index":0},
    {"name":"集団接種会場B","index":0}
],
```

## date

予約したい日程の候補を記述してください。  

| key | 説明 |
| --- | --- |
| year | 予約したい年 |
| date_list | 例:9/10 -> 0910<br>リスト型で記述<br>```limit```を超える日は無視される<br>未定義の場合は実行した日から```limit```までのすべての日程が候補となる(未実装)|
| time_list | 例:18:30 -> 1830<br>リスト型で記述<br>未定義の場合はすべての時間帯が候補となる(未実装) |
| limit | 何日先までの日を予約対象とするかを記述 |

```json
"date":{
    "year":"2021",
    "date_list":["0910","0913"],
    "time_list":["1830","1845"],
    "limit":20
}
```

