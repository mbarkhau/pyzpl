# -*- coding: utf-8 -*-
"""ZPL: ZeroMQ Property Language

ZPL is an ASCII text format that uses whitespace - line endings
and indentation - for framing and hierarchy. ZPL data consists
of a series of properties encoded as name/value pairs, one per
line, where the name may be structured, and where the value is
an untyped string.

https://github.com/zeromq/rfc/tree/master/4

Notes:

 - Whitespace is significant only before property names and
   inside values.
 - Text starting with '#' is discarded as a comment.
 - Each non-empty line defines a property consisting of a name
   and an optional value.
 - Values are untyped strings which the application may
   interpret in any way it wishes.
 - An entire value can be enclosed with single or double quotes,
   which do not form part of the value.
 - Any printable character except the closing quote is valid in
   a quoted string.
 - A value that starts with a quote and does not end in a
   matching quote is treated as unquoted.
 - There is no mechanism for escaping quotes or other characters
   in a quoted string.
 - The only special characters in ZPL are: whitespace, '#', '=',
   and single and double quotes.
 - Hierarchy is signaled by indentation, where a child is
   indented 4 spaces more than its parent.
 - The first non-whitespace character in a ZPL file is always
   either '#' or an alphanumeric character.
 - Whitespace following after a value is discarded unless within
   valid quotes.

Names SHALL match this grammar:

name = *name-char
name-char = ALPHA | DIGIT | "$" | "-" | "_" | "@" | "." | "&" | "+" | "/"

The following sequences are treated as line-endings:

    newline (%x0A)
    carriage-return (%x0D)
    carriage-return followed by newline (%x0A %x0D)

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import io
import re
import sys
import collections
import operator as op

__version__ = '0.1.8'

PY2 = sys.version_info.major < 3

str = unicode if PY2 else str   # noqa

vitems = op.methodcaller('viewitems') if PY2 else op.methodcaller('items')


NAME_RE = re.compile(r"^(?P<propname>[A-Z0-9\$_\-@\.&+/]+).*$", re.VERBOSE | re.IGNORECASE)


NAME_VALUE_PAIR_RE = re.compile(r"""
    ^
    (?P<propname>[A-Z0-9\$_\-@\.&+/]+)
    \s*=\s*
    \"?
    (?P<propvalue>[^\"]+?)
    \"?
    (?P<trailing_comment>\s*\#.*?)?
    $
""", re.VERBOSE | re.IGNORECASE)


def load_stream(bytes_stream, encoding='utf-8'):
    propname_stack = tuple()
    prev_indent_lvl = 0
    for lineno, raw_line in enumerate(bytes_stream):
        decoded_line = raw_line.decode(encoding)
        cleaned_line = decoded_line.rstrip("\r\n")
        line = cleaned_line.lstrip(" ")
        if not line:
            continue
        spaces = len(cleaned_line) - len(line)

        if spaces % 4 != 0:
            msgfmt = "Illegal indent on line {}, must be a multiple of 4\n\t{}"
            raise ValueError(msgfmt.format(spaces, repr(cleaned_line)))

        indent_lvl = spaces // 4
        if indent_lvl <= prev_indent_lvl:
            propname_stack = propname_stack[:indent_lvl]

        nv_pair_match = NAME_VALUE_PAIR_RE.match(line)
        if nv_pair_match:
            propname = nv_pair_match.group(1).strip()
            value = nv_pair_match.group(2)
            propnames = propname_stack + (propname,)
            prev_indent_lvl = indent_lvl
            yield propnames, value
        else:
            propname_match = NAME_RE.match(line)
            if propname_match:
                propname_stack += (propname_match.group(1),)
                prev_indent_lvl = indent_lvl


def load(
        bytes_stream,
        encoding='utf-8',
        flat=False,
        name_sep=":",
        dict_cls=collections.OrderedDict):

    tree = dict_cls()
    for propnames, value in load_stream(bytes_stream, encoding=encoding):
        if flat:
            flatkey = name_sep.join(propnames)
            tree[flatkey] = value
        else:
            ctx = tree
            for subkey in propnames[:-1]:
                if subkey not in ctx:
                    ctx[subkey] = dict_cls()
                ctx = ctx[subkey]
            ctx[propnames[-1]] = value

    return tree


def loads(data, *args, **kwargs):
    return load(io.BytesIO(data), *args, **kwargs)


def dump_lines(tree_items, name_sep=":"):
    for name, val in tree_items:
        if isinstance(name, str) and name_sep in name:
            name = name.split(name_sep)
        if isinstance(name, (tuple, list)):
            # TODO (mb 2016-11-23): handle indent
            indent = ""
            for parent_name in name[:-1]:
                yield indent + parent_name
                indent += "    "
            name = name[-1]
        else:
            indent = ""

        if isinstance(val, dict):
            yield name
            sub_items = vitems(val)
            for subline in dump_lines(sub_items):
                yield "    " + subline
            continue

        if not isinstance(val, str):
            val = str(val)

        if '#' in val:
            val_str = '"' + val + '"'
        else:
            val_str = val

        yield indent + name + " = " + val_str


def dumps(tree, *args, **kwargs):
    lines = dump_lines(vitems(tree), *args, **kwargs)
    return "\n".join(lines) + "\n"


def main(args=sys.argv[1:]):
    print("Not Implemented")


if __name__ == '__main__':
    sys.exit(main())
