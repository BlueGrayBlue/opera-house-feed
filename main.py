from flask import Flask, Response
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import requests
from datetime import datetime, timezone

app = Flask(__name__)

@app.route('/')
def rss_feed():
    base_url = "https://www.sydneyoperahouse.com"
    whats_on_url = f"{base_url}/whats-on"

    try:
        response = requests.get(whats_on_url)
        response.raise_for_status()
    except Exception as e:
        return Response(f"Failed to fetch events page: {e}", status=500)

    soup = BeautifulSoup(response.text, 'html.parser')
    cards = soup.select('.card.card--whats-on')

    fg = FeedGenerator()
    fg.title("Sydney Opera House Events")
    fg.link(href=whats_on_url, rel='alternate')
    fg.description("Live feed of Sydney Opera House events between 10–13 May 2025")
    fg.generator('python-feedgen')
    fg.lastBuildDate(datetime.now(timezone.utc))  # ✅ Fixed timezone-aware date

    # Define the target date range
    range_start = datetime(2025, 5, 10)
    range_end = datetime(2025, 5, 13)

    for card in cards:
        try:
            title = card.select_one('.card__heading-text').text.strip()
            category = card.select_one('.card__category').text.strip()
            date_text = card.select_one('.card__dates').text.strip()
            venue = card.select_one('.card__venue').text.strip()
            link = base_url + card.select_one('a')['href']

            # Convert event date range
            date_range = date_text.replace('–', '-').split('-')
            start_date = datetime.strptime(date_range[0].strip() + " 2025", "%d %b %Y")
            end_date = datetime.strptime(date_range[-1].strip() + " 2025", "%d %b %Y")

            # Filter: Only include events within 10–13 May 2025
            if end_date < range_start or start_date > range_end:
                continue

            # Add RSS item
            item = fg.add_entry()
            item.title(title)
            item.link(href=link)
            item.description(f"{category} | {date_text} | {venue}")
            item.pubDate(start_date.strftime("%a, %d %b %Y 00:00:00 +0000"))
            item.guid(link)

        except Exception as e:
            print("Skipping item due to error:", e)
            continue

    rss_output = fg.rss_str(pretty=True)
    return Response(rss_output, mimetype='application/rss+xml')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
