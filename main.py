import requests
from bs4 import BeautifulSoup

def scrape_news(url):
    response = requests.get(url)
    print(response)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = []
        
        for article in soup.find_all('div'):
            headline = article.find('h3')
            if headline and headline.find('a'):
                linkline = headline.find('a')
                link = linkline['href'] if linkline else ''
                headlines.append({'title': headline.get_text(strip = True), 'link': link})
                
        return headlines
    else:
        print('Failed to retrieve the page.')
        
if __name__ == '__main__':
    news_url = 'https://www.pinkelephant.com/en-us/'
    news_headlines = scrape_news(news_url)
    
    if news_headlines:
        print('Latest News Headlines:')
        for index, news in enumerate(news_headlines, start = 1):
            print(f"{index}. {news['title']}")
            print(f"    Link: {news['link']}")
            print()
    else:
        print('No news headlines found.')
            