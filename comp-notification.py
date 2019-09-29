import requests, smtplib, ssl, time
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
compsFound = []

def formatNewComps(newComps):
    result = ""
    compDetails = """<li>
                        <a href= "{}">{}</a>
                        <ul>
                            <li>Date: {}</li>
                            <li>Location: {}</li>
                        </ul>
                     </li><br>"""

    for comp in newComps:
        result = result + compDetails.format(newComps[comp][0], comp, newComps[comp][1], newComps[comp][2])
    return result

def getNewComps():
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    locations = soup.findAll("div", {"class": "location"})
    countries = [location.strong.text.strip() for location in locations]
    allComps = soup.findAll("div", {"class": "competition-link"})
    dates = soup.findAll("span", {"class": "date"})

    newComps = {}
    for i in range(len(locations)):
        for j in wantedLocations:
            if j in countries[i]:
                linkTag = allComps[i].a
                name = linkTag.text.strip()
                link = "https://worldcubeassociation.org/" + linkTag.get('href')
                if name not in compsFound:
                    newComps[name] = [link, dates[i].text.strip(), locations[i].text.strip()]
                    compsFound.append(name)

    # Remove old comps
    compsFound = [comp for comp in compsFound if comp in allComps]

    print("1 new comp retrieved") if len(newComps) == 1 else print(str(len(newComps)) + " new comps retrieved")
    return newComps

def sendMail(newComps):
    print("Sending email notification")

    s = smtplib.SMTP(host='smtp-mail.outlook.com', port=587)
    s.starttls()
    s.login(MY_ADDRESS, PASSWORD)

    message_template = read_template('newComp.html')

    msg = MIMEMultipart()
    message = message_template.substitute(COMP=formatNewComps(newComps))

    msg['From'] = MY_ADDRESS
    msg['To'] = "ainesh1998@outlook.com"
    msg['Subject'] = "New WCA Competition Announced"

    msg.attach(MIMEText(message, 'html'))

    s.send_message(msg)
    del msg

    print("Email sent")
    s.quit()


def main():
    print("Getting all relevant comps")
    newComps = getNewComps()

    while True:
        time.sleep(300)
        print("Checking for new comps at " + time.strftime('%H:%M'))
        newComps = getNewComps()
        if len(newComps) > 0:
            sendMail(newComps)

if __name__ == "__main__":
    main()
