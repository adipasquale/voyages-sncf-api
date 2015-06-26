weekender-scrapping
===================

a scrapy application to retrieve data from voyages-sncf mobi


Local setup
===========

    $ mkvirtualenv weekender-scrapping
    $ pip install -r requirements.txt


Executing
=========

    $ cd voyagessncf
    $ echo "" > output/output.json && scrapy crawl voyagessncf -o output/output.json -a origin_name=paris -a destination_name=amsterdam
