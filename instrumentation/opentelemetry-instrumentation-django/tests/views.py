from django.http import HttpResponse

from opentelemetry.util.http import HTTP_HEADER_ACCESS_CONTROL_EXPOSE_HEADERS


def traced(request):  # pylint: disable=unused-argument
    return HttpResponse()


def traced_template(request, year):  # pylint: disable=unused-argument
    return HttpResponse()


def error(request):  # pylint: disable=unused-argument
    raise ValueError("error")


def excluded(request):  # pylint: disable=unused-argument
    return HttpResponse()


def excluded_noarg(request):  # pylint: disable=unused-argument
    return HttpResponse()


def excluded_noarg2(request):  # pylint: disable=unused-argument
    return HttpResponse()


def route_span_name(
    request, *args, **kwargs
):  # pylint: disable=unused-argument
    return HttpResponse()


def response_header(request):  # pylint: disable=unused-argument
    response = HttpResponse()
    response["Server-Timing"] = "abc; val=1"
    response[HTTP_HEADER_ACCESS_CONTROL_EXPOSE_HEADERS] = "X-Test-Header"
    return response
