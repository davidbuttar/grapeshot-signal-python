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
use of your API keys counts against your monthly quota. If you believe that one
of your keys has been compromised then you can generate a new key to replace it
via the `Developer Portal`_.

Create a :code:`SignalClient` instance
--------------------------------------

Optionally create a file config_local.py somewhere on your python load
path.

.. literalinclude:: py_snippets/config_local.py
   :caption: config_local.py

You should replace the key with your own API key.



.. include:: ./links.rst
