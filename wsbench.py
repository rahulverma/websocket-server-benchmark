#!/usr/bin/env python

import asyncio
from random import randint
from multiprocessing import Pool

import websockets

cpu_count = 4


def get_address():
    while True:
        for x in range(1, 127):
            yield '127.0.0.' + str(x), 0


async def connect(generator):
    async with websockets.connect('ws://localhost:9001', local_addr=next(generator)) as websocket:
        while True:
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
            await asyncio.sleep(1 + randint(100, 1000))

async def multiple_connect(size):
    generator = get_address()
    await asyncio.wait([capture_exception(generator) for _ in range(size)])


def start(connection_count):
    asyncio.get_event_loop().run_until_complete(multiple_connect(connection_count))


with Pool(4) as p:
    p.map(start, [100000]*cpu_count)
