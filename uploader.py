import httplib2
import os
import sys
import time
import glob

from   apiclient      import discovery
import oauth2client
from   oauth2client   import client
from   oauth2client   import tools
from   apiclient.http import MediaFileUpload

CREDENTIAL_DIR     = os.path.join(os.path.expanduser('~'), '.credentials')
CLIENT_SECRET_FILE = os.path.join(CREDENTIAL_DIR, 'client_secret.json')
CREDENTIAL_PATH    = os.path.join(CREDENTIAL_DIR, 'piwikReport.json')
APPLICATION_NAME   = 'piwikReport'
SCOPES             = 'https://www.googleapis.com/auth/drive'

# アップロードしたいCSVファイルを保管しているフォルダまでのパスを定義
FILE_DIR = 'out/'

# ファイルを保管しておきたいGoogle Drive上のフォルダのID等を定義
# 詳しくは下でまとめて説明
FOLDER_ID        = '<Your Folder ID>'
MASTER_FILE_ID   = '<Your Master FIle ID>'
MASTER_FOLDER_ID = '<Your Master Folder ID>'

class DriveUploader(object):
    def __init__(self):
        """
        既にダウンロードして保存してある認証情報を使用して認証
        """
        self.credentials = self.get_credentials()
        self.http        = self.credentials.authorize(httplib2.Http())
        self.service     = discovery.build('drive', 'v3', http=self.http)

    def get_credentials(self):
        """
        既にAPI認証が済んでいないかどうか確認
        """
        if not os.path.exists(CREDENTIAL_DIR):
            os.makedirs(CREDENTIAL_DIR)

        store = oauth2client.file.Storage(CREDENTIAL_PATH)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flags = tools.argparser.parse_args(args=[])
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:
                # Python2.6を使用しているユーザーのための記述
                credentials = tools.run(flow, store)
            print('Storing credentials to' + CREDENTIAL_PATH)
        return credentials

    def upload_csvs(self):
        """
        実際にファイルをアップロードするメソッド
        指定フォルダに入っている"~~.csv"という名前のファイルを全てアップロードする
        """
        # アップロードするファイルを検索
        file_path = os.path.join(FILE_DIR, '*.csv')
        files     = glob.glob(file_path)
        if not files:
            print('No files to upload.')
            sys.exit()

        # 該当のファイル全てに対しファイル名を変更してアップロードするタスクを繰り返す
        counter = 1
        for a_file in files:
            # ファイルの名前を"MMDD_FileName"というフォーマットに変換
            file_name = time.strftime('%m%d') + a_file.replace('out/','_').replace('.csv','')
            print('>>>\nUploading[' + str(counter) + '/' + str(len(files)) + ']: ' + file_name)

            # アップロードする先を確定
            file_metadata = {
                'name'     : file_name,
                'mimeType' : 'application/vnd.google-apps.spreadsheet',
                'parents'  : [FOLDER_ID]
            }

            # 既に定義済みのGoogle Driveフォルダへスプレッドシートの形式に変換したCSVデータをアップロード
            media   = MediaFileUpload(a_file, mimetype='text/csv', resumable=True)
            file    = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            file_id = file.get('id')

            print('Successfully uploaded as:\nhttps://docs.google.com/spreadsheets/d/' + file_id)
            counter += 1

        # 結果を出力
        print('--------------\nTotal: '+ str(counter - 1) + ' Files Uploaded')

    def copy_master(self):
        """
        アップロードと同時にGoogle Drive上でコピーしておきたい日報等マスターファイルをコピー
        マスターファイルは既に定数として冒頭で定義してある通り
        """
        master_file_metadata = {
            'name'    : (time.strftime('%m%d') + '_PiwikReport'),
            'parents' : [MASTER_FOLDER_ID]
        }
        master_file = self.service.files().copy(fileId=MASTER_FILE_ID, body=master_file_metadata, fields='id, name').execute()
        print('Successfully created as: ' + master_file.get('name') + '\nhttps://docs.google.com/spreadsheets/d/' + master_file.get('id'))

# 本スクリプトをターミナルから [python3 uploader.py] というコマンドで実行するための記述
if __name__ == "__main__":
    DriveUploader().copy_master()