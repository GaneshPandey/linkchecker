# taken from http://docs.python.org/2/library/httplib.html

DNS_ERROR = 666
ERROR_DOWNLOAD_CODE = 667
TIMEOUT = 668
UNKNOWN_ERROR = 669


HTTP_STATUS_CODES = {
    DNS_ERROR: u'dns_error',
    ERROR_DOWNLOAD_CODE: u'error_downloading',
    UNKNOWN_ERROR: u'unknown',
    TIMEOUT: u'timeout',
    100: u'continue',
    101: u'switching_protocols',
    102: u'processing',
    200: u'ok',
    201: u'created',
    202: u'accepted',
    203: u'non_authoritative_information',
    204: u'no_content',
    205: u'reset_content',
    206: u'partial_content',
    207: u'multi_status',
    226: u'im_used',
    300: u'multiple_choices',
    301: u'moved_permanently',
    302: u'found',
    303: u'see_other',
    304: u'not_modified',
    305: u'use_proxy',
    307: u'temporary_redirect',
    400: u'bad_request',
    401: u'unauthorized',
    402: u'payment_required',
    403: u'forbidden',
    404: u'not_found',
    405: u'method_not_allowed',
    406: u'not_acceptable',
    407: u'proxy_authentication_required',
    408: u'request_timeout',
    409: u'conflict',
    410: u'gone',
    411: u'length_required',
    412: u'precondition_failed',
    413: u'request_entity_too_large',
    414: u'request_uri_too_long',
    415: u'unsupported_media_type',
    416: u'requested_range_not_satisfiable',
    417: u'expectation_failed',
    422: u'unprocessable_entity',
    423: u'locked',
    424: u'failed_dependency',
    426: u'upgrade_required',
    500: u'internal_server_error',
    501: u'not_implemented',
    502: u'bad_gateway',
    503: u'service_unavailable',
    504: u'gateway_timeout',
    505: u'http_version_not_supported',
    507: u'insufficient_storage',
    510: u'not_extended',
}


def get_code(code):
    if code not in HTTP_STATUS_CODES:
        code = UNKNOWN_ERROR

    return HTTP_STATUS_CODES.get(code)
