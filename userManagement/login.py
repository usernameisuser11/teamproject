import pymysql
from cryptography.fernet import Fernet #암호화 라이브러리

 # MySQL 서버 접속 설정
conn = pymysql.connect(
    host='34.171.166.56',       # 또는 외부 IP
    user='root',            # MySQL 사용자 이름
    password='#Publicwook1134',  # 비밀번호
    database='mails',  # 사용할 데이터베이스 이름
    charset='utf8mb4',      # 한글 저장 가능하게
    cursorclass=pymysql.cursors.DictCursor  # 결과를 딕셔너리로 받기
)

id = input('아이디 입력')
pw = input('패스워드 입력')

