sncf.lol
========

a scrapyrt API to retrieve data from voyages-sncf website

Local setup
===========

    $ mkvirtualenv sncfweekendapi
    $ workon sncfweekendapi
    $ pip install -r requirements.txt
    $ ./bin/post_compile  # to install scrapyrt

Run Server
==========

if you want livereload, run `pip install watchdog` and then :

    $ workon sncfweekendapi
    $ ./bin/run_local_server

Run crawl from CLI
==================

Useful for debugging, especially to use the `inspect_response` helper.

    $ cd voyagessncf
    $ scrapy crawl voyagessncf -a departure_city=paris -a arrival_city=avignon -a departure_date="01/04/2016" -a departure_hour="18h"

Call API
========

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

