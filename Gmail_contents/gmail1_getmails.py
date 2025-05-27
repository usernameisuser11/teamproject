

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import os.path
import base64

number_of_mails = 50

class GmailReader:
    def __init__(self):
        # Gmail API 접근 권한 설정
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        self.creds = None
        self.service = None
    
    def authenticate(self):
        """Gmail API 인증 처리"""
        # 저장된 인증 정보가 있는지 확인
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        # 인증 정보가 없거나 만료된 경우
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                # 토큰 갱신
                self.creds.refresh(Request())
            else:
                # 새로운 인증 진행

                base_dir = os.path.dirname(os.path.abspath(__file__))
                credentials_path = os.path.join(base_dir, 'credential.json')
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # 인증 정보 저장
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
        
        # Gmail API 서비스 생성
        self.service = build('gmail', 'v1', credentials=self.creds)
    
    def get_emails(self, max_results=number_of_mails):
        """Gmail에서 이메일 가져오기"""
        # 인증이 안 되어 있다면 인증 진행
        if not self.service:
            self.authenticate()
        
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
