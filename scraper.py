from bs4 import BeautifulSoup
import requests
import csv

URL = requests.get ("https://github.com/SimplifyJobs/Summer2026-Internships?tab=readme-ov-file")
soup = BeautifulSoup(URL.text, 'html.parser')
div = soup.find('div', attrs={"class": "OverviewRepoFiles-module__Box_1--xSt0T"}) # README
table = div.find("table") # Internship listing
links = table.find_all("a") # All links in the table

with open("out.csv", "w", newline='', encoding='utf-8') as out:
    writer = csv.writer(out)
    for (link) in links:
        writer.writerow([link.text, link.get('href')])
    print(table)
