import platform

import requests
try:
    from urllib.parse import urljoin, urlunparse
except ImportError:  # pragma: no cover
    from urlparse import urljoin, urlunparse  # pragma: no cover
import grapeshot_signal.config as config
from .model import SignalModel, SignalModel, SignalStatus
from .errors import APIError, OverQuotaError


class SignalClient(object):
    """ A wrapper for the Signal web API.

        Args:

            api_key (str): An API key obtained from the `Developer Portal`_ The
               validity of the key is not checked at intialisation time, but
               invalid keys will result in errors when calling one of the get\_
               methods.


        .. _Developer Portal: https://api-portal.grapeshot.com/
    """

    def __init__(self, api_key):
        """Initialize an instance with an API key (bearer token.)"""

        super(SignalClient, self).__init__()
        self.api_key = api_key
        self.base_url = urlunparse(('https', config.api_host, '',
                                    None, None, None))

        # Note that the User-agent string contains the library name, the
        # libary version, and the python version. This will help us track
        # what people are using, and where we should concentrate our
        # development efforts.
        self.user_agent = (config.sdk_name + '/' + config.sdk_version + '/' +
                           platform.python_version())

    def _get_headers(self):
        """Create a dictionary for headers needed to make a request.

        #. Authorization
        #. User-agent
        """
        headers = {'User-Agent': self.user_agent}

        if self.api_key:
            headers['Authorization'] = 'Bearer ' + self.api_key
        return headers

    def _get(self, path=None, params=None, is_full_path=False):
        """
        Private
        Perform a GET request with headers.

        Args:
            path (str): API path (partial or full)
            params (dict): Query params dict
            is_full_path (boolean): if false, path is appended
                                    to api version prefix.

        Returns:
            page_model (SignalModel): model/JSON dict.

        Raises:
            APIError
            OverQuotaError
            requests.exceptions.ConnectionError
        """
        headers = self._get_headers()

        if is_full_path:
            base_url = self.base_url
        else:
            base_url = urljoin(self.base_url, config.api_version)

        api_url = urljoin(base_url, path)

        response = requests.get(api_url, params=params, headers=headers)

        if 200 <= response.status_code < 299:

            data = response.json()

            if (config.raise_over_quota and
                    data['status'] == SignalStatus.over_quota):
                raise OverQuotaError(data)

            return SignalModel(data)
        else:
            try:
                data = response.json()
            except ValueError:
                data = {'message': 'Unknown server error'}

            raise APIError(response.status_code, data)

    def get_page(self, url, embed=None):
        """
        Get analysis for a page (GET /v1/pages).

        Example:
            Get the segments for a webpage::

                model = client.get_page('http://example.org', rels.segments)

            Then access the embedded segments::

                utils.get_embedded(model, rels.segments)

        Args:
            url (str): URL of the webpage to analyze.
            embed (list of str or str): Entity relations to embed in
                               response. See values in rels.py.

        Returns:
            page_model (SignalModel): model/JSON dict.

        Raises:
            APIError
            OverQuotaError
            requests.exceptions.ConnectionError
        """
        params = {
            'url': url
        }

        if embed is not None:
            params['embed'] = embed

        return self._get('pages', params)

    def _post(self, path=None, params=None, post_data=None, is_full_path=False):
        """
        Private
        Perform a POST request with headers.

        Args:
            path (str): API path (partial or full)
            params (dict): Query params dict
            post_data (dict): Post data for request
            is_full_path (boolean): if false, path is appended
                                    to api version prefix.

        Returns:
            text_model (SignalModel): model/JSON dict.

        Raises:
            APIError
            OverQuotaError
            requests.exceptions.ConnectionError
        """
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"

        if is_full_path:
            base_url = self.base_url
        else:
            base_url = urljoin(self.base_url, config.api_version)

        api_url = urljoin(base_url, path)

        response = requests.post(api_url, json=post_data, params=params, headers=headers)

        if 200 <= response.status_code < 299:

            data = response.json()

            if (config.raise_over_quota and
                    data['status'] == SignalStatus.over_quota):
                raise OverQuotaError(data)

            return SignalModel(data)
        else:
            try:
                data = response.json()
            except ValueError:
                data = {'message': 'Unknown server error'}

            raise APIError(response.status_code, data)

    def get_text(self, text, embed=None):
        """
        Get analysis for text (GET /v1/text).

        Example:
            Get the segments for a webpage::

                model = client.get_text('This is some sample text.', rels.segments)

            Then access the embedded segments::

                utils.get_embedded(model, rels.segments)

        Args:
            text (str): Text to analyze.
            embed (list of str or str): Entity relations to embed in
                               response. See values in rels.py.

        Returns:
            text_model (SignalModel): model/JSON dict.

        Raises:
            APIError
            OverQuotaError
            requests.exceptions.ConnectionError
        """
        post_data = {
            "text": text
        }

        params = None
        if embed is not None:
            params = dict()
            params['embed'] = embed

        return self._post('text', params, post_data)

    def get_link(self, model, link_rel):
        """
        Gets the data for a link relation in a model.

        Example:
            Get the keywords for the a page::

                keywords_model = client.get_link(signal_model, rels.keywords)

        Args:
            model (dict): a model returned from a previous API call.
            link_rel (str): a link relation, see rels.py.

        Returns:
            signal_model (SignalModel): model/JSON dict.

        Raises:
            APIError
            OverQuotaError
            requests.exceptions.ConnectionError
        """
        href = model.get_link_href(link_rel)
        return self._get(href, is_full_path=True)
