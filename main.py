from Gmail_contents import gmail1_getmails
from sortingMails import sortingMails
import datetime

def generate_html(categorized_emails):
    """HTML 생성"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>분류된 이메일</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .category { margin-bottom: 30px; }
            .category h2 { color: #333; border-bottom: 2px solid #333; }
            .email { 
                border: 1px solid #ddd;
                padding: 15px;
                margin: 10px 0;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
            .email:hover { background-color: #f0f0f0; }
            .subject { font-weight: bold; color: #2c3e50; }
            .sender { color: #7f8c8d; }
            .date { color: #95a5a6; font-size: 0.9em; }
            .body { margin-top: 10px; }
        </style>
    </head>
    <body>
        <h1>분류된 이메일</h1>
    """
    
    category_names = {
        'work': '업무',
        'personal': '개인',
        'spam': '스팸',
        'newsletter': '뉴스레터',
        'other': '기타'
    }
    
    for category, emails in categorized_emails.items():
        if emails:  # 해당 카테고리에 이메일이 있는 경우만 표시
            html += f"""
            <div class="category">
                <h2>{category_names[category]}</h2>
            """
            
            for email in emails:
                html += f"""
                <div class="email">
                    <div class="subject">{email['subject']}</div>
                    <div class="sender">보낸사람: {email['sender']}</div>
                    <div class="date">날짜: {email['date']}</div>
                    <div class="body">{email['body'][:200]}...</div>
                </div>
                """
            
            html += "</div>"
    
    html += """
    </body>
    </html>
    """
    
    return html

def main():
    # Gmail 이메일 가져오기
    gmail_reader = GmailReader()
    emails = gmail_reader.get_emails(max_results=20)
    
    # 이메일 분류
    classifier = EmailClassifier()
    categorized_emails = classifier.classify_emails(emails)
    
    # HTML 생성
    html_content = generate_html(categorized_emails)
    
    # HTML 파일 저장
    with open('categorized_emails.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("이메일 분류가 완료되었습니다.")
    print("categorized_emails.html 파일을 확인해주세요.")

if __name__ == "__main__":
    main() 