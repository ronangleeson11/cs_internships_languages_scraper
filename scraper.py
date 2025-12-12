from bs4 import BeautifulSoup
import requests
import csv
from urllib.parse import urljoin

URL = requests.get("https://github.com/SimplifyJobs/Summer2026-Internships?tab=readme-ov-file")
soup = BeautifulSoup(URL.text, 'html.parser')
div = soup.find('div', attrs={"class": "OverviewRepoFiles-module__Box_1--xSt0T"}) # README
table = div.find("table") # Internship listing
links = table.find_all("a") # All links in the table

languages = {
    "Python": 0,
    "JavaScript": 0,
    "Java": 0,
    "C": 0,
    "C++": 0,
    "C#": 0,
    "Ruby": 0,
    "Go": 0,
    "PHP": 0,
    "Swift": 0,
    "Kotlin": 0,
    "TypeScript": 0
}

frameworks = {
    "Django": 0,
    "Flask": 0,
    "React": 0,
    "Angular": 0,
    "Vue": 0,
    "Spring": 0,
    "Laravel": 0,
    "Rails": 0,
    "ASP.NET": 0
}

libraries = {
    "NumPy": 0,
    "Pandas": 0,
    "TensorFlow": 0,
    "PyTorch": 0,
    "jQuery": 0,
    "Lodash": 0
}

i = 0

for link in links:
    href = link.get('href')
    if not href:
        continue
    print(f"Fetching: {href}")
    try:
        resp = requests.get(href, timeout=10)
        resp.raise_for_status()
        page_soup = BeautifulSoup(resp.text, 'html.parser')
        app_text = page_soup.get_text(separator=' ', strip=True)
    except Exception as e:
        print(f"Failed to fetch {href}: {e}")
        app_text = link.get_text(strip=True)
    lower_text = app_text.lower()
    for language in languages.keys():
        if language.lower() in lower_text:
            languages[language] += 1
    for framework in frameworks.keys():
        if framework.lower() in lower_text:
            frameworks[framework] += 1
    for library in libraries.keys():
        if library.lower() in lower_text:
            libraries[library] += 1
    i += 1
    if i > 20:
        break        

with open("out.csv", "w", newline='', encoding='utf-8') as out:
    writer = csv.writer(out)
    languages_sorted = sorted(languages.items(), key=lambda e: e[1])
    frameworks_sorted = sorted(frameworks.items(), key=lambda e: e[1])
    libraries_sorted = sorted(libraries.items(), key=lambda e: e[1])
    # writer.writerow(["Languages"])
    for (language) in languages_sorted:
        writer.writerow([language[0], language[1]])
    for (framework) in frameworks_sorted:
        writer.writerow([framework[0], framework[1]])
    for (library) in libraries_sorted:
        writer.writerow([library[0], library[1]])
    # writer.writerow([link.text, link.get('href')])
