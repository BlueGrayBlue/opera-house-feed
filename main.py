from flask import Flask, Response
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import requests
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def rss_feed():
    base_url = "https://www.sydneyoperahouse.com"
    html = requests.get(f"{base_url}/whats-on").text
    soup = BeautifulSoup(html, 'html.parser')
    cards = soup.select('.card.card--whats-on')

    fg = FeedGenerator()
    fg.title("Sydney Opera House Events")
    fg.link(href=f"{base_url}/whats-on", rel='alternate')
    fg.description("Live feed of Sydney Opera House events between 10–13 May 2025")

    range_start = datetime(2025, 5, 10)
    range_end = datetime(2025, 5, 13)

    for card in cards:
        try:
            title = card.select_one('.card__heading-text').text.strip()
            category = card.select_one('.card__category').text.strip()
            date_text = card.select_one('.card__dates').text.strip()
            venue = card.select_one('.card__venue').text.strip()
            link = base_url + card.select_one('a')['href']

            date_parts = date_text.replace('–', '-').split('-')
            start_date = datetime.strptime(date_parts[0].strip() + " 2025", "%d %b %Y")
            end_date = datetime.strptime(date_parts[-1].strip() + " 2025", "%d %b %Y")

            if end_date < range_start or start_date > range_end:
                continue

            entry = fg.add_entry()
            entry.title(title)
            entry.link(href=link)
            entry.description(f"{category} | {date_text} | {venue}")
            entry.pubDate(start_date.strftime("%a, %d %b %Y 00:00:00 +0000"))
            entry.guid(link)
        except:
            continue

    return Response(fg.rss_str(pretty=True), mimetype='application/rss+xml')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
