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
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
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
        
        # 링크 생성 및 이벤트 연결 수정
        find_id_link = QLabel("<a href='find_id'>아이디 찾기</a>")
        find_pw_link = QLabel("<a href='find_pw'>비밀번호 찾기</a>")
        signup_link = QLabel("<a href='signup'>회원가입</a>")
        
        find_id_link.linkActivated.connect(lambda: self.show_info_dialog("아이디 찾기"))
        find_pw_link.linkActivated.connect(lambda: self.show_info_dialog("비밀번호 찾기"))
        signup_link.linkActivated.connect(lambda: self.show_info_dialog("회원가입"))
        
        links_layout.addWidget(find_id_link)
        links_layout.addWidget(QLabel("·"))
        links_layout.addWidget(find_pw_link)
        links_layout.addWidget(QLabel("·"))
        links_layout.addWidget(signup_link)
        
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
            
            def find_id():
                email = email_input.text()
                if not email:
                    QMessageBox.warning(dialog, "입력 오류", "이메일을 입력해주세요.")
                    return
                # 여기서는 테스트용으로 하드코딩된 이메일 사용
                if email == "test@example.com":
                    QMessageBox.information(dialog, "아이디 찾기", "회원님의 아이디는 'test' 입니다.")
                else:
                    QMessageBox.warning(dialog, "아이디 찾기", "해당 이메일로 등록된 계정이 없습니다.")
                dialog.close()
            
            submit_button.clicked.connect(find_id)
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
            
            def find_password():
                user_id = id_input.text()
                email = email_input.text()
                if not user_id or not email:
                    QMessageBox.warning(dialog, "입력 오류", "아이디와 이메일을 모두 입력해주세요.")
                    return
                # 여기서는 테스트용으로 하드코딩된 값 사용
                if user_id == "test" and email == "test@example.com":
                    QMessageBox.information(dialog, "비밀번호 찾기", "비밀번호 재설정 링크가 이메일로 전송되었습니다.")
                else:
                    QMessageBox.warning(dialog, "비밀번호 찾기", "일치하는 계정 정보가 없습니다.")
                dialog.close()
            
            submit_button.clicked.connect(find_password)
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
            pw_confirm_label = QLabel("비밀번호 확인:")
            pw_confirm_input = QLineEdit()
            pw_confirm_input.setEchoMode(QLineEdit.Password)
            email_label = QLabel("이메일:")
            email_input = QLineEdit()
            submit_button = QPushButton("가입")
            
            def sign_up():
                user_id = id_input.text()
                password = pw_input.text()
                password_confirm = pw_confirm_input.text()
                email = email_input.text()
                
                if not all([user_id, password, password_confirm, email]):
                    QMessageBox.warning(dialog, "입력 오류", "모든 항목을 입력해주세요.")
                    return
                    
                if password != password_confirm:
                    QMessageBox.warning(dialog, "입력 오류", "비밀번호가 일치하지 않습니다.")
                    return
                    
                # 여기서는 테스트용으로 간단한 유효성 검사만 수행
                if len(user_id) < 4:
                    QMessageBox.warning(dialog, "입력 오류", "아이디는 4자 이상이어야 합니다.")
                    return
                    
                if len(password) < 4:
                    QMessageBox.warning(dialog, "입력 오류", "비밀번호는 4자 이상이어야 합니다.")
                    return
                    
                if "@" not in email:
                    QMessageBox.warning(dialog, "입력 오류", "올바른 이메일 형식이 아닙니다.")
                    return
                
                QMessageBox.information(dialog, "회원가입", "회원가입이 완료되었습니다.")
                dialog.close()
            
            submit_button.clicked.connect(sign_up)
            layout.addWidget(id_label)
            layout.addWidget(id_input)
            layout.addWidget(pw_label)
            layout.addWidget(pw_input)
            layout.addWidget(pw_confirm_label)
            layout.addWidget(pw_confirm_input)
            layout.addWidget(email_label)
            layout.addWidget(email_input)
            layout.addWidget(submit_button)
            dialog.setLayout(layout)
            dialog.exec_()

    def handle_login(self):
        user_id = self.id_input.text()
        user_pw = self.pw_input.text()
        if not user_id or not user_pw:
            QMessageBox.warning(self, "입력 오류", "아이디와 비밀번호를 모두 입력해주세요.")
            return
        print(f"로그인 시도 - 아이디: {user_id}")
        
        # 테스트용 로그인 처리
        if user_id == "test" and user_pw == "1234":
            QMessageBox.information(self, "로그인 성공", f"'{user_id}'님, 환영합니다!")
        else:
            QMessageBox.warning(self, "로그인 실패", "아이디 또는 비밀번호가 올바르지 않습니다.")
            
        # MySQL 연결 부분 주석 처리
        """
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
        """

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