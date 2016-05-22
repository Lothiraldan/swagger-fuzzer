""" Validators
"""


def check_result_status_code(spec, context, result, URL, args_namespace):
    status_code = int(result.status_code)
    authorized = spec['paths'][context['endpoint_path']][context['method_name']]['responses'].keys()

    # Default means all status code are allowed
    if "default" in authorized:
        return

    allowed = set(args_namespace.http_code).union(map(int, authorized))

    if status_code not in allowed:
        raise AssertionError("Request on {!r} returned status_code {}, not in declared one {}".format(URL, result.status_code, list(allowed)))


def no_server_error(spec, context, result, URL, args_namespace):
    if result.status_code == 500:
        raise AssertionError("Request on {!r} returns status_code {}".format(URL, result.status_code))


def no_body_format_declaration(spec, context, result, URL, args_namespace):
    if context['body_args'] and context.get('request_body_format') is None:
        raise AssertionError("Body parameters but no declared format for endpoint {}: {}".format(endpoint, body_args))


VALIDATORS = [
    no_server_error,
    no_body_format_declaration,
    check_result_status_code
]
