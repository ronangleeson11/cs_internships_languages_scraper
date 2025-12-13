from bs4 import BeautifulSoup
import requests
import csv
import matplotlib.pyplot as plt
import re
import string
from keywords import keywords

LIMIT = 20 # number of application links to scrape

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
    session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; scraper/1.0)"}) # Set a user-agent to avoid being blocked
    for link in links:
        href = link.get("href")
        if not href:
            continue
        print(f"{'-'*64}\nFetching: {href}")
        try:
            resp = session.get(href, timeout=10)
            resp.raise_for_status()
            page_soup = BeautifulSoup(resp.text, 'html.parser')
            app_text = page_soup.get_text(separator=' ', strip=True) # Try to get all text from page
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
        for name, category in keywords.items(): # Check for presence of each keyword in the application text
            for key in category.keys():
                if check_present(key, app_text):
                    print(f"Found {name}: {key}")
                    category[key] += 1


def check_present(key, text):
    punct = re.escape(string.punctuation)
    pattern = rf'(?:(?<=^)|(?<=[\s{punct}]))' + re.escape(key) + rf'(?:(?=$)|(?=[\s{punct}]))' # This is a regex, I have no idea how this works, but it only mathces the key if it is surrounded by whitespace or punctuation
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def write(out):
    with open(out, "w", newline='', encoding='utf-8') as out:
        writer = csv.writer(out)
        for name, category in keywords.items():
            category_sorted = sorted(category.items(), key=lambda e: e[1], reverse=True)
            writer.writerow([name, "Frequency"])
            for (key) in category_sorted:
                writer.writerow([key[0], key[1]])


def plot_bar():
    def plot_category(category_dict, name):
        items = sorted(category_dict.items(), key=lambda e: e[1], reverse=True)
        names = [item[0] for item in items]
        values = [item[1] for item in items]
        plt.clf()
        plt.bar(names, values, color="skyblue")
        plt.title(name + " Frequencies")
        plt.xlabel("Keywords")
        plt.ylabel("Frequencies")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"figs/{name}_frequency_plot.png", dpi=300, bbox_inches="tight")
    for name, category in keywords.items():
        plot_category(category, name)


def scrape(link, limit):
    links = get_links(link, limit)
    get_frequencies(links)
    write("frequencies.csv")
    plot_bar()


if __name__ == "__main__":
    scrape("https://github.com/SimplifyJobs/Summer2026-Internships?tab=readme-ov-file", LIMIT)
    