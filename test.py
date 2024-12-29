import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from datetime import datetime, timedelta
import pytz

def get_google_news(query):
    encoded_query = quote_plus(query)
    url = f"https://news.google.com/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        articles = soup.find_all('article')
        print(f"Number of articles found: {len(articles)}")
        
        results = []
        
        for article in articles:
            headline = article.find('a', class_='JtKRv')
            time_element = article.find('time')
            if headline and time_element:
                title = headline.text.strip()
                link = 'https://news.google.com' + headline['href'][1:]
                pub_time = parse_time(time_element['datetime'])
                results.append({'title': title, 'link': link, 'time': pub_time})
        
        # Sort results by time, latest first
        results.sort(key=lambda x: x['time'], reverse=True)
        return results[:20]  # Return only the latest 20 results
    
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return []

def parse_time(time_str):
    now = datetime.now(pytz.utc)
    if 'ago' in time_str:
        # Parse relative time
        value, unit = time_str.split()[0:2]
        value = int(value)
        if 'minute' in unit:
            delta = timedelta(minutes=value)
        elif 'hour' in unit:
            delta = timedelta(hours=value)
        elif 'day' in unit:
            delta = timedelta(days=value)
        else:
            return now  # Default to now if unable to parse
        return now - delta
    else:
        # Parse absolute time
        try:
            return datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc)
        except ValueError:
            return now  # Default to now if unable to parse

# Usage
news = get_google_news("Tata Motors Ltd")
if news:
    ist = pytz.timezone('Asia/Kolkata')
    for item in news:
        ist_time = item['time'].astimezone(ist)
        print(f"Title: {item['title']}")
        print(f"Link: {item['link']}")
        print(f"Time: {ist_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print()
else:
    print("No news articles were found.")
