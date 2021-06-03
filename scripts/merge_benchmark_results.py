#!/usr/bin/env python3

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

import os
import subprocess
import sys

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(package):
    pattern = os.path.join("**", "**", "tests", "*{0}*-benchmark.json".format(package))
    command = (
        "jq -s '.[0].benchmarks = ([.[].benchmarks] | add) | if .[0].benchmarks == null then null else .[0] end'"
        " {0}"
    ).format(pattern)
    out = subprocess.check_output(command, shell=True, universal_newlines=True, cwd=root_path).strip()
    if out and out != "null":
        with open(os.path.join(root_path, "benchmark_results.json"), "w") as results:
            results.write(out)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: ./scripts/merge_benchmark_results.py <package-name>")
        sys.exit(1)
    main(sys.argv[1])

