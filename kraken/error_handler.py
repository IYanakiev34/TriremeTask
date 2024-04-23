import kraken.exceptions as exceptions

class KrakenErrorHandler():
    def _get_error(self, data):
        if isinstance(data, dict) and 'error' in data:
            error = data['error']
            for err in error:
                if err in exceptions.EXCEPTIONS:
                    return exceptions.EXCEPTIONS[err]
        return None

    def check_for_error(self, data):
        if len(data.get('error', [])) == 0 and "result" in data:
            return data["result"]

        exc = self._get_error(data)
        if exc:
            raise exc(data['error'])
        return data
        