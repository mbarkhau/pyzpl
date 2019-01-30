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

UNUSED_TEST_CASES = [
]

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



FIXTURE_3_DATA = b"""
# Basement printer
node = basement
    ip = 10.1.2.3
    port = 2001
    device = Canon Pixma

# Front door security camera
node = front door
    ip = 10.1.2.10
    port = 8080
    device = Wyze Cam Pan 1080p

# Nursery bio-monitor
node = nursery
    ip = 10.1.2.42
    port = 8888
    device = Mimo Sleep Tracker

# Our users
authorized_users
    authorization = simple

    user = alex
        privilege = super-user

    user = thomas
        privilege = user

    user = mark
        privilege = user
""".lstrip()

FIXTURE_3_OUT = b"""
node = basement
    ip = 10.1.2.3
    port = 2001
    device = Canon Pixma
node = front door
    ip = 10.1.2.10
    port = 8080
    device = Wyze Cam Pan 1080p
node = nursery
    ip = 10.1.2.42
    port = 8888
    device = Mimo Sleep Tracker
authorized_users
    authorization = simple
    user = alex
        privilege = super-user
    user = thomas
        privilege = user
    user = mark
        privilege = user
""".strip()


def test_hiearchical():
    """test the Config file parser and interface
    """
    cfg = pyzpl.load_cfg(io.BytesIO(FIXTURE_3_DATA))
    assert cfg != None

    # "subscript" access
    node = cfg["node"]                    # get the first node
    assert node != None
    assert node.value == "basement"

    node = cfg["node=front door"]         # query selection
    assert node != None
    assert node.value == "front door"

    # Negative test
    with pytest.raises(KeyError) as excinfo:
        node = cfg["door"]
    assert "door" in str(excinfo.value)

    with pytest.raises(KeyError) as excinfo:
        node = cfg["node=garage"]
    assert "node=garage" in str(excinfo.value)


    # get() access
    node = cfg.get("node")                # get the first node (unqualified)
    assert node.value == "basement"

    # sub-element navigation
    ip1 = node.get("ip")                  # relative to the sub-tree retrieved above
    ip2 = cfg.get( ("node","ip") )        # still the first node, hierarchicaly qualified
    ip3 = cfg.get("node:ip")              # string based fully qualified
    assert ip1.value == "10.1.2.3"
    assert ip1 == ip2 == ip3

    auth = cfg.get("authorized_users:authorization")
    assert auth != None
    assert auth.value == "simple"

    # chained "indexing"
    auth = cfg["authorized_users"]["authorization"]
    assert auth != None
    assert auth.value == "simple"

    # filtering
    node = cfg.get("node", query="nursery")
    assert node.value == "nursery"

    # When the query is the leaf node, a simple query may be used
    user = cfg.get( ("authorized_users", "user"), query="mark" )
    assert user != None
    assert user.value == "mark"

    # This test demonstrates how filters can be applied at any level. The query is extended to
    # include implicit 'None' values on the left, as needed to balance the depth of the path. So
    #   --- path ---            --- query ---
    #   ('a', 'b', 'c')         ('1', None)
    # is equivalent to
    #   cfg.get('a', query=None).get('b', query='1').get('c', query=None)

    priv = cfg.get( ("authorized_users", "user", "privilege"), query=("alex", None) )
    assert priv != None
    assert priv.value == "super-user"

    # iteration
    children = [ child for child in cfg.children ]

    assert len(children) == 4
    node = children[0]
    assert node.name == "node"
    assert node.value == "basement"

    node = children[1]
    assert node.name == "node"
    assert node.value == "front door"                # order is preserved

    node = children[2]
    assert node.name == "node"
    assert node.value == "nursery"

    node = children[3]
    assert node.name == "authorized_users"
    assert node.value == ""                         # this node has no value

    # return is a dump of the tree (root node). It should match the
    # input, less blank lines and comments
    assert str(cfg).strip().encode() == FIXTURE_3_OUT

