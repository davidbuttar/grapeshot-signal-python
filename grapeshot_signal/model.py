from collections import namedtuple
import grapeshot_signal.config as config
from .errors import OverQuotaError


class SignalStatus:
    """The status of a SignalModel"""

    ok = 'ok'
    queued = 'queued'
    error = 'error'
    over_quota = 'over_quota'


class SignalModel(dict):

    def is_ok(self):
        """
        Returns True if ok status
        """
        return self['status'] == SignalStatus.ok

    def is_queued(self):
        """
        Returns True if queued status
        """
        return self['status'] == SignalStatus.queued

    def is_error(self):
        """
        Returns True if error status
        """
        return self['status'] == SignalStatus.error

    def is_over_quota(self):
        """
        Returns true if over_quota status
        """
        return self['status'] == SignalStatus.over_quota

    def url(self):
        """
        Returns the url of a pages endpoint call or None for a text endpoint call
        """
        return self.get('url', None)

    def text(self):
        """
        Returns the text of a text endpoint call or None for a pages endpoint call
        """
        return self.get('text', None)

    def get_link_href(self, link_relation):
        """
        Return the link href for a link relation.
        'link_relation' the link relation for which href is required.
        See rels.py.

        Returns None if the link does not exist.
        """
        assert link_relation is not None

        result = None

        link = self['_links'].get(link_relation)
        if link:
            result = link.get('href')

        return result

    def get_embedded(self, link_relation):
        """
        Return the embedded model for link_relation.
        The returned object can be treated as a model in its own right.

        The link relation of the embedded object must have been specified
        when the model was originally requested. May not be None.
        'link_relation' the link relation for which href is required. May
        not be None.

        Returns None if the embedded object does not exist.
        """

        assert link_relation is not None

        result = None

        embedded_object = self.get('_embedded')
        if embedded_object:
            result = embedded_object.get(link_relation)
            if result is not None:
                if config.raise_over_quota and result['status'] == SignalStatus.over_quota:
                    raise OverQuotaError(result)

                result = SignalModel(result)

        return result