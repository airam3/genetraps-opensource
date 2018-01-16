#!/usr/bin/env python2.7
#
# Copyright (C) 2013-2016 DNAnexus, Inc.
#
# This file is part of dx-toolkit (DNAnexus platform client libraries).
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may not
#   use this file except in compliance with the License. You may obtain a copy
#   of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

from __future__ import print_function, unicode_literals, division, absolute_import

import json
import re
import sys

preamble = '''# Do not modify this file by hand.
#
# It is automatically generated by src/api_wrappers/generatePythonAPIWrappers.py.
# (Run make api_wrappers to update it.)

from __future__ import print_function, unicode_literals, division, absolute_import

import sys

from dxpy import DXHTTPRequest
from dxpy.utils import Nonce
'''

class_method_template = '''def {wrapper_method_name}(input_params={{}}, always_retry={retry}, **kwargs):
    """
    Invokes the {route} API method.{wiki_ref}
    """{nonce_code}
    return DXHTTPRequest('{route}', {input_params}, always_retry=always_retry, **kwargs)
'''

object_method_template = '''def {wrapper_method_name}(object_id, input_params={{}}, always_retry={retry}, **kwargs):
    """
    Invokes the {route} API method.{wiki_ref}
    """{nonce_code}
    return DXHTTPRequest('/%s/{api_method_name}' % object_id, {input_params}, always_retry=always_retry, **kwargs)
'''

app_object_method_template = '''def {wrapper_method_name}(app_name_or_id, alias=None, input_params={{}}, always_retry={retry}, **kwargs):
    """
    Invokes the /app-xxxx/{api_method_name} API method.{wiki_ref}
    """{nonce_code}
    fully_qualified_version = app_name_or_id + (('/' + alias) if alias else '')
    return DXHTTPRequest('/%s/{api_method_name}' % fully_qualified_version, {input_params}, always_retry=always_retry, **kwargs)
'''


def make_nonce_code(accept_nonce):
    return ("\n    input_params_cp = Nonce.update_nonce(input_params)" if accept_nonce else "")


def make_input_params(accept_nonce):
    return ("input_params_cp" if accept_nonce else "input_params")


def make_wiki_ref(url):
    return ("\n\n    For more info, see: " + url) if url else ""


def make_class_method(wrapper_method_name, route, accept_nonce, retry=False, url=None):
    return class_method_template.format(wrapper_method_name=wrapper_method_name,
                                        route=route,
                                        retry=retry,
                                        wiki_ref=make_wiki_ref(url),
                                        nonce_code=make_nonce_code(accept_nonce),
                                        input_params=make_input_params(accept_nonce))


def make_object_method(wrapper_method_name, api_method_name, route, accept_nonce, retry=False, url=None):
    return object_method_template.format(wrapper_method_name=wrapper_method_name,
                                         api_method_name=api_method_name,
                                         route=route,
                                         retry=retry,
                                         wiki_ref=make_wiki_ref(url),
                                         nonce_code=make_nonce_code(accept_nonce),
                                         input_params=make_input_params(accept_nonce))


def make_app_object_method(wrapper_method_name, api_method_name, accept_nonce, retry=False, url=None):
    return app_object_method_template.format(wrapper_method_name=wrapper_method_name,
                                             api_method_name=api_method_name,
                                             retry=retry,
                                             wiki_ref=make_wiki_ref(url),
                                             nonce_code=make_nonce_code(accept_nonce),
                                             input_params=make_input_params(accept_nonce))


def camel_case_to_underscore(name):
    """
    Converts a camelCase string to a name_with_underscores.
    """
    return re.sub("[A-Z]+", lambda m: "_" + m.group(0).lower(), name, 0)

print(preamble)

for method in json.loads(sys.stdin.read()):
    route, signature, opts = method
    wrapper_method_name = camel_case_to_underscore(signature.split("(")[0])
    accept_nonce = opts.get('acceptNonce', False)
    retry = opts['retryable'] or accept_nonce
    if (opts['objectMethod']):
        root, oid_route, api_method_name = route.split("/")
        if oid_route == 'app-xxxx':
            print(make_app_object_method(wrapper_method_name,
                                         api_method_name,
                                         accept_nonce,
                                         retry=retry,
                                         url=opts.get('wikiLink', None)))
        else:
            print(make_object_method(wrapper_method_name,
                                     api_method_name,
                                     route,
                                     accept_nonce,
                                     retry=retry,
                                     url=opts.get('wikiLink', None)))
    else:
        print(make_class_method(wrapper_method_name,
                                route,
                                accept_nonce,
                                retry=retry,
                                url=opts.get('wikiLink', None)))
