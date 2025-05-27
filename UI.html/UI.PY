import sys
import os.path
import base64
from email import message_from_bytes

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QLabel, QPushButton, QTextEdit, QLineEdit
)

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API 범위
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """Gmail API 인증"""
    creds = None
    if os.path.exists('token.json'):
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

def get_email_subjects(service, max_results=10):
    """이메일 제목만 추출"""
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = results.get('messages', [])
    subjects = []

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_data.get("payload", {}).get("headers", [])
        for h in headers:
            if h['name'] == 'Subject':
                subjects.append(h['value'])
    return subjects

class EmailClassifierUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("이메일 분류기")
        self.resize(900, 600)
        self.gmail_service = authenticate_gmail()
        self.init_ui()
        self.load_emails()

    def init_ui(self):
        # 전체 레이아웃
        layout = QVBoxLayout()

        # 상단: 검색 바 및 필터
        top_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("이메일 검색...")
        self.search_button = QPushButton("검색")
        top_layout.addWidget(self.search_input)
        top_layout.addWidget(self.search_button)

        # 중앙 레이아웃
        center_layout = QHBoxLayout()

        # 사이드바
        self.sidebar = QListWidget()
        self.sidebar.addItems(["전체 메일", "업무", "개인", "스팸"])

        # 이메일 리스트
        self.email_list = QListWidget()

        # 이메일 상세 보기
        self.email_detail = QTextEdit()
        self.email_detail.setReadOnly(True)
        self.email_detail.setText("메일 내용을 여기에 표시합니다.")

        center_layout.addWidget(self.sidebar, 1)
        center_layout.addWidget(self.email_list, 2)
        center_layout.addWidget(self.email_detail, 3)

        # 하단: 설정 및 로그아웃 버튼
        bottom_layout = QHBoxLayout()
        self.settings_button = QPushButton("설정")
        self.logout_button = QPushButton("로그아웃")
        bottom_layout.addWidget(self.settings_button)
        bottom_layout.addWidget(self.logout_button)

        # 레이아웃 조립
        layout.addLayout(top_layout)
        layout.addLayout(center_layout)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

        # 리스트 항목 클릭 시 메일 내용 보여주기
        self.email_list.itemClicked.connect(self.show_email_detail)

    def load_emails(self):
        subjects = get_email_subjects(self.gmail_service)
        self.email_list.clear()
        for subject in subjects:
            self.email_list.addItem(subject)

    def show_email_detail(self, item):
        self.email_detail.setText(f"선택한 제목: {item.text()}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EmailClassifierUI()
    window.show()
    sys.exit(app.exec_())