import feedparser
import json
import urllib
import urllib2
from flask import Flask, render_template, request

app = Flask(__name__)

RSS_FEEDS = {	'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
				'cnn': 'http://rss.cnn.com/rss/edition.rss',
				'fox': 'http://feeds.foxnews.com/foxnews/latest',
				'iol': 'http://www.iol.co.za/cmlink/1.640',
				'reuters': 'http://feeds.reuters.com/news/artsculture',
				'nrk': 'http://www.nrk.no/toppsaker.rss'}
DEFAULTS = {"publication":"bbc",
			"city":"London,UK",
			"currency_from": "GBP",
			"currency_to": "USD"}
CURRENCY_URL = "https://openexchangerates.org/api/latest.json?app_id=e636aa08e8654d089e50cf1d740aaf77"
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=0f4a44a433984f4558fc80bc239fa889"
def get_rate(frm, to):
	all_currency = urllib2.urlopen(CURRENCY_URL).read()
	parsed = json.loads(all_currency).get('rates')
	frm_rate = parsed.get(frm.upper())
	to_rate = parsed.get(to.upper())
	return (to_rate/frm_rate, parsed.keys())

def get_weather(query):
	api_url = WEATHER_URL
	query = urllib.quote(query)
	url = api_url.format(query)
	data = urllib2.urlopen(url).read()
	parsed = json.loads(data)
	weather = None
	if parsed.get("weather"):
		weather = {
			"description":parsed["weather"][0]["description"],
			"temperature":parsed["main"]["temp"],
			"city":parsed["name"],
			"country":parsed["sys"]["country"]
		}
	return weather

def get_news(query):
	if not query or query.lower() not in RSS_FEEDS:
		publication = DEFAULTS["publication"]
	else:
		publication = query.lower()
	feed = feedparser.parse(RSS_FEEDS[publication])
	# first_article = feed['entries'][0]
	weather = get_weather("Oxford,UK")
	return feed['entries']
@app.route('/')
def home():
	publication = request.args.get('publication')
	if not publication:
		publication = DEFAULTS['publication']
	articles = get_news(publication)
	city = request.args.get('city')
	if not city:
		city = DEFAULTS['city']
	weather = get_weather(city)
	currency_from = request.args.get("currency_from")
	if not currency_from:
		currency_from = DEFAULTS["currency_from"]
	currency_to = request.args.get("currency_to")
	if not currency_to:
		currency_to = DEFAULTS["currency_to"]
	rate, currencies = get_rate(currency_from, currency_to)
	return render_template("home.html", articles=articles, weather=weather, currency_from=currency_from, currency_to=currency_to, rate=rate, currencies=sorted(currencies))
if __name__ == '__main__':
	app.run(port=5000, debug = True)
