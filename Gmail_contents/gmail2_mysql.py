import pymysql

# MySQL 서버 접속 설정
connection = pymysql.connect(
    host='127.0.0.1',       # 또는 외부 IP
    user='root',            # MySQL 사용자 이름
    password='#Publicwook1134',  # 비밀번호
    database='CollegeTeamProject_War_Against_Spam',  # 사용할 데이터베이스 이름
    charset='utf8mb4',      # 한글 저장 가능하게
    cursorclass=pymysql.cursors.DictCursor  # 결과를 딕셔너리로 받기
)

