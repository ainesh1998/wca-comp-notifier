import requests, smtplib, ssl, time, os
from bs4 import BeautifulSoup
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

interval = 30 # how often to check, in minutes
url = "https://www.worldcubeassociation.org/competitions"
WANTED_LOCATIONS = os.environ.get('WANTED_LOCATIONS')
MY_ADDRESS = os.environ.get('ADDRESS')
PASSWORD = os.environ.get('PASSWORD')
compsFound = []

# Ensure the globals have the intended values
def setGlobals():
    global WANTED_LOCATIONS, MY_ADDRESS, PASSWORD
    if not WANTED_LOCATIONS or not MY_ADDRESS or not PASSWORD:
        with open ("app.cfg", "r") as file:
            config_vars = file.read().split('\n')
            WANTED_LOCATIONS = config_vars[0].split(',')
            MY_ADDRESS = config_vars[1]
            PASSWORD = config_vars[2]
    else:
        WANTED_LOCATIONS = WANTED_LOCATIONS.split(',')

# Reads email templates
def read_template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

# Puts in information regarding new competitions into the email template
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

# Removes old competitions (those not on the competitions page anymore) and gets those just announced
def updateComps():
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    locations = soup.findAll("div", {"class": "location"})
    countries = [location.strong.text.strip() for location in locations]
    allCompDivs = soup.findAll("div", {"class": "competition-link"})
    allComps = [compDiv.a for compDiv in allCompDivs]
    dates = soup.findAll("span", {"class": "date"})

    newComps = {}
    global compsFound

    # Remove old comps - those not on the WCA page anymore
    compsFound = [comp for comp in compsFound if comp in [comp.text.strip() for comp in allComps]]

    # Get new comps
    for i in range(len(locations)):
        for j in WANTED_LOCATIONS:
            if j in countries[i]:
                name = allComps[i].text.strip()
                link = "https://worldcubeassociation.org/" + allComps[i].get('href')
                if name not in compsFound:
                    newComps[name] = [link, dates[i].text.strip(), locations[i].text.strip()]

    compsFound = compsFound + list(newComps.keys())

    print("1 new comp retrieved") if len(newComps) == 1 else print(str(len(newComps)) + " new comps retrieved")
    return newComps

# Sends an email containing the new competitions
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
    # Initialise
    print("Getting all relevant comps")
    setGlobals()
    updateComps()

    while True:
        time.sleep(interval * 60)
        print("Checking for new comps at " + time.strftime('%H:%M'))
        newComps = updateComps()
        if len(newComps) > 0:
            sendMail(newComps)

if __name__ == "__main__":
    main()
