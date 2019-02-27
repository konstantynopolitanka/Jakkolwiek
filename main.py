import asyncio
import json
import logging
import websockets

logging.basicConfig()

STATE = {'value': 0}

USERS = set()

MESSAGE = {'text': ""}

def state_event():
    return json.dumps({'type': 'state', **STATE})

def users_event():
    return json.dumps({'type': 'users', 'count': len(USERS)})

def message_event():
    return json.dumps({'type': 'message', **MESSAGE })    

async def notify_state():
    if USERS:       # asyncio.wait doesn't accept an empty list
        message = state_event()
        await asyncio.wait([user.send(message) for user in USERS])

async def notify_users():
    if USERS:       # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([user.send(message) for user in USERS])

async def notify_message():
    if USERS:       # asyncio.wait doesn't accept an empty list
        message = message_event()
        print(message)
        await asyncio.wait([user.send(message) for user in USERS])
        print("Total antisemitism")


async def register(websocket):
    USERS.add(websocket)
    await notify_users()

async def unregister(websocket):
    USERS.remove(websocket)
    await notify_users()

async def counter(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        await websocket.send(state_event())
        async for message in websocket:
            print("DATA to chuj")
            data = json.loads(message)
            print(data.keys())
            # if data is empty throws invalid keystroke error
            MESSAGE['text'] = data["message"]
            await notify_message()
            # if data['action'] == 'minus':
            #     STATE['value'] -= 1
            #     await notify_state()
            # elif data['action'] == 'plus':
            #     STATE['value'] += 1
            #     await notify_state()
            # else:
            #     logging.error("unsupported event: {}")#, data)
    finally:
        await unregister(websocket)

asyncio.get_event_loop().run_until_complete(
    websockets.serve(counter, 'localhost', 8765))
asyncio.get_event_loop().run_forever()