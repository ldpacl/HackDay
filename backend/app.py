from flask import Flask, jsonify
from flask_caching import Cache
from flask_cors import CORS
from news_fetcher import get_google_news
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import pytz

app = Flask(__name__)
CORS(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/news/<stock_name>')
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_stock_news(stock_name):
    news = get_google_news(stock_name)
    return jsonify(news)

def update_cache():
    with app.app_context():
        stocks = ["Tata Motors Ltd", "Reliance Industries", "Infosys"]
        for stock in stocks:
            cache.delete('view//api/news/' + stock)
            get_stock_news(stock)

# Use a UTC timezone explicitly from pytz
scheduler = BackgroundScheduler(timezone=pytz.utc)
trigger = IntervalTrigger(minutes=5, timezone=pytz.utc)
scheduler.add_job(func=update_cache, trigger=trigger)
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True)
