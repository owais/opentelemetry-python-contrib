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

from pyramid.config import Configurator

from opentelemetry.instrumentation.pyramid import PyramidInstrumentor
from opentelemetry.test.test_base import TestBase
from opentelemetry.test.wsgitestutil import WsgiTestBase

# pylint: disable=import-error
from .pyramid_base_test import InstrumentationTest


class TestAutomatic(InstrumentationTest, TestBase, WsgiTestBase):
    _request_hook = None
    _response_hook = None

    def setUp(self):
        super().setUp()

        PyramidInstrumentor().instrument(request_hook=self.request_hook, response_hook=self.response_hook)

        self.config = Configurator()

        self._common_initialization(self.config)

    def tearDown(self):
        super().tearDown()
        with self.disable_logging():
            PyramidInstrumentor().uninstrument()

    def request_hook(self, *args, **kwargs):
        if self._request_hook:
            self._request_hook(*args, **kwargs)

    def response_hook(self, *args, **kwargs):
        if self._response_hook:
            self._response_hook(*args, **kwargs)

    def test_uninstrument(self):
        # pylint: disable=access-member-before-definition
        resp = self.client.get("/hello/123")
        self.assertEqual(200, resp.status_code)
        self.assertEqual([b"Hello: 123"], list(resp.response))
        span_list = self.memory_exporter.get_finished_spans()
        self.assertEqual(len(span_list), 1)

        PyramidInstrumentor().uninstrument()
        self.config = Configurator()

        self._common_initialization(self.config)

        resp = self.client.get("/hello/123")
        self.assertEqual(200, resp.status_code)
        self.assertEqual([b"Hello: 123"], list(resp.response))
        span_list = self.memory_exporter.get_finished_spans()
        self.assertEqual(len(span_list), 1)

    def test_tween_list(self):
        tween_list = "pyramid.tweens.excview_tween_factory"
        config = Configurator(settings={"pyramid.tweens": tween_list})
        self._common_initialization(config)
        resp = self.client.get("/hello/123")
        self.assertEqual(200, resp.status_code)
        self.assertEqual([b"Hello: 123"], list(resp.response))
        span_list = self.memory_exporter.get_finished_spans()
        self.assertEqual(len(span_list), 1)
        self.assertEqual(span_list[0].name, "/hello/{helloid}")

        PyramidInstrumentor().uninstrument()

        self.config = Configurator()

        self._common_initialization(self.config)

        resp = self.client.get("/hello/123")
        self.assertEqual(200, resp.status_code)
        self.assertEqual([b"Hello: 123"], list(resp.response))
        span_list = self.memory_exporter.get_finished_spans()
        self.assertEqual(len(span_list), 1)

    def test_hooks(self):
        def request_hook(span, request):
            span.update_name("name from hook")

        def response_hook(span, request, response):
            span.set_attribute('from_hook', 'hello otel')
            response.headers.add('hook-header', 'hello client')

        self._request_hook = request_hook
        self._response_hook = response_hook

        tween_list = "pyramid.tweens.excview_tween_factory"
        config = Configurator(settings={"pyramid.tweens": tween_list })
        self._common_initialization(config)
        resp = self.client.get("/hello/123")
        self.assertEqual(resp.headers['hook-header'], 'hello client')
        self.assertEqual(200, resp.status_code)
        self.assertEqual([b"Hello: 123"], list(resp.response))
        span_list = self.memory_exporter.get_finished_spans()
        self.assertEqual(len(span_list), 1)
        span = span_list[0] 
        self.assertEqual(span.name, "name from hook")
        self.assertIn('from_hook', span.attributes)
        self.assertIn(span.attributes['from_hook'], 'hello otel')

        self._request_hook = self._response_hook = None