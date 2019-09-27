import requests, smtplib, ssl
from bs4 import BeautifulSoup
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def read_template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

wantedLocations = ["Malaysia", "United Kingdom"]
url = "https://www.worldcubeassociation.org/competitions"
r = requests.get(url)
soup = BeautifulSoup(r.text, 'html.parser')
locations = soup.findAll("div", {"class": "location"})
countries = [location.strong for location in locations]
comps = soup.findAll("div", {"class": "competition-link"})

for i in range(len(locations)):
    for j in wantedLocations:
        if j in countries[i]:
            print(comps[i])

MY_ADDRESS = 'ainesh1998@outlook.com'
PASSWORD = input("Type your password and press enter: ")

s = smtplib.SMTP(host='smtp-mail.outlook.com', port=587)
s.starttls()
s.login(MY_ADDRESS, PASSWORD)

message_template = read_template('message.txt')

msg = MIMEMultipart()
message = message_template.substitute(COMP="Beacon House Open 2019")

msg['From']=MY_ADDRESS
msg['To']="ainesh1998@outlook.com"
msg['Subject']="New WCA Competition Announced"

msg.attach(MIMEText(message, 'plain'))

s.send_message(msg)
del msg

s.quit()
