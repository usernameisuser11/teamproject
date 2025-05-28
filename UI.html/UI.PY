import sys
import os.path
import base64
from email import message_from_bytes, policy

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QLabel, QPushButton, QTextEdit, QLineEdit,
    QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail API 범위
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """Gmail API 인증"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing access token...")
            creds.refresh(Request())
        else:
            print("Authorizing new credentials...")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_email_list_data(service, max_results=10):
    """
    이메일 목록에 표시할 정보 (ID, From, Subject, Snippet) 추출
    메일 10개만 가져오도록 설정
    """
    email_data_list = []
    try:
        results = service.users().messages().list(userId='me', maxResults=max_results).execute()
        messages = results.get('messages', [])

        if not messages:
            print("No messages found.")
            return []

        print(f"Fetching {len(messages)} email metadata...")
        for msg_id_info in messages:
            try:
                # 'metadata' 형식으로 메시지 헤더와 스니펫만 가져옴
                msg_full_data = service.users().messages().get(
                    userId='me', id=msg_id_info['id'], format='metadata'
                ).execute()

                headers = msg_full_data.get("payload", {}).get("headers", [])
                
                subject = "제목 없음"
                sender = "보낸 사람 없음"
                
                for h in headers:
                    if h['name'] == 'Subject':
                        subject = h['value']
                    elif h['name'] == 'From':
                        sender = h['value']
                
                snippet = msg_full_data.get('snippet', '')

                email_data_list.append({
                    'id': msg_id_info['id'],
                    'from': sender,
                    'subject': subject,
                    'snippet': snippet
                })
            except HttpError as error:
                print(f"An error occurred while fetching message {msg_id_info['id']}: {error}")
            except Exception as e:
                print(f"An unexpected error occurred for message {msg_id_info['id']}: {e}")

    except HttpError as error:
        print(f"An error occurred while listing messages: {error}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
    return email_data_list

def get_email_body(service, message_id):
    """지정된 ID의 이메일 전체 내용을 가져와 파싱"""
    try:
        # 'full' 형식으로 전체 메시지 내용 가져옴
        msg_raw_data = service.users().messages().get(
            userId='me', id=message_id, format='full'
        ).execute()

        # base64 디코딩 및 MIME 파싱
        msg_payload = msg_raw_data.get("payload")
        
        # message_from_bytes에 bytes 타입이 필요
        raw_message_bytes = base64.urlsafe_b64decode(msg_raw_data['raw'])
        msg = message_from_bytes(raw_message_bytes, policy=policy.default)

        # HTML 또는 일반 텍스트 내용 추출
        html_content = None
        plain_content = None

        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get('Content-Disposition'))

                # 첨부파일이 아니고 텍스트 파트인 경우
                if 'attachment' not in cdispo:
                    if ctype == 'text/plain':
                        plain_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    elif ctype == 'text/html':
                        html_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else: # 단일 파트 메시지
            ctype = msg.get_content_type()
            if ctype == 'text/plain':
                plain_content = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            elif ctype == 'text/html':
                html_content = msg.get_payload(decode=True).decode('utf-8', errors='ignore')

        # HTML 내용이 있으면 HTML을, 없으면 일반 텍스트를 반환
        return html_content if html_content else plain_content

    except HttpError as error:
        print(f"An error occurred while fetching message body {message_id}: {error}")
        return f"메일 내용을 가져오는 중 오류가 발생했습니다: {error}"
    except Exception as e:
        print(f"An unexpected error occurred while parsing message body {message_id}: {e}")
        return f"메일 내용을 파싱하는 중 오류가 발생했습니다: {e}"

class EmailClassifierUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gmail 클라이언트 (PyQt)")
        self.resize(1200, 750) # 창 크기 확장
        self.gmail_service = None
        
        # 인증은 UI 로딩 후 백그라운드에서 진행하거나, 별도 로딩 화면에서 처리하는 것이 좋음
        # 일단은 여기서 호출하여 시작 시 인증 프롬프트가 뜨도록 함
        try:
            self.gmail_service = authenticate_gmail()
        except Exception as e:
            print(f"인증 중 오류 발생: {e}")
            self.email_detail.setText("인증에 실패했습니다. credentials.json 파일을 확인해주세요.")
            # 앱 종료 또는 재시도 버튼 추가 고려
            return

        self.init_ui()
        self.load_emails()

    def init_ui(self):
        # Google Mail 스타일 QSS (Qt Style Sheet)
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', 'Roboto', sans-serif;
                font-size: 14px;
                color: #3C4043; /* Google Dark Grey */
            }
            #main_widget {
                background-color: #F6F6F6; /* Light grey background */
            }
            /* Top Search Bar */
            #search_bar {
                background-color: #FFFFFF;
                border-radius: 8px;
                padding: 5px 10px;
                border: 1px solid #DADCE0; /* Light border */
                margin: 8px 16px;
            }
            QLineEdit {
                border: none;
                padding: 5px;
            }
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #DADCE0;
                border-radius: 4px;
                padding: 8px 15px;
                min-width: 80px;
                color: #3C4043;
                margin-left: 5px; /* Spacing for search button */
            }
            QPushButton:hover {
                background-color: #F8F9FA;
            }
            QPushButton:pressed {
                background-color: #E8EAED;
            }
            /* Compose Button */
            #compose_button {
                background-color: #D3E3FD; /* Google Blue Light */
                color: #1A73E8; /* Google Blue */
                font-weight: bold;
                border: none;
                border-radius: 24px; /* Pill shape */
                padding: 12px 24px;
                text-align: left;
                margin: 16px;
                min-height: 48px;
                min-width: 130px;
            }
            #compose_button:hover {
                background-color: #C2DAF8;
            }
            /* Sidebar */
            QListWidget#sidebar {
                background-color: #F6F6F6;
                border: none;
                padding: 8px 0;
            }
            QListWidget#sidebar::item {
                height: 36px;
                padding-left: 16px;
            }
            QListWidget#sidebar::item:selected {
                background-color: #E8EAED; /* Light grey selected */
                color: #1A73E8; /* Google Blue text */
                border-radius: 0 18px 18px 0; /* Rounded right edge */
                font-weight: bold;
            }
            QListWidget#sidebar::item:hover:!selected {
                background-color: #E8EAED; /* Light grey on hover */
            }
            /* Email List */
            QListWidget#email_list {
                background-color: #FFFFFF;
                border: none;
                border-left: 1px solid #DADCE0;
                border-right: 1px solid #DADCE0;
            }
            QListWidget#email_list::item {
                padding: 10px 16px;
                border-bottom: 1px solid #E8EAED; /* Thin separator */
                min-height: 70px; /* Space for from, subject, snippet */
            }
            QListWidget#email_list::item:hover {
                background-color: #F6F6F6;
            }
            QListWidget#email_list::item:selected {
                background-color: #D3E3FD; /* Light blue selected */
                color: #3C4043;
            }
            /* Email Detail */
            QTextEdit#email_detail {
                background-color: #FFFFFF;
                border: none;
                padding: 20px;
            }
            QLabel#detail_from_label, QLabel#detail_subject_label {
                font-size: 16px;
                font-weight: bold;
                padding: 10px 20px 0px 20px;
            }
            QLabel#detail_subject_label {
                font-size: 22px;
                padding-bottom: 10px;
            }
            QScrollArea {
                border: none;
            }
        """)

        # 전체 레이아웃 (수평 분할: 사이드바 | 메인 콘텐츠 영역)
        main_h_layout = QHBoxLayout()
        main_h_layout.setContentsMargins(0, 0, 0, 0) # 전체 마진 제거
        main_h_layout.setSpacing(0) # 위젯 간격 제거

        # --- 좌측 사이드바 ---
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        self.compose_button = QPushButton("  편지쓰기") # 아이콘 자리 확보
        self.compose_button.setObjectName("compose_button")
        # 실제 구글 메일 아이콘처럼 꾸미려면 QIcon 사용 필요
        # self.compose_button.setIcon(QIcon('path/to/compose_icon.png')) 
        sidebar_layout.addWidget(self.compose_button)
        sidebar_layout.addSpacing(10)

        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.addItems(["  받은편지함", "  별표편지함", "  전체 메일", "  보낸편지함", "  임시보관함", "  스팸", "  휴지통"])
        self.sidebar.setCurrentRow(0) # 기본 선택: 받은편지함
        sidebar_layout.addWidget(self.sidebar)
        
        # 하단 공간 채우기
        sidebar_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # --- 메인 콘텐츠 영역 (상단 검색바 | 메일 목록 | 메일 상세) ---
        main_content_v_layout = QVBoxLayout()
        main_content_v_layout.setContentsMargins(0, 0, 0, 0)
        main_content_v_layout.setSpacing(0)

        # 상단: 검색 바 (구글 메일은 검색바가 거의 상단 전체를 차지)
        top_bar_layout = QHBoxLayout()
        top_bar_layout.setContentsMargins(16, 8, 16, 8) # 여백 추가
        top_bar_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("search_bar")
        self.search_input.setPlaceholderText("메일 검색")
        self.search_input.setFixedHeight(40) # 검색바 높이 고정
        
        # 실제 구글 메일은 돋보기 아이콘이 인풋 안에 있음
        # QLineEdit에 setAction(QAction(QIcon(...)))으로 구현 가능하지만 일단 생략
        
        # 검색 버튼은 실제 구글 메일 검색 바에는 직접적인 버튼이 없으므로 제거하거나 숨김 처리
        # self.search_button = QPushButton("검색") 
        # top_bar_layout.addWidget(self.search_input)
        # top_bar_layout.addWidget(self.search_button)

        top_bar_layout.addWidget(self.search_input, 1) # 검색바가 전체 너비 차지
        # top_bar_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)) # 우측 정렬용

        main_content_v_layout.addLayout(top_bar_layout)

        # 중앙: 메일 목록 & 메일 상세 (수평 분할)
        center_h_layout = QHBoxLayout()
        center_h_layout.setContentsMargins(0, 0, 0, 0)
        center_h_layout.setSpacing(0)

        # 이메일 리스트
        self.email_list = QListWidget()
        self.email_list.setObjectName("email_list")
        self.email_list.setWordWrap(True) # 긴 제목/스니펫 자동 줄바꿈
        self.email_list.setVerticalScrollMode(QListWidget.ScrollPerPixel) # 부드러운 스크롤
        
        # 이메일 상세 보기 영역
        email_detail_v_layout = QVBoxLayout()
        email_detail_v_layout.setContentsMargins(0, 0, 0, 0)
        email_detail_v_layout.setSpacing(0)

        self.detail_subject_label = QLabel("메일을 선택해주세요.")
        self.detail_subject_label.setObjectName("detail_subject_label")
        self.detail_from_label = QLabel("")
        self.detail_from_label.setObjectName("detail_from_label")
        
        self.email_detail = QTextEdit()
        self.email_detail.setObjectName("email_detail")
        self.email_detail.setReadOnly(True)
        self.email_detail.setText("왼쪽 목록에서 메일을 선택하면 내용이 여기에 표시됩니다.")
        
        email_detail_v_layout.addWidget(self.detail_subject_label)
        email_detail_v_layout.addWidget(self.detail_from_label)
        email_detail_v_layout.addWidget(self.email_detail)

        center_h_layout.addWidget(self.email_list, 2) # 메일 목록이 상세보다 약간 작게
        center_h_layout.addLayout(email_detail_v_layout, 3) # 메일 상세가 더 넓게

        main_content_v_layout.addLayout(center_h_layout, 1) # 중앙 레이아웃이 남은 공간 차지

        # 전체 레이아웃 조립
        main_h_layout.addLayout(sidebar_layout, 1) # 사이드바 너비
        main_h_layout.addLayout(main_content_v_layout, 5) # 메인 콘텐츠 너비 (상대적 비율)

        self.setLayout(main_h_layout)

        # 시그널 연결
        self.email_list.itemClicked.connect(self.show_email_detail)

    def load_emails(self):
        self.email_list.clear()
        self.email_list.addItem("메일 로딩 중...")
        QApplication.processEvents() # UI 업데이트 강제

        if not self.gmail_service:
            self.email_list.clear()
            self.email_list.addItem("인증 서비스가 준비되지 않았습니다.")
            return

        emails_data = get_email_list_data(self.gmail_service, max_results=10) # 10개 메일 제한
        self.email_list.clear()

        if not emails_data:
            self.email_list.addItem("가져올 메일이 없습니다.")
            return

        for email in emails_data:
            # QListWidgetItem에 보낸사람, 제목, 미리보기를 HTML로 표시
            # 실제 Gmail처럼 From, Subject, Snippet이 한 줄에 표시되도록
            item_text = (
                f"<div style='line-height:1.4;'>"
                f"<span style='font-weight:bold;'>{email['from']}</span><br>"
                f"<span style='font-weight:bold; color:#202124;'>{email['subject']}</span><br>"
                f"<span style='color:#5F6368; font-size:12px;'>{email['snippet']}</span>"
                f"</div>"
            )
            list_item = QListWidget() # 껍데기
            list_item = self.create_email_list_item(email)
            self.email_list.addItem(list_item)
            # 메일 ID를 QListWidgetItem의 사용자 역할(UserRole) 데이터로 저장
            list_item.setData(Qt.UserRole, email['id'])

    def create_email_list_item(self, email_data):
        """메일 목록에 표시될 QListWidgetItem을 생성합니다."""
        item = QListWidgetItem()
        # HTML 형식으로 From, Subject, Snippet 표시
        item_html = f"""
        <div style="padding: 5px 0;">
            <div style="font-weight: bold; color: #3C4043; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;">
                {email_data['from']}
            </div>
            <div style="font-weight: bold; font-size: 15px; color: #202124; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;">
                {email_data['subject']}
            </div>
            <div style="color: #5F6368; font-size: 13px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;">
                {email_data['snippet']}
            </div>
        </div>
        """
        item.setText(item_html)
        # item.setTextAlignment(Qt.AlignTop) # 텍스트를 상단 정렬 (필요시)
        return item


    def show_email_detail(self, item):
        message_id = item.data(Qt.UserRole)
        if not message_id:
            self.detail_subject_label.setText("오류: 메일 ID를 찾을 수 없습니다.")
            self.detail_from_label.setText("")
            self.email_detail.setText("메일 ID를 가져오는 데 문제가 발생했습니다.")
            return

        self.detail_subject_label.setText("메일 내용을 로딩 중...")
        self.detail_from_label.setText("")
        self.email_detail.setText("메일 내용을 가져오고 있습니다...")
        QApplication.processEvents() # UI 업데이트 강제

        # From과 Subject는 이미 item.text()에서 가져올 수 있지만,
        # 실제 상세 화면에서는 메일 자체의 헤더에서 다시 가져오는 것이 더 정확할 수 있음.
        # 여기서는 편의상 item의 표시 텍스트에서 추출
        # 좀 더 정교하게 하려면 get_email_body에서 full 데이터를 받아와 헤더도 파싱해야 함.
        # 일단은 미리보기 텍스트를 파싱하여 From과 Subject를 분리하여 표시
        from_text = ""
        subject_text = ""
        try:
            # 간단한 HTML 파싱으로 From과 Subject 추출
            html_text = item.text()
            from_start = html_text.find("<div style=\"font-weight: bold; color: #3C4043;")
            if from_start != -1:
                from_end = html_text.find("</div>", from_start)
                from_text = html_text[from_start:from_end].split(">", 1)[1].strip()
            
            subject_start = html_text.find("<div style=\"font-weight: bold; font-size: 15px; color: #202124;")
            if subject_start != -1:
                subject_end = html_text.find("</div>", subject_start)
                subject_text = html_text[subject_start:subject_end].split(">", 1)[1].strip()
        except Exception as e:
            print(f"Error parsing item text for From/Subject: {e}")
            from_text = "Unknown Sender"
            subject_text = item.text().split('<br>')[0].replace('<b>', '').replace('</b>', '') # Fallback to simple split

        self.detail_subject_label.setText(subject_text)
        self.detail_from_label.setText(f"보낸 사람: {from_text}")


        email_content = get_email_body(self.gmail_service, message_id)
        if email_content:
            # HTML 내용이라면 setTextFormat을 HTML로 설정
            if "<html" in email_content.lower() or "<body" in email_content.lower():
                self.email_detail.setHtml(email_content)
            else:
                self.email_detail.setPlainText(email_content)
        else:
            self.email_detail.setPlainText("메일 내용을 가져오지 못했습니다.")


if __name__ == "__main__":
    # Windows에서 기본 스타일을 Fusion으로 설정하면 더 현대적인 UI를 얻을 수 있습니다.
    if sys.platform == "win32":
        QApplication.setStyle(QStyleFactory.create('Fusion'))

    app = QApplication(sys.argv)
    window = EmailClassifierUI()
    window.show()
    sys.exit(app.exec_())