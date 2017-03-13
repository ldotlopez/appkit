# -*- coding: utf-8 -*-

# Copyright (C) 2015 Luis López <luis@cuarentaydos.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA.


import re
from urllib import parse


def normalize(uri, default_protocol='http'):
    """
    Do some normalization on uri
    """
    assert isinstance(uri, str) and uri

    # Protocol relative URIs
    if uri.startswith('//'):
        uri = default_protocol + ':' + uri

    elif uri.startswith('/'):
        uri = 'file://' + uri

    parsed = parse.urlparse(uri)
    path, dummy = re.subn(r'/+', '/', parsed.path or '/')
    parsed = parsed._replace(path=path)

    return parse.urlunparse(parsed)


def alter_query_param(uri, key, value, safe='/'):
    """
    Replace the value of key in the query string of uri
    If key doesn't exists it's added
    If value is None key it's deleted
    """
    assert isinstance(uri, str) and uri
    assert isinstance(key, str) and uri
    assert value is None or (isinstance(value, str))

    parsed = parse.urlparse(uri)
    tmp = parse.parse_qsl(parsed.query)

    found = False

    qsl = []
    for (k, v) in tmp:
        if k == key:
            found = True
            if value is None:
                continue
            v = value

        if v is not None:
            qsl.append((k, v))

    if value and not found:
        qsl.append((key, value))

    return parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path,
                             parsed.params,
                             parse.urlencode(qsl, doseq=True, safe=safe),
                             parsed.fragment))


def paginate_by_query_param(uri, key, default=1):
    """
    Utility generator for easy pagination
    """

    assert isinstance(uri, str) and uri
    assert isinstance(key, str) and key
    assert isinstance(default, int)

    while True:
        yield alter_query_param(uri, key, str(default))
        default = default + 1


def query_param(uri, key, default=None):
    """
    Extract a value from a query string
    """
    assert isinstance(uri, str) and uri
    assert isinstance(key, str) and key
    assert default is None or (isinstance(default, str) and default)

    q = parse.parse_qs(parse.urlparse(uri).query)
    if key in q:
        return q[key][-1]
    else:
        return default
