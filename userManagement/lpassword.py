import sys
import pymysql
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QMessageBox,
    QDialog
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

# --- 데이터베이스 연결 정보 ---
DB_HOST = '34.171.166.56'
DB_USER = 'root'
DB_PASSWORD = '#Publicwook1134'
DB_NAME = 'mails'

class SimpleLoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("로그인")
        self.setGeometry(350, 350, 350, 420)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(15)
        title_label = QLabel("로그인")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        main_layout.addSpacing(25)
        self.id_input = QLineEdit(placeholderText="아이디")
        self.id_input.setFixedHeight(40)
        main_layout.addWidget(self.id_input)
        self.pw_input = QLineEdit(placeholderText="비밀번호")
        self.pw_input.setEchoMode(QLineEdit.Password)
        self.pw_input.setFixedHeight(40)
        main_layout.addWidget(self.pw_input)
        options_layout = QHBoxLayout()
        self.keep_login_checkbox = QCheckBox("로그인 상태 유지")
        options_layout.addWidget(self.keep_login_checkbox)
        options_layout.addStretch(1)
        main_layout.addLayout(options_layout)
        main_layout.addSpacing(10)
        self.login_button = QPushButton("로그인")
        self.login_button.setFixedHeight(45)
        self.login_button.clicked.connect(self.handle_login)
        main_layout.addWidget(self.login_button)
        main_layout.addSpacing(20)
        links_layout = QHBoxLayout()
        links_layout.setAlignment(Qt.AlignCenter)
        links_texts = ["아이디 찾기", "비밀번호 찾기", "회원가입"]
        for i, text in enumerate(links_texts):
            link_label = QLabel(f"<a href='#'>{text}</a>")
            link_label.setOpenExternalLinks(False)
            link_label.linkActivated.connect(lambda t=text: self.show_info_dialog(t))
            links_layout.addWidget(link_label)
            if i < len(links_texts) - 1:
                links_layout.addWidget(QLabel("·"))
        main_layout.addLayout(links_layout)
        main_layout.addStretch(1)
        self.setLayout(main_layout)
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #F0F0F0;
                font-family: Arial, sans-serif;
            }
            QLabel#TitleLabel {
                font-size: 20px;
                font-weight: bold;
                color: #333333;
            }
            QLabel {
                font-size: 12px;
                color: #555555;
            }
            QLineEdit {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 8px 10px;
                font-size: 14px;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 1px solid #0078D7;
            }
            QCheckBox {
                font-size: 12px;
                color: #444444;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border: 1px solid #AAAAAA;
                border-radius: 3px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #FFFFFF;
            }
            QCheckBox::indicator:checked {
                background-color: #0078D7;
                border: 1px solid #0078D7;
            }
            QPushButton {
                background-color: #0078D7;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
            QLabel a {
                color: #0078D7;
                text-decoration: none;
            }
            QLabel a:hover {
                text-decoration: underline;
            }
        """)

    def show_info_dialog(self, action):
        if action == "아이디 찾기":
            dialog = QDialog(self)
            dialog.setWindowTitle("아이디 찾기")
            dialog.setGeometry(400, 400, 300, 200)
            layout = QVBoxLayout()
            email_label = QLabel("이메일:")
            email_input = QLineEdit()
            submit_button = QPushButton("확인")
            submit_button.clicked.connect(lambda: self.show_message("아이디 찾기", f"입력한 이메일: {email_input.text()}"))
            layout.addWidget(email_label)
            layout.addWidget(email_input)
            layout.addWidget(submit_button)
            dialog.setLayout(layout)
            dialog.exec_()
        elif action == "비밀번호 찾기":
            dialog = QDialog(self)
            dialog.setWindowTitle("비밀번호 찾기")
            dialog.setGeometry(400, 400, 300, 200)
            layout = QVBoxLayout()
            id_label = QLabel("아이디:")
            id_input = QLineEdit()
            email_label = QLabel("이메일:")
            email_input = QLineEdit()
            submit_button = QPushButton("확인")
            submit_button.clicked.connect(lambda: self.show_message("비밀번호 찾기", f"입력한 아이디: {id_input.text()}, 이메일: {email_input.text()}"))
            layout.addWidget(id_label)
            layout.addWidget(id_input)
            layout.addWidget(email_label)
            layout.addWidget(email_input)
            layout.addWidget(submit_button)
            dialog.setLayout(layout)
            dialog.exec_()
        elif action == "회원가입":
            dialog = QDialog(self)
            dialog.setWindowTitle("회원가입")
            dialog.setGeometry(400, 400, 300, 300)
            layout = QVBoxLayout()
            id_label = QLabel("아이디:")
            id_input = QLineEdit()
            pw_label = QLabel("비밀번호:")
            pw_input = QLineEdit()
            pw_input.setEchoMode(QLineEdit.Password)
            email_label = QLabel("이메일:")
            email_input = QLineEdit()
            submit_button = QPushButton("가입")
            submit_button.clicked.connect(lambda: self.show_message("회원가입", f"입력한 아이디: {id_input.text()}, 이메일: {email_input.text()}"))
            layout.addWidget(id_label)
            layout.addWidget(id_input)
            layout.addWidget(pw_label)
            layout.addWidget(pw_input)
            layout.addWidget(email_label)
            layout.addWidget(email_input)
            layout.addWidget(submit_button)
            dialog.setLayout(layout)
            dialog.exec_()

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)

    def handle_login(self):
        user_id = self.id_input.text()
        user_pw = self.pw_input.text()
        if not user_id or not user_pw:
            QMessageBox.warning(self, "입력 오류", "아이디와 비밀번호를 모두 입력해주세요.")
            return
        print(f"로그인 시도 - 아이디: {user_id}")
        try:
            conn = pymysql.connect(
                host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
                database=DB_NAME, charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            with conn.cursor() as cursor:
                if user_id == "test" and user_pw == "1234":
                    QMessageBox.information(self, "로그인 성공", f"'{user_id}'님, 환영합니다!")
                else:
                    QMessageBox.warning(self, "로그인 실패", "아이디 또는 비밀번호가 올바르지 않습니다.")
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "데이터베이스 오류", f"DB 오류: {e}")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"알 수 없는 오류: {e}")
        finally:
            if 'conn' in locals() and conn:
                conn.close()

if __name__ == "__main__":
    try:
        print("[DEBUG] QApplication 생성 전")
        app = QApplication(sys.argv)
        print("[DEBUG] SimpleLoginWindow 생성 전")
        login_window = SimpleLoginWindow()
        print("[DEBUG] SimpleLoginWindow 생성 후, show() 전")
        login_window.show()
        print("[DEBUG] show() 후, app.exec_() 전")
        sys.exit(app.exec_())
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()