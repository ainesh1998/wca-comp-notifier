import requests, smtplib, ssl, time, pandas
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
MY_ADDRESS = 'ainesh1998@outlook.com'
PASSWORD = input("Type your password and press enter: ")
compsFound = {}

def getNewComps():
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    locations = soup.findAll("div", {"class": "location"})
    countries = [location.strong.text.strip() for location in locations]
    allComps = soup.findAll("div", {"class": "competition-link"})

    newComps = {}
    for i in range(len(locations)):
        for j in wantedLocations:
            if j in countries[i]:
                linkTag = allComps[i].a
                name = linkTag.text.strip()
                link = "https://worldcubeassociation.org/" + linkTag.get('href')
                if name not in compsFound:
                    newComps[name] = link
                    compsFound[name] = link

    print("1 new comp retrieved") if len(newComps) == 1 else print(str(len(newComps)) + " new comps retrieved")
    return newComps

def sendMail(newComps):
    print("Sending email notification")

    s = smtplib.SMTP(host='smtp-mail.outlook.com', port=587)
    s.starttls()
    s.login(MY_ADDRESS, PASSWORD)

    message_template = read_template('message.txt')

    msg = MIMEMultipart()
    message = message_template.substitute(COMP=pandas.DataFrame(list(newComps.keys())).to_csv(index=False))

    msg['From']=MY_ADDRESS
    msg['To']="ainesh1998@outlook.com"
    msg['Subject']="New WCA Competition Announced"

    msg.attach(MIMEText(message, 'plain'))

    s.send_message(msg)
    del msg

    print("Email sent")
    s.quit()


def main():
    print("Getting all relevant comps")
    # getNewComps()

    while True:
        # time.sleep(300) # wait one minute
        print("Checking for new comps at " + time.strftime('%H:%M'))
        newComps = getNewComps()
        if len(newComps) > 0:
            sendMail(newComps)

if __name__ == "__main__":
    main()
