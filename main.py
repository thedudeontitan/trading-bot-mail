import os
import pickle
import re
import time
import csv
from datetime import date,datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from base64 import urlsafe_b64decode, urlsafe_b64encode
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type
from scraper import scrapedata
import MetaTrader5 as mt5
from tradingbot import connect
from config import emailID,Sender_Email,Meta_Trader_Account_No,Meta_Trader_Password,Meta_Tarder_Server



SCOPES = ['https://mail.google.com/']
our_email = emailID

def gmail_authenticate():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

service = gmail_authenticate()
account = int(Meta_Trader_Account_No)
password= Meta_Trader_Password
server= Meta_Tarder_Server
connect(account,password,server)
def search_messages(service, query):
    result = service.users().messages().list(userId='me',q=query).execute()
    messages = [ ]
    if 'messages' in result:
        messages.extend(result['messages'])
    while 'nextPageToken' in result:
        page_token = result['nextPageToken']
        result = service.users().messages().list(userId='me',q=query, pageToken=page_token).execute()
        if 'messages' in result:
            messages.extend(result['messages'])
    # print(messages) 
    return messages

def clean(text):
    return "".join(c if c.isalnum() else "_" for c in text)

def parse_parts(service, parts, folder_name, message):

    if parts:
        for part in parts:
            filename = part.get("filename")
            mimeType = part.get("mimeType")
            body = part.get("body")
            data = body.get("data")
            file_size = body.get("size")
            part_headers = part.get("headers")
            if part.get("parts"):
                parse_parts(service, part.get("parts"), folder_name, message)
            if mimeType == "text/plain":
                if data:
                    text = urlsafe_b64decode(data).decode()
            elif mimeType == "text/html":
                if not filename:
                    filename = "index.html"
                filepath = os.path.join(folder_name, filename)
                print("Saving HTML to", filepath)
                
                with open(filepath, "wb") as f:
                    f.write(urlsafe_b64decode(data))
                with open(filepath,"r") as f:
                        datax = scrapedata(f.read())
                        with open((clean(str(date.today().strftime("%d_%m_%Y")))+".csv"),"a",encoding='UTF-8') as x:
                            w = csv.writer(x)
                            for s in datax:
                                for key, val in s.items():
                                    w.writerow([key, val])
                                    
            else:
                pass
            
            
def read_message(service, message):
    msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
    payload = msg['payload']
    headers = payload.get("headers")
    parts = payload.get("parts")
    folder_name = "email"
    has_subject = False
    if headers:
        for header in headers:
            name = header.get("name")
            value = header.get("value")
            
            if name.lower() == 'from':
                print("From:", value)

            if name.lower() == "to":
                print("To:", value)

            if name.lower() == "date":
                print("Date:",value)

            if name.lower() == "subject":
                has_subject = True
                print("Subject:", value)
                regsub = re.search(r"[A-Za-z: ]+([0-9.]+[ -part 0-9]+)",value)
                sub = regsub.group(1)
                
                resub2 = re.search(r"[A-Za-z: ]+([0-9.]+)[ -part 0-9]+",value)
                maildate = resub2.group(1)
                print(maildate, type(maildate))
                print(str(date.today().strftime("%d.%m.%Y")), type(date.today().strftime("%d.%m.%Y")))
                # if str(maildate) == str(date.today().strftime("%d.%m.%Y")):
                # sub = value
                folder_name = clean(sub)
                while not os.path.isdir(folder_name):
                    os.mkdir(folder_name)
                

    if not has_subject:
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)

    parse_parts(service, parts, folder_name, message)
    print("="*50)

results = search_messages(service, Sender_Email)
results2 = search_messages(service, str(date.today().strftime("%d.%m.%Y")))

for msg in results and results2:

    read_message(service, msg)
