import os
from  sortingMails import sortingMails
from Gmail_contents import gmail1_getmails
from Gmail_contents import gmail2_mysql
from Gmail_contents import decrypt
credential_path = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(os.path.join(credential_path, "Gmail_contents," "credential.json")) :
    decrypt.decryptCredential()
getmails = gmail1_getmails.GmailReader()
getmails.authenticate()
gotmails = getmails.get_emails()
gmail2_mysql.SaveDatabase(emails=sortingMails.sortingMails(emails=gotmails))