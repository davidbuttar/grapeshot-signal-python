
class OverQuotaError(Exception):

    def __init__(self, data):
        Exception.__init__(self, "Grapeshot Over Quota")
        self.data = data

    def href(self):
        """
        url of the endpoint which is over quota.
        """
        return self.data['_links']['self']['href']


class APIError(Exception):

    def __init__(self, code, data, headers):
        error = data.get('error', '')
        message = data.get('message', '')
        Exception.__init__(self, "{0} {1}: {2}".format(code, error, message))
        self._code = code
        self.data = data
        self.headers = headers

    def __str__(self):

        msg = "{0} {1}: {2}".format(self.status_code(),
                                    self.error(),
                                    self.message())
        errors = self.errors()
        if errors:
            for err in errors:
                msg += "\n{0}: {1}".format(err.get('field'), err.get('message'))

        return msg

    def __unicode__(self):
        return self.__str__()

    def status_code(self):
        return self._code

    def error(self):
        return self.data.get('error', 'Unknown Error')

    def message(self):
        return self.data.get('message', '')

    def errors(self):
        return self.data.get('errors')
