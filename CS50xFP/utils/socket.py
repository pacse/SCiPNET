"""
Functions related to socket
for both client and server
"""

# TODO: Implement TLS: after submit final project

import socket
from struct import pack, unpack
from json import dumps, loads
from typing import Any


# ==== Globals & setup for server connection ====
HOST = '127.0.0.1'  # localhost
PORT = 65432
ADDR = (HOST, PORT)

RCVSIZE = 4096
MAX_MSG_SIZE = (1024 ** 2) * 50  # 50 MB max message size
SIZE_TYPE = '!I'  # use !I for packing/unpacking

# sanity messages
TEST_MSG = b'PING'
ACK_MSG = b'PONG'

socket.setdefaulttimeout(60)  # set a timeout for socket operations
# ==== Funcs ====

def encode(data: Any) -> bytes:
    """
    Encodes `data` to json, converts to
    bytes, and appends size at start
    so it can be sent over a socket conn
    """
    encoded_data = dumps(data).encode()

    return pack(SIZE_TYPE, len(encoded_data)) + encoded_data

def decode(data: bytes) -> Any:
    """
    Decodes `data` from bytes to json
    so it can be processed by the server
    """
    return loads(data.decode())


def send(conn: socket.socket, data: Any) -> None:
    """
    Sends `data` over `conn`
    """

    try:
        # === validate data ===
        if not data:
            raise ValueError('No data to send') # ensure we have data

        e_data = encode(data)

        if (l := len(e_data)) > MAX_MSG_SIZE:
            raise ValueError(f'Data exceeds maximum size:\n'
                             f'data size: {l}, max size: {MAX_MSG_SIZE})\n'
                             f'{data!r}\n') # limit size


        # === test connection ===
        conn.settimeout(2) # short timeout for test

        conn.sendall(TEST_MSG)
        if conn.recv(100) != ACK_MSG:
            raise ConnectionError('Did not receive ACK')


        # === send data ===
        conn.settimeout(60) # reset timeout
        conn.sendall(e_data)

    except Exception as e:
        raise ConnectionError(f'Error transmitting data over conn:\n{e}\nData: {data!r}\n')



def recv(conn: socket.socket) -> Any:
    """
    Receives and returns data from `conn`
    """

    try:
        # === test connection ===
        conn.settimeout(2)                 # short timeout for test

        if conn.recv(100) != TEST_MSG:     # get test msg
            raise ConnectionError('Did not receive TEST_MSG')

        conn.sendall(ACK_MSG)              # send test response


        # === receive data ===
        conn.settimeout(60)                # reset timeout

        # get size of incoming message
        size = conn.recv(4)
        if not size or len(size) < 4:
            raise ConnectionError('Connection lost or incomplete size data')

        size = unpack(SIZE_TYPE, size)[0]

        data = b''

        while len(data) < size:

            buffer = conn.recv(RCVSIZE)

            if not buffer:
                raise ConnectionError('Connection lost')

            data += buffer


        # check max size
        if len(data) > MAX_MSG_SIZE:
            raise ValueError(f'Message exceeds maximum size:\n{data!r}\n')

        # decode and return
        return decode(data)

    except Exception as e:
        raise ConnectionError(f'Error receiving data from conn:\n{e}\nRaw data: {data!r}\n')
