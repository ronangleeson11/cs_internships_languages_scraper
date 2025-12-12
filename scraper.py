from bs4 import BeautifulSoup
import requests
import csv
import matplotlib.pyplot as plt
from keywords import languages, frameworks, libraries


def get_links(url, limit):
    link = requests.get(url)
    soup = BeautifulSoup(link.text, 'html.parser')
    div = soup.find('div', attrs={"class": "OverviewRepoFiles-module__Box_1--xSt0T"}) # Get README
    table = div.find("table") # Get internship listing
    links = table.find_all("a", limit = limit) # Get all links in internship listing
    return links


def get_frequencies(links):
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


def write(out):
    with open(out, "w", newline='', encoding='utf-8') as out:
        writer = csv.writer(out)
        languages_sorted = sorted(languages.items(), key=lambda e: e[1], reverse=True)
        frameworks_sorted = sorted(frameworks.items(), key=lambda e: e[1], reverse=True)
        libraries_sorted = sorted(libraries.items(), key=lambda e: e[1], reverse=True)
        writer.writerow(["Languages", "Frequency"])
        for (language) in languages_sorted:
            writer.writerow([language[0], language[1]])
        writer.writerow(["Frameworks", "Frequency"])    
        for (framework) in frameworks_sorted:
            writer.writerow([framework[0], framework[1]])
        writer.writerow(["Libraries", "Frequency"])    
        for (library) in libraries_sorted:
            writer.writerow([library[0], library[1]])


def plot():
    def plot_category(category_dict, title):
        items = sorted(category_dict.items(), key=lambda e: e[1], reverse=True)
        names = [item[0] for item in items]
        values = [item[1] for item in items]
        plt.bar(names, values, color='skyblue')
        plt.title(title)
        plt.xlabel('Items')
        plt.ylabel('Frequencies')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    plot_category(languages, "Programming Languages Frequency")
    plot_category(frameworks, "Frameworks Frequency")
    plot_category(libraries, "Libraries Frequency")


def scrape(link, limit):
    links = get_links(link, limit)
    get_frequencies(links)
    write("frequencies.csv")
    plot()


if __name__ == "__main__":
    scrape("https://github.com/SimplifyJobs/Summer2026-Internships?tab=readme-ov-file", 10)
    