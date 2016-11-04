Tutorial
========

Obtaining the SDK.
------------------

Installation with pip
^^^^^^^^^^^^^^^^^^^^^

From pre-packaged sources::

  pip install grapeshot-signal-sdk

From github, e.g. ::

  pip install git+git://github.com/grapeshot/grapeshot-signal-python.git@master

We recommend using a `virtual environment`_.

Checkout with git
^^^^^^^^^^^^^^^^^

Using pip will install the sdk itself. The sources for this documentation and
some example client code are not included with the packaged distribution. Use
git to obtain a complete copy of the repository ::

  git clone git@github.com:grapeshot/grapeshot-signal-python.git


Download
^^^^^^^^

A complete copy of the sdk sources can be download from github, e.g ::
  wget https://github.com/grapeshot/grapeshot-signal-python/archive/master.zip


Check Import
------------

Verify your installation::

  (gs-sdk) [paul@localhost grapeshot-signal-python]$ python
  Python 3.5.1 (default, Sep 19 2016, 10:16:17)
  [GCC 6.1.1 20160621 (Red Hat 6.1.1-3)] on linux
  Type "help", "copyright", "credits" or "license" for more information.
  >>> import grapeshot_signal
  >>>


An import error::

  >>> import grapeshot_signal
  Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
  ImportError: No module named grapeshot_signal
  >>>

indicates a problem with installation, which should be resolved before proceeding.

Obtain an API key
-----------------

Create an account at the `Developer Portal`_ and obtain an API key. Every
account has an associated monthly quota. The free tier enables development and
experimentation without incurring any cost. Paid subscriptions provide higher
monthly quotas. Therefore you should take care with your API keys, since any
use of your API keys counts against your monthly quota.

Use a :class:`.SignalClient` instance
-------------------------------------

Optionally create a file config_local.py somewhere on your python load
path.

.. literalinclude:: py_snippets/config_local.py
   :caption: config_local.py

You should replace the key with your own API key. This step can be skipped, but
provides convenient access to your API key.

Then create a :class:`.SignalClient` instance and use it obtain information about a web page::

  >>> from grapeshot_signal import SignalClient, config, rels
  >>> client = SignalClient(config.api_key)
  >>> page_model = client.get_page("http://www.bbc.co.uk/sport/cycling/37691574", [rels.keywords, rels.segments]) # try any web page here
  >>> page_model.is_ok()
  True


See :ref:`errors` below if :meth:`.is_ok` returns ``False``.


   >>> kw_model = page_model.get_embedded(rels.keywords)
   >>>

Note that this is itself a :class:`.SignalModel` instance. In this case it has a ``'keywords'`` property::

  >>> pprint(kw_model['keywords'])
  [{'name': 'Bradley Wiggins', 'score': 2.154},
  {'name': 'Chris Froome', 'score': 2.154},
  {'name': 'Sport', 'score': 2.071},
  {'name': "cycling's", 'score': 1.466},
  {'name': 'Team Sky', 'score': 1.466},
  {'name': 'Tour de France', 'score': 1.466},
  {'name': 'allergies', 'score': 1.167},
  {'name': 'steroid', 'score': 1.167},
  {'name': 'treatment', 'score': 1.167},
  {'name': 'asthma', 'score': 0.725},
  {'name': 'athletes', 'score': 0.725},
  {'name': 'banned substances', 'score': 0.725},
  {'name': 'Dave Brailsford', 'score': 0.725},
  {'name': "Giro d'Italia", 'score': 0.725},
  {'name': 'Mark Cavendish', 'score': 0.725},
  {'name': 'medical', 'score': 0.725},
  {'name': 'Olympian', 'score': 0.725},
  {'name': 'respiratory', 'score': 0.725},
  {'name': 'Rio Olympics', 'score': 0.725},
  {'name': 'symptoms', 'score': 0.725},
  {'name': 'therapeutic', 'score': 0.725},
  {'name': 'UCI', 'score': 0.725}]


Note that:

#. The scores associated with each keyword are a measure of the relative
   importance of each keyword within the page, but are not necessarily
   comparable with scores obtained from different pages.
#. keywords can be short phrases (as in the above example).

The segments for the model are also available::

  >>> pprint(page_model.get_embedded(rels.segments)['segments'][0])
  {'matchterms': [{'name': 'Bradley Wiggins', 'score': 2.154},
                  {'name': 'Chris Froome', 'score': 2.154},
                  {'name': 'Sport', 'score': 2.071},
                  {'name': "cycling's", 'score': 1.466},
                  {'name': 'Team Sky', 'score': 1.466},
                  {'name': 'Tour de France', 'score': 1.466},
                  {'name': 'athletes', 'score': 0.725},
                  {'name': 'Dave Brailsford', 'score': 0.725},
                  {'name': "Giro d'Italia", 'score': 0.725},
                  {'name': 'Mark Cavendish', 'score': 0.725},
                  {'name': 'Olympics', 'score': 0.725},
                  {'name': 'UCI', 'score': 0.725}],
  'name': 'gs_sport',
  'score': 48.262}
  >>>

The segments each have a name. A brief description for each is here:
https://api-portal.grapeshot.com/documentation/segment_descriptions. The
value for the ``'matchterms'`` key gives the keywords that contributed towards
the categorisation of the page with this segment.


.. _errors:

Errors
------
In some circumstances :meth:`.is_ok` could return ``False``, for example::

  >>> oops_page = client.get_page("http://grapeshot.com/zzzz")
  >>> oops_page.is_ok()
  False

We can check the page status directly::

  >>> oops_page['status']
  'queued'

A status of `queued` means that this page has not (recently) been crawled. The
act of requesting information about the page will ensure that it is crawled
soon. So requesting information again gives a different result (if the page has
been crawled)::

  >>> oops_page = client.get_page("http://grapeshot.com/zzzz")
  >>> oops_page['status']
  'error'

In these circumstances the model will have a `error_code` and `error_message` keys::

  >>> oops_page['error_message']
  'gx_notfound'
  >>> oops_page['error_message']
  'Grapeshot was unable to analyse this page because the site returned a Not Found (404) error when our crawler tried to visit it.'


The codes and associated error messages are documented here: https://api-portal.grapeshot.com/documentation/error_codes. In this case we've asked for a non-existent page.



.. include:: ./links.rst
