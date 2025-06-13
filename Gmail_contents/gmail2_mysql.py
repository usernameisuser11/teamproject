import pymysql
def SaveDatabase(emails, userName):
    table_name = f"{userName}_contents"

    # MySQL 서버 접속 설정
    conn = pymysql.connect(
        host='34.171.166.56',       # 또는 외부 IP
        user='root',            # MySQL 사용자 이름
        password='#Publicwook1134',  # 비밀번호
        database='mails',  # 사용할 데이터베이스 이름
        charset='utf8mb4',      # 한글 저장 가능하게
        cursorclass=pymysql.cursors.DictCursor  # 결과를 딕셔너리로 받기
    )

    contents = emails



    try:
        with conn.cursor() as cursor:
                for index in range(len(contents)) :
                    sql = f"INSERT INTO `{table_name}` (subject, sender, date, body, Category_index) VALUES (%s, %s, %s, %s, %s)"
                    values = (contents[index]["subject"], contents[index]["sender"], contents[index]["date"], contents[index]["body"], contents[index]["categoryIndex"])
                    cursor.execute(sql, values)
        conn.commit()

    finally:
        conn.close()