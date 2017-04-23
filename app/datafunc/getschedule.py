from lxml import html
import requests

url = "https://sfbaytransit.org/durant-av-shattuck-av/times"
page = requests.get(url)
tree = html.fromstring(page.content)
b = tree.xpath('div[@title="stoptimes"]')
print(b)
