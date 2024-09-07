import asyncio
import websockets
import xml.etree.ElementTree as ET

global_myId = 'main'
global_ids  = []
global_pub_keys = []

async def process_message(message):
    root = ET.fromstring(message)
    
    instance = root.find('instance').text
    print(instance)

    if instance == "you":
        my_id = root.find('id').text
        print("My ID:", my_id)

    elif instance == "clients":
        for elem in root:
            if elem.tag == 'id':
                print(f'Tag: {elem.tag}, Zawartość: {elem.text}')
                global_ids.append(elem.text)

    elif instance == "send":
        print("(send):", message)

    elif instance == "msg":
        id_elem = root.find('id').text
        msg = root.find('msg').text
        print("(msg):", message)
        decrypted_text = decrypt_message(msg)

    elif instance == "pls":
        client_id = root.find('mid').text
        my_pub_key = client_auth.get_login()
        print("pls:", client_id)
        tb = f"<tb><instance>key</instance><id>{client_id}</id><msg>{my_pub_key}</msg><mid>{client_id}</mid></tb>"
        return tb  

    elif instance == "key":
        print(message)
        
        reciver_client_id = root.find('id').text
        reciver_pub_key = root.find('msg').text

        for index, global_client_id in enumerate(global_ids):
            if global_client_id == reciver_client_id:
                global_pub_keys[index] = reciver_pub_key
                break


    else:
        print(message)

async def connect_and_listen(uri):
    async with websockets.connect(uri) as websocket:
        print("Connected")

        async def handle_messages():
            while True:
                try:
                    message = await websocket.recv()
                    print("Received message:", message)
                    response_to_send = await process_message(message)
                    if response_to_send:
                        await websocket.send(response_to_send)
                        print("Sent response:", response_to_send)
                except websockets.ConnectionClosedError as e:
                    print(f"WebSocket connection closed with error: {e}")
                    # Optionally, you could attempt to reconnect here if needed

        asyncio.create_task(handle_messages())

        await clients(websocket)

        if not global_ids:
            print("No client IDs found.")
            return

        for client_id in global_ids:
            await pls_key(client_id, websocket)

        print("Length of global_ids:", len(global_ids))
        print("Length of global_pub_keys:", len(global_pub_keys))

        print("Public keys:")
        for pub_key in global_pub_keys:
            print(pub_key) 


def decrypt_message(encrypted_msg):
    return encrypted_msg

async def clients(websocket):
    tb  = "<tb>"
    tb += "<instance>clients</instance>"
    tb += "<id></id>"
    tb += "<msg></msg>"
    tb += "<mid></mid>"
    tb += "</tb>"
    
    # Wysłanie wiadomości przez WebSocket
    await websocket.send(tb)

async def pls_key(client_id, websocket):
    print("PLS_KEY")
    tb = "<tb>"
    tb += "<instance>pls_key</instance>"
    tb += f"<id>{client_id}</id>"
    tb += "<msg></msg>"
    tb += f"<mid>{global_myId}</mid>"
    tb += "</tb>"
    print(tb)
    await websocket.send(tb) 