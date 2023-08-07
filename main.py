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
        response = requests.get(url)
        print(response, url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            scrape_routes(soup)
            # print(routes)
            for element in soup.find_all("div"):
                headlines.append(
                    {"url": url, "article": element.get_text(strip=True).casefold()}
                )
        else:
            print("Failed to retrieve the page.")
    return headlines


def find_string(articles, target_string):
    found_strings = [
        {"url": data["url"], "string": target_string, "element": data["article"]}
        for data in articles
        if target_string in data["article"]
    ]
    return found_strings


if __name__ == "__main__":
    news_url = "https://www.pinkelephant.com/en-us"
    routes = [news_url]
    target_string = "PDC"
    # print(routes)
    news_headlines = scrape_news()
    found_strings = find_string(news_headlines, target_string)

    print(found_strings)
