from Gmail_contents import gmail1_getmails



check_security = ["Security", "보안",
    "Authentication", "인증",
    "Verification", "확인",
    "Confirm", "확인하다",
    "Confirmation", "확인",
    "Validation", "검증",
    "Account verification", "계정 확인",
    "Identity verification", "신원 확인",
    "Secure", "안전한",
    "Two-factor authentication", "2단계 인증",
    "OTP", "일회용 비밀번호",
    "Password reset", "비밀번호 재설정",
    "Account recovery", "계정 복구",
    "Access alert", "접속 알림",
    "Alert", "경고",
    "Notification"]
check_spam = ['광고', '특가', '세일', '혜택', '멤버십', 'promotion', 'advertisement', 'Ad', 'Deal', 'Sale', 'Limited time offer']
reader = gmail1_getmails.GmailReader()
emails = reader.get_emails()

def sortingMails(emails) :
    spamMail = []
    securityMail = []
    commonMail = []
    for mail in range(len(emails)) :
        if any(spam_word in emails[mail]['subject'] or spam_word in emails[mail]['body'] for spam_word in check_spam) :
            spamMail.append(emails[mail])
            emails[mail]['categoryIndex'] = 3
        elif any( security_word in emails[mail]['subject'] or security_word in emails[mail]['body'] for security_word in check_security) :
            securityMail.append(emails[mail])
            emails[mail]['categoryIndex'] = 2
        else :
            commonMail.append(emails[mail])
            emails[mail]['categoryIndex'] = 1

    return emails