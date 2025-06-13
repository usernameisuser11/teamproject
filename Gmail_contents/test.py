SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import os.path
import base64
import pymysql

conn = pymysql.connect(
        host='34.171.166.56',       # 서버 IP
        user='root',            # MySQL 사용자 이름
        password='#Publicwook1134',  # 비밀번호
        database='users',
        charset='utf8mb4',      # 한글 저장 가능하게
        port = 3306,
        cursorclass=pymysql.cursors.DictCursor  # 결과를 딕셔너리로 받기
    )
number_of_mails = 50

class GmailReader:
    def __init__(self):
        # Gmail API 접근 권한 설정
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        self.creds = None
        self.service = None
    

    def save_token_to_db(self, id):
        cursor = conn.cursor()
        token_blob = pickle.dumps(self.creds)  # creds → bytes
        # 기존 토큰 있으면 UPDATE, 없으면 INSERT
        cursor.execute("SELECT id FROM user WHERE id=%s",(id,))
        if cursor.fetchone():
            cursor.execute("UPDATE user SET AccessToken=%s WHERE id=%s", (token_blob,id))
        else:
            cursor.execute("UPDATE user SET AccessToken=%s WHERE id=%s", (token_blob, id))
        conn.commit()
        cursor.close()

    def load_token_from_db(self, id):
        cursor = conn.cursor()
        cursor.execute("SELECT AccessToken FROM user WHERE id=%s",id)
        result = cursor.fetchone()
        cursor.close()
        if result and result['AccessToken']:
            return pickle.loads(result['AccessToken'])  # bytes → creds\
        else :
            print(f"[INFO] Token not found for id {id}. Starting authentication.")
            return None

    def authenticate(self, updatedID):
        """Gmail API 인증 처리 (DB 사용)"""
        self.creds = self.load_token_from_db(id=updatedID)

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
            self.save_token_to_db(id=updatedID)

        self.service = build('gmail', 'v1', credentials=self.creds)

    
    def get_emails(self,gotID, max_results=number_of_mails):
        """Gmail에서 이메일 가져오기"""
        # 인증이 안 되어 있다면 인증 진행
        if not self.service:
            self.authenticate(updatedID=gotID)
        
        # 이메일 목록 가져오기
        results = self.service.users().messages().list(
            userId='me', maxResults=max_results).execute()
        messages = results.get('messages', [])
        
        emails = []
        for message in messages:
            # 각 이메일의 상세 정보 가져오기
            msg = self.service.users().messages().get(
                userId='me', id=message['id']).execute()
            
            # 이메일 헤더에서 정보 추출
            headers = msg['payload']['headers']
            subject = next(h['value'] for h in headers if h['name'] == 'Subject')
            sender = next(h['value'] for h in headers if h['name'] == 'From')
            date = next(h['value'] for h in headers if h['name'] == 'Date')
            
            # 이메일 본문 추출 (멀티파트 메시지 처리)
            body = ''
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        body = base64.urlsafe_b64decode(
                            part['body']['data']).decode('utf-8')
                        break
            else:
                body = base64.urlsafe_b64decode(
                    msg['payload']['body']['data']).decode('utf-8')
            
            # 이메일 정보 저장
            emails.append({
                'subject': subject,
                'sender': sender,
                'body': body,
                'date': date,
                'categoryIndex':0
            })
        return emails