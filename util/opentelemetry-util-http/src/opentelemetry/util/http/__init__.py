# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from os import environ
from re import compile as re_compile
from re import search
from typing import Callable, Collection, Optional, Tuple

from opentelemetry import trace


_root = r"OTEL_PYTHON_{}"

HTTP_HEADER_ACCESS_CONTROL_EXPOSE_HEADERS = "Access-Control-Expose-Headers"
ENV_HTTP_TRACE_RESPONSE_HEADER = "OTEL_PYTHON_HTTP_TRACE_RESPONSE_HEADER"


class ExcludeList:
    """Class to exclude certain paths (given as a list of regexes) from tracing requests"""

    def __init__(self, excluded_urls):
        self._excluded_urls = excluded_urls
        if self._excluded_urls:
            self._regex = re_compile("|".join(excluded_urls))

    def url_disabled(self, url: str) -> bool:
        return bool(self._excluded_urls and search(self._regex, url))


def get_traced_request_attrs(instrumentation):
    traced_request_attrs = environ.get(
        _root.format("{}_TRACED_REQUEST_ATTRS".format(instrumentation)), []
    )

    if traced_request_attrs:
        traced_request_attrs = [
            traced_request_attr.strip()
            for traced_request_attr in traced_request_attrs.split(",")
        ]

    return traced_request_attrs


def get_excluded_urls(instrumentation):
    excluded_urls = environ.get(
        _root.format("{}_EXCLUDED_URLS".format(instrumentation)), []
    )

    if excluded_urls:
        excluded_urls = [
            excluded_url.strip() for excluded_url in excluded_urls.split(",")
        ]

    return ExcludeList(excluded_urls)


def get_trace_response_headers(
    span: trace.Span,
) -> Collection[Tuple[str, str]]:
    header_name = environ.get(ENV_HTTP_TRACE_RESPONSE_HEADER, "").strip()
    if not header_name:
        return tuple()

    if span is trace.INVALID_SPAN:
        return tuple()

    ctx = span.get_span_context()
    if ctx is trace.INVALID_SPAN_CONTEXT:
        return tuple()

    return (
        (HTTP_HEADER_ACCESS_CONTROL_EXPOSE_HEADERS, header_name),
        (
            header_name,
            'traceparent;desc="00-{trace_id}-{span_id}-{sampled}"'.format(
                trace_id=trace.format_trace_id(ctx.trace_id),
                span_id=trace.format_span_id(ctx.span_id),
                sampled="01" if ctx.trace_flags.sampled else "00",
            ),
        ),
    )
