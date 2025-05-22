from pathlib import Path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient import errors
from email.message import EmailMessage
import base64


""" 1. gmail 사용자 인증 """
def gmail_authenticate():
	SCOPES = ['https://mail.google.com/']
	creds = None
	if Path('token.json').is_file():
		creds = Credentials.from_authorized_user_file('token.json', SCOPES)
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
			creds = flow.run_local_server(port=0)
		with open('token.json', 'w') as token:
			token.write(creds.to_json())
	return build('gmail', 'v1', credentials=creds)


"""2. 메시지 생성"""
def create_message(받는사람이메일, 제목, 본문, 첨부파일리스트=None):
	message = EmailMessage()
	message["From"] = 보내는사람이메일
	message["To"] = 받는사람이메일.split(",")
	message["Subject"] = 제목
	message.set_content(본문)
	# message.set_content(본문, subtype='html') # html 형식으로 보내려면 subtype 지정
	
	# 파일 첨부 (하위 디렉토리 files 내에 첨부파일 준비)
	if 첨부파일리스트:
		for 파일명 in 첨부파일리스트:
			파일명 = Path(파일명).name
			with open("files/"+파일명, "rb") as f:
				message.add_attachment(f.read(), maintype="application", subtype="octet-stream", filename=파일명)
		
	return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf8')}


"""3. 메시지 발송"""
def send_message(service, user_id, message):
	try:
		message = service.users().messages().send(userId=user_id, body=message).execute()
		# print(message['id'])
		return message
	except errors.HttpError as error:
		print(error)


"""main"""
def main():
	service = gmail_authenticate()
	#message = create_message("받는사람이메일", "제목", "본문")
	#send_message(service, "me", message)
	

if __name__ == '__main__':
	main()