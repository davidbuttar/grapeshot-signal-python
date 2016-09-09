
====================
Grapeshot Signal SDK
====================

The grapeshot signal sdk provides a wrapper to the Grapeshot Signal
web service which provides high quality realtime analysis of web
pages. See http://devportal-test.grapeshot.co.uk for details.

Detailed documentation is available in the "docs" directory.

Quick Start
-----------

1. Install via pip::

     pip install grapeshot-signal-sdk

   For alternative installation methods see the detailed documentation.

2. Obtain an api key via http://devportal-test.grapeshot.co.uk.

3. In your code create an instance of SignalClient, passing in your api key::

     from grapeshot_signal import SignalClient

     signal_client = SignalClient("your api key")

4. Use the client to obtain information about web pages::

     from grapeshot_signal import rels

     url =  "http://news.bbc.co.uk" #for example
     page = signal_client.get_page(url, embed=[rels.keywords, rels.segments])
		
     do_my_stuff(results)

