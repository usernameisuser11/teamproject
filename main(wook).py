
import os

from data import emails
from  sortingMails import sortingMails
from Gmail_contents import gmail1_getmails
from Gmail_contents import gmail2_mysql
import datetime

reader = gmail1_getmails.GmailReader().get_emails()

gmail2_mysql.SaveDatabase(emails=sortingMails.sortingMails(emails=reader))
