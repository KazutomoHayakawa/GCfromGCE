import gspread
import json

#ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成します。
from oauth2client.service_account import ServiceAccountCredentials 

#2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

#認証情報設定
#ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
credentials = ServiceAccountCredentials.from_json_keyfile_name('/.credential/client_id.json', scope)

#OAuth2の資格情報を使用してGoogle APIにログインします。
gc = gspread.authorize(credentials)


# １．ファイル名を指定してワークブックを選択
# workbook = gc.open('ファイル名')

# ２．スプレッドシートキーを指定してワークブックを選択（おすすめ）
workbook = gc.open_by_key('1qqsdubleCo2HxQagmU6jk3whBZGUAVxqbRYkOkrjQx0')

# ３．URLを指定してワークブックを選択を開く
#workbook = gc.open_by_url('URL')

#################################
# パラメータ
print(workbook.title)
print(workbook.id)
#workbook.title	#スプレッドシートのタイトルを取得する
#workbook.id		#スプレッドシートキーを取得する

