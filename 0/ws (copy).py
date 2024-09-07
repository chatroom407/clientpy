import asyncio
import websockets

async def connect_and_send(uri):
    async with websockets.connect(uri) as websocket:
        await websocket.send("<tb>backend219</tb>")
        print("Message sent: <tb>backend219</tb>")
        conn_flag = 1
        print("Connection flag set:", conn_flag)
        response = await websocket.recv()
        print("Received response:", response)