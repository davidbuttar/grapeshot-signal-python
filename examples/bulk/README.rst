========================
Batch processing of URLs
========================

These scripts provide illustrate making repeated calls to the API to categorise
webpages, and then performing some post-processing on the results.

Quickstart
==========

#. Obtain an API Key via https://api-portal.grapeshot.com

#. Create a file config_local.py::

     apikey = "your api key here"

#. Pass a file containing one url per line to bulk.py::

     ./bulk.py --infile=my_url_file.txt --outfile=url-data.json

#. Examine the output.

#. Produce a summary of the results::

     ./summarise.py --infile=url-data.json --outfile=summary.json


bulk.py
=======

This script takes a list of urls delimited by newlines; calls the Signal Api
for each url and summarises the categories (aka "segments") matching the page's
contents.

Detailed help on the various options can be obtained::

  $ ./bulk.py --help
  usage: bulk.py [-h] [--infile [INFILE]] [--outfile [OUTFILE]]
                 [--apikey APIKEY] [--consumers CONSUMERS] [--retry429]
                 [--no-retry429] [--pause429] [--no-pause429]

  Make multiple requests to the Grapeshot OpenAPI server.

  optional arguments:
    -h, --help            show this help message and exit
    --infile [INFILE]     file containing one url per line, defaults to stdin
    --outfile [OUTFILE]   file containing results, defaults to stdout
    --apikey APIKEY       api key for the api server
    --consumers CONSUMERS
                          number of url consumers
    --retry429            retry rate limited requests
    --no-retry429         do not retry rate limited requests
    --pause429            pause on 429
    --no-pause429         do not pause on 429, not recommended - just for testing


Repeating "queued" urls
~~~~~~~~~~~~~~~~~~~~~~~

If urls have not been crawled then the result status will be queued and crawled
subsequently (usually within a few minutes). The queued urls can be retried e.g.::

  $ ./bulk.py --infile urls.txt > url-data.json
  100%|████████████████████████████████████████████████████████| 101/101 [00:00<00:00, 170130.40it/s]
  $ cat url-data.json | jq 'select(.result.status=="queued") | .url' -r | ./bulk.py url-data-2.json
  6it [00:00, 34711.48it/s]


A file containing the final result from the two passes can be created::

  $ cat url-data.json | jq -c 'select(.result.status!="queued")| .' > noq.json
  $ cat noq.json  url-data-2.json > final.json


A couple of lines of output might look like this (pretty printed) ::

  $ tail -n 2 final.json |jq .
  {
    "try_count": 1,
    "request_time": 1481636766.3704753,
    "url": "http://www.mumsnet.com/talk/am_i_being_unreasonable/1953420-to-be-terrified-for-my-friend?pg=12",
    "client_id": 4,
    "response_time": 1481636767.1446118,
    "result": {
      "segments": [
        {
          "score": 32.366,
          "name": "gs_law_misc",
          "matchterms": [
            "police"
          ]
        },
        {
          "score": 30.748,
          "name": "gs_law",
          "matchterms": [
            "police"
          ]
        },
        {
          "score": 18.819,
          "name": "gs_predicts_mothers_day",
          "matchterms": [
            "daughter"
          ]
        },
        {
          "score": 12.165,
          "name": "gs_family_marriage",
          "matchterms": [
            "marriage"
          ]
        },
        {
          "score": 12.165,
          "name": "gs_society",
          "matchterms": [
            "marriage"
          ]
        }
      ],
      "status": "ok",
      "language": "en"
    }
  }
  {
    "try_count": 1,
    "request_time": 1481636766.3698153,
    "url": "http://www.wattpad.com/18305337-no-love-tyga-love-story-filler",
    "client_id": 2,
    "response_time": 1481636768.404048,
    "result": {
      "status": "error",
      "error_code": "gx_notfound"
    }
  }


The first of these is typical for a url that has been crawled and
categorised. The second is an example of a url that returned 404 at the time
our crawler attempted to visit it.

summary.py
==========

bulk.py produces json to facilitate ease of post-processing. summary.py
illustrates computing some summary statistics from an output file.


elastic.py
==========

Arrange for a suitable elasticsearch/kibana cluster. For smallish data::

  $ docker run --rm  sebp/elk

Then use elastic.py to populate your index::

  $ ./elastic.py --infile=final.json
