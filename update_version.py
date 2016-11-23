# -*- coding: utf-8 -*-
"""Update version number (semver) in python source file

Usage:
    update_version (--major|--minor|--patch)
    cb -h | --help

Options:
    -h --help               Show this screen.
    --major                 Increment version like so 1.2.3 -> 2.0.0
    --minor                 Increment version like so 1.2.3 -> 1.3.0
    --patch                 Increment version like so 1.2.3 -> 1.2.4
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import io
import re
import sys


PY2 = sys.version_info.major < 3

str = unicode if PY2 else str   # noqa


VERSION_STRING_RE = re.compile(r"""
^
__version__
\s* = \s*
[\"\']
(?P<version>\d+\.\d+\.\d+)
[\"\']
\s*
$
""", re.VERBOSE | re.MULTILINE)


def inc_version(inctype, path):
    if not os.path.isfile(path):
        print("ERROR: No such file", path)
        return 1

    with io.open(path, mode='r', encoding='utf-8') as fh:
        cur_data = fh.read()

    cur_version_match = VERSION_STRING_RE.search(cur_data)
    if not cur_version_match:
        print("ERROR: No version number found in file", path)
        print("\tVersion number must match the pattern", VERSION_STRING_RE.pattern)
        return 1

    cur_version_line = cur_version_match.group(0)
    cur_version = cur_version_match.groupdict()['version']
    cur_major, cur_minor, cur_patch = cur_version.split(".")
    new_major, new_minor, new_patch = cur_major, cur_minor, cur_patch

    if inctype == '--major':
        new_major = str(int(cur_major) + 1)
        new_minor = new_patch = "0"
    if inctype == '--minor':
        new_minor = str(int(cur_minor) + 1)
        new_patch = "0"
    if inctype == '--patch':
        new_patch = str(int(cur_patch) + 1)

    new_version = ".".join((new_major, new_minor, new_patch))
    new_version_line = cur_version_line.replace(cur_version, new_version)
    new_data = cur_data.replace(cur_version_line, new_version_line)
    print(cur_version_line.strip(), "->", new_version_line.strip())

    tmp_path = path + ".version_updated"
    with io.open(tmp_path, mode='w', encoding='utf-8') as fh:
        fh.write(new_data)

    os.rename(tmp_path, path)

    return 0


def main(args=sys.argv[1:]):
    if '-h' in args or '--help' in args or len(args) != 2:
        print(__doc__)
        return

    inctype = args[0]
    if inctype not in ['--major', '--minor', '--patch']:
        print("Invalid argument: {}")
        print(__doc__)
        return 1

    path = args[1]
    return inc_version(inctype, path)


if __name__ == '__main__':
    sys.exit(main())
