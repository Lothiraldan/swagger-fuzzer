# -*- coding: utf-8 -*-
""" Swagger Fuzzer helps you do fuzzing testing on your Swagger APIs.
"""
import sys
import json
from datetime import datetime
from urllib.parse import urlparse, urlunparse

import requests
import hypothesis.strategies as st
from furl import furl
from hypothesis import given, settings, assume
from swagger_spec_validator.util import get_validator

from .swagger_helpers import CustomTransformation
from .strategy import data

SPEC_URL = sys.argv[1]
PARSED_HOST = urlparse(SPEC_URL)

swagger_spec = requests.get(SPEC_URL)
swagger_spec.raise_for_status()
SPEC = swagger_spec.json()

validator = get_validator(swagger_spec.json(), SPEC_URL)

validator.validate_spec(swagger_spec.json(), SPEC_URL)

SPEC_HOST = urlunparse(list(PARSED_HOST)[:2] + [SPEC['basePath']] + ['', '', ''])

s = requests.Session()

STANDARDS_STATUS_CODE = [200, 405, 404]


class CustomJsonEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return super().default(o)


def get_ref(ref):
    assert ref.startswith('#/')
    splitted = ref.lstrip('#/').split('/')

    referenced_to = SPEC

    for path in splitted:
        referenced_to = referenced_to[path]

    return referenced_to


def get_item_path_acceptable_format(path_item):
    if path_item.get('consumes'):
        return path_item['consumes']

    return SPEC.get('consumes')


def _get_filtered_parameter(path_item, in_):
    parameters = path_item.get('parameters')
    filtered_params = [p for p in parameters if p['in'] == in_]
    non_converted_params = {p['name']: p for p in filtered_params}
    return CustomTransformation(get_ref).transform(non_converted_params)


def check_result_status_code(context, result, URL):
    status_code = int(result.status_code)
    authorized = SPEC['paths'][context['endpoint_path']][context['method_name']]['responses'].keys()

    # Default means all status code are allowed
    if "default" in authorized:
        return

    allowed = set(STANDARDS_STATUS_CODE).union(map(int, authorized))

    if status_code not in allowed:
        raise AssertionError("Request on {!r} returned status_code {}, not in declared one {}".format(URL, result.status_code, list(allowed)))


def no_server_error(context, result, URL):
    if result.status_code == 500:
        raise AssertionError("Request on {!r} returns status_code {}".format(URL, result.status_code))


def no_body_format_declaration(context, request_body_format, endpoint):
    if context['body_args'] and context.get('request_body_format') is None:
        raise AssertionError("Body parameters but no declared format for endpoint {}: {}".format(endpoint, body_args))


VALIDATORS = [
    no_server_error,
    no_body_format_declaration,
    check_result_status_code
]


@given(data())
@settings(max_examples=100000)
def swagger_fuzzer(data):
    endpoint_path = data.draw(st.sampled_from(SPEC['paths'].keys()), 'URL')
    endpoint = SPEC['paths'][endpoint_path]

    method_name = data.draw(st.sampled_from(endpoint.keys()), 'METHOD')
    endpoint = endpoint[method_name]

    path_params = _get_filtered_parameter(endpoint, 'path')
    path_args = data.draw(st.fixed_dictionaries(path_params), 'QUERY_STRING')

    query_params = _get_filtered_parameter(endpoint, 'query')
    query_args = data.draw(st.fixed_dictionaries(query_params), 'QUERY_ARGS')

    body_params = _get_filtered_parameter(endpoint, 'body')
    if body_params:
        body_args = data.draw(body_params['body'], 'BODY_ARGS')
    else:
        body_args = None

    valid_request_body_format = get_item_path_acceptable_format(endpoint)

    request_data = None
    request_headers = {"X-User": "56e2f82a30781f1d92abeb91"}

    if body_args:
        # no_body_format_declaration(body_args, valid_request_body_format, endpoint)
        if body_args and valid_request_body_format is None:
            # Force a request format, swagger ui seems to force json format
            valid_request_body_format = ["application/json"]

        request_body_format = data.draw(st.sampled_from(valid_request_body_format), 'request_body_format')

        request_headers['Content-Type'] = request_body_format
        if request_body_format == 'application/x-www-form-urlencoded':
            request_data = body_args
        elif request_body_format == 'application/json':
            request_data = json.dumps(body_args, cls=CustomJsonEncoder)
        elif request_body_format == 'application/xml':
            pass
            # TODO Implement XML
        else:
            raise Exception(request_body_format)

    endpoint_url = endpoint_path.format(**path_args)
    assume('\x00' not in endpoint_url)

    # Generate request
    URL = furl(SPEC_HOST)
    URL = URL.join(endpoint_url.lstrip('/'))

    if query_args:
        URL = URL.add(args=query_args)

    result = s.request(method=method_name, url=URL.url, data=request_data,
                       headers=request_headers)

    for validator in VALIDATORS:
        validator(locals(), result, URL)


if __name__ == '__main__':
    swagger_fuzzer()
