""" Validators
"""


def check_result_status_code(spec, request, response, settings):
    """ Check that response status code is either a "standard" one
    like 404, 405, 200 (use -s cli argument to change it) or one
    of the declared one globally or for the path in swagger configuration
    """
    status_code = int(response.status_code)
    endpoint_path = request.build_context['endpoint_path']
    authorized = spec['paths'][endpoint_path][request.method.lower()]['responses'].keys()

    # Default means all status code are allowed
    if "default" in authorized:
        return

    allowed = set(settings.http_code).union(map(int, authorized))

    if status_code not in allowed:
        raise AssertionError("Request on {!r} returned status_code {}, not in declared one {}".format(request.url, response.status_code, list(allowed)))


def no_server_error(spec, request, response, settings):
    """ Check that response status code is different than 500
    """
    if response.status_code == 500:
        raise AssertionError("Request on {!r} returns status_code {}".format(URL, response.status_code))


def no_body_format_declaration(spec, request, response, settings):
    """ Check that for each post path, a body format is declared
    """
    body_args = request.build_context.get('body_args')
    if request.build_context['body_args'] and request.build_context.get('request_body_format') is None:
        raise AssertionError("Body parameters but no declared format for endpoint {}: {}".format(endpoint, body_args))


def valid_output_mime(spec, request, response, settings):
    """ Check that each request returns with a content-type that is declared
    """
    global_valids = spec.get('consumes', [])

    endpoint_path = request.build_context['endpoint_path']
    path = spec['paths'][endpoint_path][request.method.lower()]
    local_valids = path.get('consumes', [])

    if local_valids:
        valids = local_valids
    else:
        valids = global_valids

    if response.headers['Content-Type'] not in valids:
        raise AssertionError("Response content-type {} is not declared: {}".format(response.headers['Content-Type'], valids))


VALIDATORS = [
    no_server_error,
    no_body_format_declaration,
    check_result_status_code,
    valid_output_mime
]
