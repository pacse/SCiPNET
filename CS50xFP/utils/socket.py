'''
Functions related to socket 
for both client and server
'''
import socket
from json import dumps, loads
from typing import Any
from time import sleep

# Information for server connection
HOST = "127.0.0.1" # localhost
PORT = 65432
ADDR = (HOST, PORT) # combine into a tuple
RCVSIZE = 1024 # buffer size for message length

WAITTIME = 0.25 # time to wait between sending data

def encode(data: Any) -> bytes:
    # TODO: Validate
    '''
    Encodes data into json and converty it to bytes
    so it can be sent over a socket connection
    '''
    return dumps(data).encode()

def decode(data: bytes) -> Any:
    # TODO: Validate
    '''
    Decodes data from bytes to json
    so it can be processed by the server
    '''
    return loads(data.decode())

def send(conn: socket.socket, data: Any) -> None:
    '''
    Sends data over conn with
    dynamic buffer size
    '''
    d = encode(data)
    buffer = len(d) * 8

    #TODO: Ensure buffer validity

    # now send data
    sleep(WAITTIME)
    conn.sendall(encode(buffer))
    sleep(WAITTIME)
    conn.sendall(d)

def recv(conn: socket.socket) -> bytes:
    '''
    Receives data from conn, returning decoded data
    '''
    size = decode(conn.recv(RCVSIZE)) # size to recv
    assert isinstance(size, int) # verify size type
    return conn.recv(size) # return data
