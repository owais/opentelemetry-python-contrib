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
# type: ignore

"""
OpenTelemetry Base Instrumentor
"""

from abc import ABC, abstractmethod
from logging import getLogger
from typing import Collection

from opentelemetry.instrumentation.resources import get_dependency_conflicts

_LOG = getLogger(__name__)


class BaseInstrumentor(ABC):
    """An ABC for instrumentors

    Child classes of this ABC should instrument specific third
    party libraries or frameworks either by using the
    ``opentelemetry-instrument`` command or by calling their methods
    directly.

    Since every third party library or framework is different and has different
    instrumentation needs, more methods can be added to the child classes as
    needed to provide practical instrumentation to the end user.
    """

    _instance = None
    _is_instrumented = False

    def __new__(cls, *args, **kwargs):

        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)

        return cls._instance

    @abstractmethod
    def instrumentation_dependencies(self) -> Collection[str]:
        """"Return the Python package name"""

    def _instrument(self, **kwargs):
        """Instrument the library"""

    @abstractmethod
    def _uninstrument(self, **kwargs):
        """Uninstrument the library"""

    def _check_dependency_conflicts(self) -> bool:
        dependencies = self.instrumentation_dependencies()
        return get_dependency_conflicts(dependencies)

    def instrument(self, **kwargs):
        """Instrument the library

        This method will be called without any optional arguments by the
        ``opentelemetry-instrument`` command.

        This means that calling this method directly without passing any
        optional values should do the very same thing that the
        ``opentelemetry-instrument`` command does.
        """

        if self._is_instrumented:
            _LOG.warning("Attempting to instrument while already instrumented")
            return None

        # check if instrumentor has any missing or conflicting dependencies
        conflict = self._check_dependency_conflicts()
        if conflict:
            _LOG.debug(conflict)
            return None

        result = self._instrument(  # pylint: disable=assignment-from-no-return
            **kwargs
        )
        self._is_instrumented = True
        return result

    def uninstrument(self, **kwargs):
        """Uninstrument the library

        See ``BaseInstrumentor.instrument`` for more information regarding the
        usage of ``kwargs``.
        """

        if self._is_instrumented:
            result = self._uninstrument(**kwargs)
            self._is_instrumented = False
            return result

        _LOG.warning("Attempting to uninstrument while already uninstrumented")

        return None


__all__ = ["BaseInstrumentor"]
