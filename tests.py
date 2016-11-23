# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import io
import collections
import functools as ft

import pytest
import pyzpl


FIXTURE_1_DATA = b"""
1. ZPL configuration file example
1. This format is designed to be trivial to write and parse
#
context
    iothreads = 1
    verbose = 1      #   Ask for a trace

main
    type = zmq_queue
    frontend
        option
            hwm = 1000
            swap = 25000000
            subscribe = "#2"
        bind = tcp://eth0:5555
    backend
        bind = tcp://eth0:5556
""".strip()


FIXTURE_1_TREE = {
    "context": {
        "iothreads": "1",
        "verbose"  : "1"
    },
    "main"   : {
        "type"    : "zmq_queue",
        "frontend": {
            "option": {
                "hwm"      : "1000",
                "swap"     : "25000000",
                "subscribe": "#2",
            },
            "bind": "tcp://eth0:5555",
        },
        "backend" : {
            "bind": "tcp://eth0:5556"
        },
    }
}


FIXTURE_1_FLAT_TREE = {
    "context:iothreads"             : "1",
    "context:verbose"               : "1",
    "main:type"                     : "zmq_queue",
    "main:frontend:option:hwm"      : "1000",
    "main:frontend:option:swap"     : "25000000",
    "main:frontend:option:subscribe": "#2",
    "main:frontend:bind"            : "tcp://eth0:5555",
    "main:backend:bind"             : "tcp://eth0:5556",
}


FIXTURE_2_DATA = b"""
version = 1.0
apps
    listener
        context
            iothreads = 1
            verbose = 1
        devices
            main
                type = zmq_queue
                sockets
                    frontend
                        type = SUB
                        option
                            hwm = 1000
                            swap = 25000000
                        bind = tcp://eth0:5555
                    backend
                        bind = tcp://eth0:5556
""".lstrip()


FIXTURE_2_TREE = {
    "version": "1.0",
    "apps": {
        "listener": {
            "context": {
                "iothreads": "1",
                "verbose": "1"
            },
            "devices": {
                "main": {
                    "type": "zmq_queue",
                    "sockets": {
                        "frontend": {
                            "type": "SUB",
                            "option": {
                                "hwm": "1000",
                                "swap": "25000000"
                            },
                            "bind": "tcp://eth0:5555"
                        },
                        "backend": {
                            "bind": "tcp://eth0:5556"
                        }
                    }
                }
            }
        }
    }
}


NESTED_1_DATA = b"""
root
    branch
        leafname = leafval
""".lstrip()


NESTED_1_TREE = {
    "root": {
        "branch": {
            "leafname": "leafval"
        }
    }
}


NESTED_1_TREE_FLAT = {
    "root:branch:leafname": "leafval"
}


Case = collections.namedtuple("Case", ['name', 'call', 'data', 'expected'])


LOAD_TEST_CASES = [
    Case(
        name="loads spec doc",
        call=pyzpl.loads,
        data=FIXTURE_1_DATA,
        expected=FIXTURE_1_TREE,
    ),
    Case(
        name="loads spec doc flat",
        call=ft.partial(pyzpl.loads, flat=True),
        data=FIXTURE_1_DATA,
        expected=FIXTURE_1_FLAT_TREE,
    ),
    Case(
        name="load_stream spec doc",
        call=(lambda data: {":".join(k): v for k, v in pyzpl.load_stream(io.BytesIO(data))}),
        data=FIXTURE_1_DATA,
        expected=FIXTURE_1_FLAT_TREE
    ),
    Case(
        name="loads config",
        call=pyzpl.loads,
        data=FIXTURE_2_DATA,
        expected=FIXTURE_2_TREE,
    ),
    Case(
        name="loads nested",
        call=pyzpl.loads,
        data=NESTED_1_DATA,
        expected=NESTED_1_TREE,
    ),
    Case(
        name="dumps nested 1",
        call=pyzpl.dumps,
        data=NESTED_1_TREE,
        expected=NESTED_1_DATA.decode()
    ),
    Case(
        name="dumps nested 1 flat",
        call=pyzpl.dumps,
        data=NESTED_1_TREE_FLAT,
        expected=NESTED_1_DATA.decode()
    ),
    Case(
        name="dumps hello world",
        call=pyzpl.dumps,
        data={"hello": "world"},
        expected="hello = world\n"
    ),
    Case(
        name="dumps val with hash",
        call=pyzpl.dumps,
        data={"propname": "world with # hash (not a comment)"},
        expected="""propname = "world with # hash (not a comment)"\n"""
    ),
    # TODO (mb 2016-11-22): Test cases for
    #  - A value that starts with a quote and does not end in a
    #    matching quote is treated as unquoted.
]


@pytest.mark.parametrize("name, call, data, expected", LOAD_TEST_CASES)
def test_load(name, call, data, expected):
    result = call(data)

    print("######## " * 10)
    print(data)
    print("######## " * 10)
    print(result)
    print("######## " * 10)
    print(expected)
    print("######## " * 10)

    assert result == expected


def test_full_cycle():
    tree1 = pyzpl.loads(FIXTURE_2_DATA)
    data1 = pyzpl.dumps(tree1).encode('ascii')
    tree2 = pyzpl.loads(data1)
    data2 = pyzpl.dumps(tree2).encode('ascii')

    assert FIXTURE_2_TREE == tree1
    assert FIXTURE_2_TREE == tree2

    assert FIXTURE_2_DATA == data1
    assert FIXTURE_2_DATA == data2
