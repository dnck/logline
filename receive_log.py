# -*- coding: utf-8 *-*
"""
A simple UDP server that writes loglines to file. You should firewall this guy.
"""
import argparse
import socket
import json


MAX_BYTES = 65535

def write_line(line, fname):
    with open('./logs/{}.log'.format(fname), 'a') as f:
        f.write(line+'\n')

def log_server(host, port, fname):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    print('Server listening at {}'.format(sock.getsockname()))
    while True:
        received_bytes, address = sock.recvfrom(MAX_BYTES)
        client_data = json.loads(received_bytes.decode())
        write_line(client_data, fname)


if __name__ == '__main__':

    PARSER = argparse.ArgumentParser(
        description='Log server.'
    )
    PARSER.add_argument('-host',
        metavar='port', type=str, default='127.0.0.1',
        help='The log server public IP where we listen on'
    )
    PARSER.add_argument('-port',
        metavar='port', type=int, default=5222,
        help='The log server port where we listen on'
    )
    PARSER.add_argument('-fname',
        metavar='fname', type=str, default="test",
        help='The name of the log to write. Will be written in logs dir.'
    )

    args = PARSER.parse_args()

    log_server(args.host, args.port, args.fname)
