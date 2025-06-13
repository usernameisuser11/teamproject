import sys
import os
from  sortingMails import sortingMails
from Gmail_contents import GetMails
from Gmail_contents import gmail2_mysql
from Gmail_contents import decrypt
def saveDB(Id,userName):
    credential_path = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(os.path.join(credential_path, "Gmail_contents," "credential.json")) :
        decrypt.decryptCredential()
    getmails = GetMails.GmailReader()
    gotmails = []
    
    gotmails = getmails.get_emails(gotID=Id)
    gmail2_mysql.SaveDatabase(userName=userName,emails=sortingMails.sortingMails(emails=gotmails))