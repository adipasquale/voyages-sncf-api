sncf.lol
========

a scrapyrt API to retrieve data from voyages-sncf.mobi website

Local setup
===========

    $ mkvirtualenv sncflolapi
    $ workon sncflolapi
    $ pip install -r requirements.txt

If you run into problems with the `cryptography` package on a osx machine, run this:

    $ brew install pkg-config libffi openssl
    $ env LDFLAGS="-L$(brew --prefix openssl)/lib" CFLAGS="-I$(brew --prefix openssl)/include" pip install cryptography

(cf this [SO thread](http://stackoverflow.com/questions/22073516/failed-to-install-python-cryptography-package-with-pip-and-setup-py))

Run Server
==========

if you want livereload, run `pip install watchdog` and then :

    $ workon sncflolapi
    $ ./bin/run_local_server

Run crawl from CLI
==================

Useful for debugging, especially to use the `inspect_response` helper.

    $ cd voyagessncf
    $ scrapy crawl voyagessncf_mobi -a departure_city=paris -a arrival_city=avignon -a departure_date="01/04/2016" -a departure_hour="18h"

or

    $ scrapy crawl voyagessncf_com -a departure_city=paris -a arrival_city=avignon -a departure_date="10/03/2017" -a departure_hour="8"

Call API
========

    $ curl "http://localhost:9080/crawl.json?spider_name=voyagessncf_com&url=http%3A%2F%2Fwww.voyages-sncf.com&departure_date=10%2F03%2F2017&departure_city=paris&arrival_city=rennes&departure_hour=8"

