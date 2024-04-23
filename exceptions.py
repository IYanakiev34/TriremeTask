import functools


def docstring_message(cls):
    """Decorates an exception to make its docstring its default message.
    https://stackoverflow.com/questions/49224770/default-message-in-custom-exception-python/66491013#66491013
    """
    # Must use cls_init name, not cls.__init__ itself, in closure to avoid recursion
    cls_init = cls.__init__ 
    @functools.wraps(cls.__init__)
    def wrapped_init(self, msg=cls.__doc__, *args, **kwargs):
        cls_init(self, msg, *args, **kwargs)
    cls.__init__ = wrapped_init
    return cls

@docstring_message
class KrakenAPIError(Exception):
    """An error occurred while processing the request."""

@docstring_message
class KrakenInvalidArgumentsError(Exception):
    """Invalid arguments were passed to the API."""

@docstring_message
class KrakenRateLimitError(Exception):
    """Rate limit exceeded."""

@docstring_message
class KrakenUnknownAssetPair(Exception):
    """Unknown asset pair."""

EXCEPTIONS = {
    "EGeneral:Invalid arguments": KrakenInvalidArgumentsError,
    "EOrder:Rate limit exceeded": KrakenRateLimitError,
    "EQuery:Unknown asset pair": KrakenUnknownAssetPair
}

