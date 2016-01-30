sncf.lol
========

a scrapyrt API to retrieve data from voyages-sncf website

Local setup
===========

    $ mkvirtualenv sncflol
    $ workon sncflol
    $ pip install -r requirements.txt
    $ ./bin/post_compile  # to install scrapyrt

Run Server
==========

    $ workon sncflol
    $ cd voyagessncf && scrapyrt

or if you want livereload, run `pip install watchdog` and then :

    $ scrapyrt & watchmedo shell-command --patterns="*.py;*.cfg" -R --command="pkill python; scrapyrt"

Run crawl from CLI
==================

Useful for debugging, especially to use the `inspect_response` helper.

    $ scrapy crawl voyagessncf -a origin_name=paris -a destination_name=amsterdam

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

