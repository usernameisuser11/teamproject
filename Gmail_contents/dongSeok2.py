from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import os.path
import base64

class GmailReader:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        self.creds = None
        self.service = None

    def authenticate(self):
        # 저장된 토큰 불러오기
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        # 토큰이 없거나 유효하지 않으면 새 인증
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                self.creds = flow.run_console()  # WSL에서는 콘솔 인증 사용

            # 인증 정보 저장
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        # Gmail API 서비스 생성
        self.service = build('gmail', 'v1', credentials=self.creds)

    def get_emails(self, max_results=5):
        if not self.service:
            self.authenticate()

        results = self.service.users().messages().list(userId='me', maxResults=max_results).execute()
        messages = results.get('messages', [])

        emails = []
        for message in messages:
            msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), '(No Sender)')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '(No Date)')

            # 이메일 본문 추출
            body = ''
            payload = msg['payload']
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
            elif 'body' in payload and 'data' in payload['body']:
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

            emails.append({
                'id': message['id'],
                'subject': subject,
                'sender': sender,
                'date': date,
                'body': body
            })

        return emails

# 실행 진입점
if __name__ == '__main__':
    reader = GmailReader()
    emails = reader.get_emails(max_results=5)
    for email in emails:
        print(f"Subject: {email['subject']}")
        print(f"From: {email['sender']}")
        print(f"Date: {email['date']}")
        print(f"Body Preview:\n{email['body'][:200]}...\n")
        print("=" * 60)
