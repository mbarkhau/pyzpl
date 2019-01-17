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
import operator

__version__ = '0.1.9'

PY2 = sys.version_info.major < 3

if PY2:
    str = unicode
    vitems = operator.methodcaller('viewitems')
else:                                     #python 3
    # str supports necessary decode
    vitems = operator.methodcaller('items')
    

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

    
def load_stream(bytes_stream, encoding='utf-8', emit_empty=False):
    """for propname,value in load_stream(linelist, encoding='utf-8', emit_empty=False): ...

    Arguments:
        linelist   - an iterable that yields one ZPL line at a time ('file' is a suitable
                     argument)
        encoding   - character encoding. Any value suitable for str.decode(), default is 'utf-8'
        emit_empty - whether to emit value-less nodes or not (default=false)

    This is a generator function, yielding one tuple of (propname, value) for each name/value
    property in the stream. The 'propname' is itself a tuple of components, representing the
    hierarchical path to the property.

    As a stream parser, it carries no state (other that the property's place in the hierarchy).
    """

    propname_stack = tuple()
    prev_indent_lvl = 0
    for lineno, raw_line in enumerate(bytes_stream):
        decoded_line = raw_line.decode(encoding)
        cleaned_line = decoded_line.rstrip("\r\n")
        line = cleaned_line.lstrip(" ")
        if not line:
            continue                      # skip blank lines
        spaces = len(cleaned_line) - len(line)

        if spaces % 4 != 0:
            msgfmt = "Illegal indent on line {}, must be a multiple of 4\n\t{}"
            raise ValueError(msgfmt.format(lineno, repr(cleaned_line)))

        indent_lvl = spaces // 4
        if indent_lvl <= prev_indent_lvl:
            propname_stack = propname_stack[:indent_lvl]
            # this represents an outdent?

        nv_pair_match = NAME_VALUE_PAIR_RE.match(line)
        if nv_pair_match:
            propname_stack += (nv_pair_match.group(1).strip(),)
            prev_indent_lvl = indent_lvl
            yield propname_stack, nv_pair_match.group(2)
        else:
            propname_match = NAME_RE.match(line)
            if propname_match:
                propname_stack += (propname_match.group(1),)
                prev_indent_lvl = indent_lvl
                if emit_empty: yield propname_stack, ""

def load(
        bytes_stream,
        encoding='utf-8',
        flat=False,
        name_sep=":",
        dict_cls=collections.OrderedDict):
    """tree = load(linelist, encoding='utf-8', flat=False, name_sep=':', dict_cls=collections.OrderedDict)
    
    loads a ZPL stream (an iterable yielding one line at a time) into an mapping object
    (instance of dict_cls). Internally, it calls load_stream, passing the linelist and the
    encoding, and assembles the results into the collection.

    Note that this interface does not allow for repeated property names at the same level. The
    ZPL spec is not clear about if this is defined behavior or not. It also does not support
    properties having both values and children.
    """

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


class ZPLnode(object):
    """ZPLnode(name=root, value=None)

    This class represents a single node in a ZPL hierarchy. Per the ZPL specification:

        ZPL is designed to represent a property set, where each property has a name
        and a value. Properties are hierarchical, i.e. properties can contain other
        properties.

    Also, preserving the stream-like properties of a ZPL sequence, the order in which nodes
    appear is preserved
    """

    def __init__(self, **kw):
        self._name = kw.get("name", "root")
        self._value = kw.get("value", None)
        self._parent = kw.get("parent", None)
        if (self._parent):
            self._level = self._parent._level + 1
            self._parent._children.append(self)
        else:
            self._level = 0
        self._children = []

    def get(self, path, query=(None,), name_sep=':'):
        """get(path, query=None, name_sep=':')

        Retrieve the node described by 'path' and (optionally) matching 'query'

        path is a tuple of names, or a string of 'name_sep' delimited parts, corresponding to
        the hierarchy of nodes

        query is an optional value to compare the value of matching nodes against. It is
        either a single string, in which case only the last node is filtered, or it is a tuple
        of values corresponding to the last len(query) parts. It may not be a 'name_sep'
        delimited string, because values are arbitrary values

        Examples:
            buffer = b'''
            thing = foo
                bar = baz

            thing = flu
                bar = bat

            thing
                bar = bar

            depth
                item
                    value = 1
'''
            cfg = pyzpl.parse_cfg(buffer)

            thing = cfg.get("thing")
            assert thing.get('bar').value == 'baz'  # first matching 'thing' node

            thing = cfg.get("thing", "flu")
            assert thing.value == "flu"

            bar = cfg.get( ("thing", "bar"), query="bar" )   # get the bar of the any 'thing' node where the value is "bar"
            assert bar.value == "bar"

            bar = cfg.get( ("thing", "bar"), query=("flu", None) )   # get the 'bar' of the 'thing=flu' node
            assert bar.value == "bat"
        """

        # if this is a string, turn it into a list
        if (hasattr(path, 'encode')): path = path.split(name_sep)

        # check the query; if it is a string, turn it into a list. If it is short, pad it with 'None'
        if (hasattr(query, 'encode')): query = (query,)

        if (len(query) > len(path)) : raise ValueError("too many query parameters for path", "path="+str(path), "query="+str(query))

        # left-pad the query with None
        query = (None,)*(len(path)-len(query)) + query

        # Turn the parts and querys into a list that can be sliced
        args = [ x for x in zip(path, query) ]
        match, node = self.__match(args)

        result = node if match else None
        return result

    def __match(self, args):
        node = None
        part, filt = args[0]

        for child in self.children:
            match = (child.name == part and ( (not filt) or filt == child.value ))
            if match:
                node = child
                if len(args) > 1:
                    match, node = child.__match(args[1:])
                if match: break
            
        return match, node

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, val):
        self._value = val

    @property
    def level(self):
        return self._level

    @property
    def children(self):
        return iter(self._children)       # todo if only an iterable is appropriate.

    def __str__(self):
        result = ""
        if (self.level != 0):             # don't print node information for the root node
#            result += str(self.level) + ":"
            result += "    " * (self.level-1)
            result += str(self.name);
            if (self.value): result += " = " + self.value

        for child in self.children:
            result += "\n" + str(child)

        return result

def load_cfg(bytes_stream, encoding='utf-8'):
    """root_node = load_cfg(linelist, encoding='utf-8')

    loads a ZPL stream (an iterable yielding one line at a time) into a hiearchy of ZPLnode
    instances, returning the root node.
    """

    print("Entering load_cfg")
    root = ZPLnode()
    roots = [root,]
    for propnames, value in load_stream(bytes_stream, encoding=encoding, emit_empty=True):
        # call load_stream with emit_empty=True to make it return all nodes. This simplifies
        # creating sub-trees, and ensures that the maximum increate in depth is 1
        level = len(propnames)

        # Because the maximum increase in level is 1, and we slice 'roots' to the current
        # level, this works regardless of indent
        roots = roots[:level]         # levels are 0-based, so the length is always 1 more than the level
        parent = roots[level-1]
        name = propnames[-1]
        child = ZPLnode( name=name, value=value, parent=parent )
        roots.append(child)

    return root


def main(args=sys.argv[1:]):
    print("Not Implemented")


if __name__ == '__main__':
    sys.exit(main())
