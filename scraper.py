from bs4 import BeautifulSoup
import requests
import csv
import matplotlib.pyplot as plt
import re
import string
from keywords import languages, frameworks, libraries


def get_links(url, limit):
    link = requests.get(url)
    soup = BeautifulSoup(link.text, 'html.parser')
    div = soup.find('div', attrs={"class": "OverviewRepoFiles-module__Box_1--xSt0T"}) # Get README
    table = div.find("table") # Get internship listing
    all_links = table.find_all("a") # Get all links in internship listing
    links = [link for link in all_links if "simplify.jobs" not in link.get("href").lower()]
    return links[:limit]


def get_frequencies(links):
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; scraper/1.0)"})
    for link in links:
        href = link.get("href")
        if not href:
            continue
        print("-" * 64)
        print(f"Fetching: {href}")
        try:
            resp = session.get(href, timeout=10)
            resp.raise_for_status()
            page_soup = BeautifulSoup(resp.text, 'html.parser')
            app_text = page_soup.get_text(separator=' ', strip=True)
            if not app_text.strip(): # Fallback 1: check meta description
                print("Falling back to meta description")
                meta = page_soup.find('meta', attrs={"name": "description"})
                if meta and meta.get('content'):
                    app_text = meta.get('content').strip()
                else:
                    og = page_soup.find('meta', attrs={"property": "og:description"})
                    if og and og.get('content'):
                        app_text = og.get('content').strip()
            if not app_text.strip(): # Fallback 2: check largest text-containing element
                print("Falling back to largest text-containing element")
                candidates = page_soup.find_all(['main', 'article', 'div'])
                if candidates:
                    largest = max(candidates, key=lambda t: len(t.get_text(strip=True)))
                    app_text = largest.get_text(separator=' ', strip=True)
            print(app_text[:100] + "...")
        except Exception as e:
            print(f"Failed to fetch {href}: {e}")
            app_text = link.get_text(strip=True)
        for language in languages.keys():
            if check_present(language, app_text):
                print(f"Found language: {language}")
                languages[language] += 1
        for framework in frameworks.keys():
            if check_present(framework, app_text):
                print(f"Found framework: {framework}")
                frameworks[framework] += 1
        for library in libraries.keys():
            if check_present(library, app_text):
                print(f"Found library: {library}")
                libraries[library] += 1


def check_present(key, text):
    punct = re.escape(string.punctuation)
    pattern = rf'(?:(?<=^)|(?<=[\s{punct}]))' + re.escape(key) + rf'(?:(?=$)|(?=[\s{punct}]))' # This is a regex, I have no idea how this works, but it only mathces the key if it is surrounded by whitespace or punctuation
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


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


def plot_bar():
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
    plot_bar()


if __name__ == "__main__":
    scrape("https://github.com/SimplifyJobs/Summer2026-Internships?tab=readme-ov-file", 10)
    