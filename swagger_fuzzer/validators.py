""" Validators
"""

STANDARDS_STATUS_CODE = [200, 405, 404]


def check_result_status_code(spec, context, result, URL):
    status_code = int(result.status_code)
    authorized = spec['paths'][context['endpoint_path']][context['method_name']]['responses'].keys()

    # Default means all status code are allowed
    if "default" in authorized:
        return

    allowed = set(STANDARDS_STATUS_CODE).union(map(int, authorized))

    if status_code not in allowed:
        raise AssertionError("Request on {!r} returned status_code {}, not in declared one {}".format(URL, result.status_code, list(allowed)))


def no_server_error(spec, context, result, URL):
    if result.status_code == 500:
        raise AssertionError("Request on {!r} returns status_code {}".format(URL, result.status_code))


def no_body_format_declaration(spec, context, request_body_format, endpoint):
    if context['body_args'] and context.get('request_body_format') is None:
        raise AssertionError("Body parameters but no declared format for endpoint {}: {}".format(endpoint, body_args))


VALIDATORS = [
    no_server_error,
    no_body_format_declaration,
    check_result_status_code
]
