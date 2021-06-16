import smtplib
import imaplib
import base64
import os
import email
import re

from PyQt5.QtWidgets import QLabel


class Email:
    def __init__(self, smtp_server, imap_server, username, password):
        # SMTP
        self.server = smtplib.SMTP(smtp_server, 587)
        self.server.ehlo()
        self.server.login(username, password)

        # IMAP
        self.mail = imaplib.IMAP4_SSL(imap_server, 993)
        self.mail.login(username, password)

    def receive(self):
        self.mail.select("inbox")

    def show_latest(self):
        self.mail.sort('DATE', 'UTF-8', 'ALL')
        for i in range(1, 10):
            data = self.mail.fetch(i, '(BODY[HEADER])')
            header_data = data[1][0][1]
            parser = email.parser()
            msg = parser.parsestr(header_data)
            print(msg['subject'])

    def show_inbox(self):
        _, search_data = self.mail.search(None, 'ALL')
        my_message = []

        count = 0
        for num in search_data[0].split():
            email_data = {}
            _, data = self.mail.fetch(num, '(RFC822)')
            # print(data[0])
            _, b = data[0]
            email_message = email.message_from_bytes(b)
            for header in ['subject', 'to', 'from', 'date']:
                print("{}: {}".format(header, email_message[header]))
                email_data[header] = email_message[header]
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True)
                    email_data['body'] = body.decode()
                elif part.get_content_type() == "text/html":
                    html_body = part.get_payload(decode=True)
                    email_data['html_body'] = html_body.decode()
            my_message.append(email_data)
            count += 1
            if count > 9:
                break
        return my_message

    def show_widget(self):
        _, search_data = self.mail.search(None, 'ALL')

        labels = []

        count = 0
        for num in search_data[0].split():
            email_data = {}
            _, data = self.mail.fetch(num, '(RFC822)')
            # print(data[0])
            _, b = data[0]
            email_message = email.message_from_bytes(b)
            sender = re.sub('<[^>]+>', '', email_message['from'])
            labels.append({"subject": email_message['subject'], "sender": sender.strip()})

            count += 1
            if count > 3:
                break

        return labels

    def print_mail(self):
        type, data = self.mail.search(None, 'ALL')
        mail_ids = data[0]
        id_list = mail_ids.split()

        for num in data[0].split():
            typ, data = self.mail.fetch(num, '(RFC822)')
            raw_email = data[0][1]
            # converts byte literal to string removing b''
            raw_email_string = raw_email.decode('utf-8')
            email_message = email.message_from_string(raw_email_string)

        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_string(response_part[1].decode('utf-8'))
                email_subject = msg['subject']
                email_from = msg['from']
                print('From : ' + email_from + '\n')
                print('Subject : ' + email_subject + '\n')
                print(msg.get_payload(decode=True))

    def close(self):
        self.mail.close()
        self.server.close()
