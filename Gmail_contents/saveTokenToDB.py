import pymysql
import pickle
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
conn = pymysql.connect(
        host='34.171.166.56',       # 서버 IP
        user='root',            # MySQL 사용자 이름
        password='#Publicwook1134',  # 비밀번호
        database='users',
        charset='utf8mb4',      # 한글 저장 가능하게
        port = 3306,
        cursorclass=pymysql.cursors.DictCursor  # 결과를 딕셔너리로 받기
    )
class GmailReader:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        self.creds = None
        self.service = None

    def load_token_from_db(self):
        cursor = conn.cursor()
        cursor.execute("SELECT AccessToken FROM user WHERE id=1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            return pickle.loads(result[0])  # bytes → creds
        return None

    def save_token_to_db(self):
        cursor = conn.cursor()
        token_blob = pickle.dumps(self.creds)  # creds → bytes
        # 기존 토큰 있으면 UPDATE, 없으면 INSERT
        cursor.execute("SELECT id FROM user WHERE id=1")
        if cursor.fetchone():
            cursor.execute("UPDATE user SET token_data=%s WHERE id=1", (token_blob,))
        else:
            cursor.execute("INSERT INTO user (id, token_data) VALUES (1, %s)", (token_blob,))
        conn.commit()
        cursor.close()
        conn.close()

    def authenticate(self):
        """Gmail API 인증 처리 (DB 사용)"""
        self.creds = self.load_token_from_db()

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                credentials_path = os.path.join(base_dir, 'credential.json')
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, self.SCOPES)
                self.creds = flow.run_local_server(port=0)

            # 새 토큰 저장
            self.save_token_to_db()

        self.service = build('gmail', 'v1', credentials=self.creds)
