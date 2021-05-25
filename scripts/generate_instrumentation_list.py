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

import logging
import os
import subprocess

from jinja2 import Template

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("instrumentation_list_generator")

_auto_generation_msg = """
# DO NOT EDIT. THIS FILE WAS AUTOGENERATED FROM templates/{source}.
# RUN `python scripts/generate_setup.py` TO REGENERATE.
"""
_template_dir = "templates"
_template_name = "instrumentation_setup.py.txt"
_prefix = "opentelemetry-instrumentation-"

_template = '''
{license}

{instrumentation}
'''


def main():
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    setuppy_tmpl = Template(
        open(
            os.path.join(root_path, _template_dir, _template_name), "r"
        ).read()
    )
    instrumentation_list_path = os.path.join(root_path, "opentelemetry-instrumentation/src/opentelemetry/instrumentation/instrumentations.py")
    print('>>>>>>>>>>>>>>>>>>>')
    print(instrumentation_list_path)
    print('>>>>>>>>>>>>>>>>>>>')

    base_instrumentation_path = os.path.join(root_path, "instrumentation")

    all_instrumentations = []
    for pkg in os.listdir(base_instrumentation_path):
        pkg_path = os.path.join(base_instrumentation_path, pkg)
        if not os.path.isdir(pkg_path):
            continue

        name = subprocess.check_output("python setup.py --name", shell=True, cwd=pkg_path)
        version = subprocess.check_output("python setup.py --version", shell=True, cwd=pkg_path)
        print(name, version)




if __name__ == "__main__":
    main()
