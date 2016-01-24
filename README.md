weekender-scrapping
===================

a scrapy application to retrieve data from voyages-sncf mobi


Local setup
===========

    $ mkvirtualenv weekender-scrapping
    $ pip install -r requirements.txt


Executing
=========

    $ scrapyrt & watchmedo shell-command -R --command="pkill python; scrapyrt"

    $ curl 'http://localhost:9080/crawl.json' -X POST -d '{
        "request": {
            "url": "http://voyages-sncf.mobi",
            "meta": {
                "origin_name": "paris",
                "destination_name": "amsterdam"
            }
        },
        "spider_name": "voyagessncf_api"
    }' -H 'Content-Type: application/json'
