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


FIXTURE_1 = b"""
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


FIXTURE_2 = b"""
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
"""


Case = collections.namedtuple("Case", ['call', 'data', 'expected'])


PARSE_TEST_CASES = [
    Case(
        call=pyzpl.loads,
        data=FIXTURE_1,
        expected={
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
    ),
    Case(
        call=ft.partial(pyzpl.loads, flat=True),
        data=FIXTURE_1,
        expected={
            "context:iothreads"             : "1",
            "context:verbose"               : "1",
            "main:type"                     : "zmq_queue",
            "main:frontend:option:hwm"      : "1000",
            "main:frontend:option:swap"     : "25000000",
            "main:frontend:option:subscribe": "#2",
            "main:frontend:bind"            : "tcp://eth0:5555",
            "main:backend:bind"             : "tcp://eth0:5556",
        }
    ),
    Case(
        call=pyzpl.loads,
        data=FIXTURE_2,
        expected={
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
    ),
    Case(
        call=(lambda data: {":".join(k): v for k, v in pyzpl.load_stream(io.BytesIO(data))}),
        data=FIXTURE_1,
        expected={
            "context:iothreads"             : "1",
            "context:verbose"               : "1",
            "main:type"                     : "zmq_queue",
            "main:frontend:option:hwm"      : "1000",
            "main:frontend:option:swap"     : "25000000",
            "main:frontend:option:subscribe": "#2",
            "main:frontend:bind"            : "tcp://eth0:5555",
            "main:backend:bind"             : "tcp://eth0:5556",
        }
    )
]


@pytest.mark.parametrize("call, data, expected", PARSE_TEST_CASES)
def test_parse(call, data, expected):
    result = call(data)
    assert result == expected
