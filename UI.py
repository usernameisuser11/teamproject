import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QPushButton, QTextEdit, QLineEdit,
    QSplitter, QFrame, QListWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QTextDocument
import pymysql
import pymysql

## 본문이 html 인지 판별 ##
def is_html(text):
    lowered = text.lower()
    return '<html' in text.lower() or '<body' in text.lower() or '<div' in text.lower() or '<p' in text.lower()

def html_to_plain_text(html):
    doc = QTextDocument()
    doc.setHtml(html)
    return doc.toPlainText()

## 데이터 베이스에서 자료 가져오기 ##
# MySQL 서버 접속 설정
conn = pymysql.connect(
    host='34.171.166.56',       # 또는 외부 IP
    user='root',            # MySQL 사용자 이름
    password='#Publicwook1134',  # 비밀번호
    database='mails',  # 사용할 데이터베이스 이름
    charset='utf8mb4',      # 한글 저장 가능하게
    port = 3306,
    cursorclass=pymysql.cursors.DictCursor  # 결과를 딕셔너리로 받기
)

try:
    with conn.cursor() as cursor:
        #SQL 쿼리 실행
        sql = "SELECT id, body, sender, subject, Category_index FROM contents"
        cursor.execute(sql)

        #결과를 리스트[dict] 형태로 가져오기
        mails = cursor.fetchall()

finally:
    conn.close()

common_mails = []
spam_mails = []
security_mails = []

for i in range(len(mails)) :
    if mails[i]['Category_index'] == 2 :
        security_mails.append(mails[i])
    if mails[i]['Category_index'] == 3 :
        spam_mails.append(mails[i])
    else :
        common_mails.append(mails[i])
        


class GmailUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gmail Client")
        self.resize(1200, 800)
        self.init_ui()

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
        menu_items = ["common", "Security", "Spam"]
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
            if item == "Spam":
                btn.clicked.connect(self.SpamMailsList)
            elif item == "common":
                btn.clicked.connect(self.CommonMailsList)
            elif item == "Security" :
                btn.clicked.connect(self.SecurityMailsList)
            


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
    
    def SpamMailsList(self, index) :
        self.email_list.clear() 
        for i in range(len(spam_mails)) :
            item = QListWidgetItem(self.email_list)
            subject_labels = QLabel(spam_mails[i]['subject'])
            subject_labels.setWordWrap(True)
            self.email_list.setItemWidget(item, subject_labels)
        self.current_category = spam_mails
        self.current_mail = i
        self.email_list.itemClicked.connect(self.Displaydetails)
    def SecurityMailsList(self, index) :
        self.email_list.clear() 
        for i in range(len(security_mails)) :
            item = QListWidgetItem(self.email_list)
            subject_labels = QLabel(security_mails[i]['subject'])
            subject_labels.setWordWrap(True)
            self.email_list.setItemWidget(item, subject_labels)
        self.current_category = security_mails
        self.current_mail = i
        self.email_list.itemClicked.connect(self.Displaydetails)
    def CommonMailsList(self, index) :
        self.email_list.clear() 
        for i in range(len(common_mails)) :
            item = QListWidgetItem(self.email_list)
            subject_labels = QLabel(common_mails[i]['subject'])
            subject_labels.setWordWrap(True)
            self.email_list.setItemWidget(item, subject_labels)
        self.current_category = common_mails
        self.current_mail = i
        self.email_list.itemClicked.connect(self.Displaydetails)
            
    def Displaydetails(self, item):
        index = self.email_list.row(item)
        content = self.current_category[index]['body']
    
        if is_html(content):
            self.email_detail.setHtml(content) 
        else:
            self.email_detail.setPlainText(content)

    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GmailUI()
    window.show()
    sys.exit(app.exec_())