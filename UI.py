import sys
import os.path
import base64
from email import message_from_bytes
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QLabel, QPushButton, QTextEdit, QLineEdit,
    QSplitter, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import html2text

class GmailUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gmail Client")
        self.resize(1200, 800)
        self.init_ui()
        self.load_emails()

    def init_ui(self):
        # 메인 레이아웃
        main_layout = QHBoxLayout()
        
        # 왼쪽 사이드바
        sidebar = QFrame()
        sidebar.setMaximumWidth(200)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #f6f8fc;
                border-right: 1px solid #e0e0e0;
            }
        """)
        sidebar_layout = QVBoxLayout()

        # 메뉴 항목들
        menu_items = ["common", "Security", "Spam", "Trash"]
        for item in menu_items:
            btn = QPushButton(item)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 8px 16px;
                    border: none;
                    color: #202124;
                }
                QPushButton:hover {
                    background-color: #e8eaed;
                    border-radius: 0 16px 16px 0;
                }
            """)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        sidebar.setLayout(sidebar_layout)
        
        # 중앙 영역
        center_widget = QWidget()
        center_layout = QVBoxLayout()
        
        # 검색 바
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search mail")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 16px;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: #f1f3f4;
            }
        """)
        search_layout.addWidget(self.search_input)
        center_layout.addLayout(search_layout)
        
        # 이메일 리스트와 상세 보기 영역
        content_splitter = QSplitter(Qt.Horizontal)
        
        # 이메일 리스트
        self.email_list = QListWidget()
        self.email_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f1f3f4;
            }
            QListWidget::item:selected {
                background-color: #f1f3f4;
            }
        """)
        
        # 이메일 상세 보기
        self.email_detail = QTextEdit()
        self.email_detail.setReadOnly(True)
        self.email_detail.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: white;
                padding: 16px;
            }
        """)
        
        content_splitter.addWidget(self.email_list)
        content_splitter.addWidget(self.email_detail)
        content_splitter.setSizes([400, 600])
        
        center_layout.addWidget(content_splitter)
        center_widget.setLayout(center_layout)
        
        # 레이아웃 조립
        main_layout.addWidget(sidebar)
        main_layout.addWidget(center_widget)
        self.setLayout(main_layout)
        
        # 이벤트 연결
        self.email_list.itemClicked.connect(self.show_email_detail)

    def load_emails(self):
        """이메일 목록 로드
        try:
            results = self.gmail_service.users().messages().list(
                userId='me', maxResults=20).execute()
            messages = results.get('messages', [])
            
            self.email_list.clear()
            for message in messages:
                msg = self.gmail_service.users().messages().get(
                    userId='me', id=message['id']).execute()
                
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
                # 이메일 아이템 생성
                item_text = f"{sender}\n{subject}\n{date}"
                self.email_list.addItem(item_text)
                
        except Exception as e:
            print(f"Error loading emails: {str(e)}")
        """
    def show_email_detail(self, item):
        """이메일 상세 내용 표시"""
        try:
            # 선택된 이메일의 인덱스
            index = self.email_list.row(item)
            
            # 해당 이메일의 전체 내용 가져오기
            results = self.gmail_service.users().messages().list(
                userId='me', maxResults=20).execute()
            messages = results.get('messages', [])
            msg = self.gmail_service.users().messages().get(
                userId='me', id=messages[index]['id']).execute()
            
            # 이메일 본문 추출
            if 'parts' in msg['payload']:
                parts = msg['payload']['parts']
                body = ''
                for part in parts:
                    if part['mimeType'] == 'text/html':
                        body = base64.urlsafe_b64decode(
                            part['body']['data']).decode('utf-8')
                        break
                    elif part['mimeType'] == 'text/plain':
                        body = base64.urlsafe_b64decode(
                            part['body']['data']).decode('utf-8')
            else:
                body = base64.urlsafe_b64decode(
                    msg['payload']['body']['data']).decode('utf-8')
            
            # HTML을 텍스트로 변환
            h = html2text.HTML2Text()
            h.ignore_links = False
            body = h.handle(body)
            
            # 이메일 상세 정보 표시
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            detail_text = f"""
            <div style='font-family: Arial, sans-serif;'>
                <h2>{subject}</h2>
                <div style='color: #666; margin-bottom: 20px;'>
                    <p><strong>From:</strong> {sender}</p>
                    <p><strong>Date:</strong> {date}</p>
                </div>
                <div style='line-height: 1.6;'>
                    {body}
                </div>
            </div>
            """
            
            self.email_detail.setHtml(detail_text)
            
        except Exception as e:
            print(f"Error showing email detail: {str(e)}")

    def compose_email(self):
        """새 이메일 작성"""
        # TODO: 이메일 작성 기능 구현
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GmailUI()
    window.show()
    sys.exit(app.exec_())