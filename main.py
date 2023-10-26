import requests
from bs4 import BeautifulSoup


def scrape_routes(soup):
    a_tags = soup.find_all("a")
    for tag in a_tags:
        link = tag.get("href", "").casefold()
        if link and link not in routes:
            new_route = "https://www.pinkelephant.com" + link
            routes.append(new_route) if link.startswith(
                "/en"
            ) and new_route not in routes else ""


def scrape_news():
    headlines = []
    for url in routes:
        response = requests.get(url, verify=False)
        print(response, url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            scrape_routes(soup)
            # print(routes)
            headlines = find_string(soup.descendants, headlines, url)
        else:
            print("Failed to retrieve the page.")
    return headlines


def find_string(tags, headlines, url):
    for element in tags:
        if element.string and target_string in element.string:
            headlines.append(
                {"url": url, "tags": element}
            )

    return headlines


if __name__ == "__main__":
    news_url = "https://www.pinkelephant.com/en-us"
    routes = [news_url]
    target_string = "PINKLINK-INTERNAL"
    # print(routes)
    news_headlines = scrape_news()
    print(news_headlines)
