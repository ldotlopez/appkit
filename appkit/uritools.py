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
    if not parsed.scheme:
        parsed._replace(scheme='http')

    if parsed.scheme in ['http', 'https']:
        # Path must be at least a single slash
        path = parsed.path or '/'
        # Remove multiple slashes
        path, dummy = re.subn(r'/+', '/', path)
        # Update url
        parsed = parsed._replace(path=path)

    return parse.urlunparse(parsed)


def alter_query_params(uri, params, **urlencode_kwargs):
    urlencode_kwargs['doseq'] = urlencode_kwargs.get('doseq', True)

    parsed = parse.urlparse(uri)

    qs = parse.parse_qs(parsed.query)
    for (param, value) in params.items():
        if value is None:
            try:
                del(qs[param])
            except KeyError:
                continue

        else:
            qs[param] = value

    return parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path or '/',
                             parsed.params,
                             parse.urlencode(qs, **urlencode_kwargs),
                             parsed.fragment))


def paginate_by_query_param(uri, key, default=1):
    """
    Utility generator for easy pagination
    """

    try:
        current = int(query_param(uri, key, default))
    except ValueError:
        current = default

    while True:
        yield alter_query_params(uri, {key: current})
        current = current + 1


def query_param(uri, key, default=None):
    q = parse.parse_qs(parse.urlparse(uri).query)
    try:
        return q[key][-1]
    except KeyError:
        return default
