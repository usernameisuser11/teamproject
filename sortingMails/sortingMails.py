from data import emails


check_security = ['인증', '보안']


def checkSpam() :
    check_spam = '멤버십'
    spamMail = []
    nonSpam = []
    for mail in range(len(emails.emails)) :
        if check_spam in emails.emails[mail]['subject'] or check_spam in emails.emails[mail]['body']:
            spamMail.append(emails.emails[mail])
        else :
            nonSpam.append(emails.emails[mail])
    print(spamMail)