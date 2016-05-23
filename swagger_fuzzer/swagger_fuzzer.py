# -*- coding: utf-8 -*-
""" Swagger Fuzzer helps you do fuzzing testing on your Swagger APIs.
"""
import argparse
from urllib.parse import urlparse, urlunparse

import requests
from hypothesis import given, settings as hsettings, note
from swagger_spec_validator.util import get_validator

from .strategy import data
from .validators import VALIDATORS
from .swagger_helpers import get_request

parser = argparse.ArgumentParser()
parser.add_argument('spec_url', help="The Swagger spec url")
parser.add_argument('-n', '--number', dest='iterations',
                    default=1000000, type=int,
                    help='Maximum number of iterations (default: 100000)')
parser.add_argument('-s', '--standard-http-code', dest='http_code',
                    action='append', type=int,
                    help='Standards http codes, no need to declare them in '
                         'swagger spec, default: 200, 404, 405')


def main():
    args = parser.parse_args()
    if args.http_code is None:
        args.http_code = [200, 405, 404]
    do(args)


def to_curl_command(request):
    """ Convert a requests preparred request to curl command
    """
    command = "curl -i -X {method}{headers} -d '{data}' '{uri}'"
    method = request.method
    uri = request.url
    data = request.body
    if data is None:
        data = ''
    headers = ["{0}: '{1}'".format(k, v) for k, v in request.headers.items()]
    headers = " -H ".join(headers)
    if headers:
        headers = " -H {} ".format(headers)
    return command.format(method=method, headers=headers, data=data, uri=uri)


def do(settings):
    PARSED_HOST = urlparse(settings.spec_url)

    swagger_spec = requests.get(settings.spec_url)
    swagger_spec.raise_for_status()
    SPEC = swagger_spec.json()

    validator = get_validator(SPEC, settings.spec_url)
    validator.validate_spec(swagger_spec.json(), settings.spec_url)

    SPEC_HOST = urlunparse(list(PARSED_HOST)[:2] + [SPEC['basePath']] + ['', '', ''])

    s = requests.Session()

    @given(data())
    @hsettings(max_examples=settings.iterations)
    def swagger_fuzzer(data):
        request = get_request(data, SPEC, SPEC_HOST)
        note("Curl command: {}".format(to_curl_command(request)))

        result = s.send(request)

        for validator in VALIDATORS:
            validator(SPEC, request, result, settings)

    # Call the function
    swagger_fuzzer()

if __name__ == '__main__':
    main()
    # swagger_fuzzer()
