import requests
import platform
try:
    from urllib.parse import urljoin, urlunparse
except ImportError:  # pragma: no cover
    from urlparse import urljoin, urlunparse  # pragma: no cover
import grapeshot_signal.config as config
from .model import SignalModel, SignalStatus
from .errors import APIError, OverQuotaError


class SignalClient(object):

    def __init__(self, api_key):
        """
        Initialize an instance with an API key (bearer token.)
        """
        super().__init__()
        self.api_key = api_key
        self.base_url = urlunparse(('https', config.api_host, '', None, None, None))

        # Note that the User-agent string contains the library name, the
        # libary version, and the python version. This will help us track
        # what people are using, and where we should concentrate our
        # development efforts.
        self.user_agent = (config.sdk_name + '/' + config.sdk_version + '/' +
                           platform.python_version())

    def _get_headers(self):
        """
        Private
        Get all the headers we're going to need:
        1. Authorization
        3. User-agent
        """
        headers = {'User-Agent': self.user_agent }

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

            if config.raise_over_quota and data['status'] == SignalStatus.over_quota:
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

        Example usage: client.get_page('http://example.org',
                                       rels.segments)

        If you specify embeds, you can access them in the result
        model using utils.get_embedded(model, link_rel).

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

    def get_link(self, model, link_rel):
        """
        Gets the data for a link relation in a model.
        For example, if you request a page and then want to get the
        keywords for the page, you can call:

        keywords_model = client.get_link(page_model, rels.keywords)

        Args:
            model (dict): a model returned from a previous API call.
            link_rel (str): a link relation, see rels.py.

        Returns:
            page_model (SignalModel): model/JSON dict.

        Raises:
            APIError
            OverQuotaError
            requests.exceptions.ConnectionError
        """
        href = model.get_link_href(link_rel)
        return self._get(href, is_full_path=True)
