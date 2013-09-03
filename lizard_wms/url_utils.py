from collections import OrderedDict
import urllib
import urlparse


def combine_url_and_params(url, params):
    """URL is an URL, perhaps with existing GET params. Params is a
    dictionary of params, probably coming from request.GET in some
    view. We add the params to the URL and return the result URL."""

    # This is adapted from
    # http://stackoverflow.com/questions/2506379/add-params-to-given-url-in-python

    if not params:
        return url

    urlparts = list(urlparse.urlparse(url))

    # We use an ordereddict to make the order of params in the result
    # predictable, for unit testing.
    query = OrderedDict(urlparse.parse_qsl(urlparts[4]))
    query.update(params)
    urlparts[4] = urllib.urlencode(query)

    # Always have a / after the domain part
    if urlparts[2] == '':
        urlparts[2] = '/'

    return urlparse.urlunparse(urlparts)
