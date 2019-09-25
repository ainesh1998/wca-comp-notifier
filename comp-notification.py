import requests
from bs4 import BeautifulSoup

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
