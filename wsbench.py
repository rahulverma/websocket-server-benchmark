#!/usr/bin/env python

import asyncio
import uvloop
import websockets
import argparse
from random import randint
from multiprocessing import Pool
import os

process_count = 4


def get_address():
    while True:
        for x in range(1, 127):
            yield '127.0.0.' + str(x), 0


async def connect(generator):
    async with websockets.connect('ws://localhost:9001', local_addr=next(generator)) as websocket:
        while True:
            # print('Local Address: {}'.format(websocket.local_address))
            await websocket.send('*')

            response = await websocket.recv()
            if response != '*':
                print('Error in response:\npacket:{}\nresponse:{}'.format('*', response))
                return

            await asyncio.sleep(10 + randint(0, 10))


async def capture_exception(generator):
    while True:
        try:
            await connect(generator)
        except Exception as e:
            print('Error: {}'.format(e))
            return


def multiple_connect(size):
    generator = get_address()
    loop = asyncio.get_event_loop()
    for _ in range(size):
        loop.create_task(capture_exception(generator))


def start(connection_count):
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    multiple_connect(connection_count)
    asyncio.get_event_loop().run_forever()


parser = argparse.ArgumentParser(description='Websocket Benchmark.')
parser.add_argument('-p', dest='parallel_processes', action='store',
                    type=int, nargs='?', default=os.cpu_count(),
                    help='Number of parallel processes')

parser.add_argument('-c', dest='connection_count', action='store',
                    type=int, nargs='?', default=100,
                    help='Connections per process.')


args = parser.parse_args()

if args.parallel_processes == 1:
    start(args.connection_count)
else:
    process_count = args.parallel_processes
    with Pool(process_count) as p:
        p.map(start, [args.connection_count]*process_count)

