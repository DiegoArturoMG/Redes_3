import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

mailsender = "manurome28@gmail.com"
mailreceip = "manurome28@gmail.com"
mailserver = 'smtp.gmail.com: 587'
password = 'LuisFigueroa1'

def enviaAlerta(subject,imgPath):
    msg = MIMEMultipart()

    msg['Subject'] = subject
    msg['From'] = mailsender
    msg['To'] = mailreceip
    
    fp = open(imgPath, 'rb')
    img = MIMEImage(fp.read())
    fp.close()
    
    msg.attach(img)
    
    mserver = smtplib.SMTP(mailserver)
    mserver.starttls()
    # Login Credentials for sending the mail
    mserver.login(mailsender, password)

    mserver.sendmail(mailsender, mailreceip, msg.as_string())
    mserver.quit()
