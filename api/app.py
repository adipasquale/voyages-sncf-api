import uuid
import pymongo
from flask import Flask, request, jsonify
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import sys
sys.path.append("/Users/adipasquale/OpenSourceProjects/weekender-scrapping/voyagessncf")
from voyagessncf.spiders.voyagessncf_spider import VoyagesSncfSpider
from voyagessncf.settings import MONGO_URI, MONGO_DATABASE

project_settings = get_project_settings()
print "project_settings is %s" % MONGO_URI
process = CrawlerProcess()

app = Flask(__name__)

db_client = pymongo.MongoClient(MONGO_URI)
db = db_client[MONGO_DATABASE]


@app.route("/get_offers")
def get_offers():
  request_id = uuid.uuid4()
  args = {k: v[0] for k, v in request.args.iteritems()}
  args["request_id"] = request_id
  process.crawl(VoyagesSncfSpider, **args)
  process.start()  # the script will block here until the crawling is finished
  offers = list(db["offers"].find({"request_id": request_id}))
  offers
  return jsonify({"offers": offers})


if __name__ == '__main__':
  app.run(debug=True)
