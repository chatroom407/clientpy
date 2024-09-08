import asyncio
import websockets
import xml.etree.ElementTree as ET
import time


global_myId = 'main'
global_ids  = []
global_pub_keys = []
global_new_clients = 0

async def process_message(message):
    global client_auth
    global global_new_clients
    global global_pub_keys
    global global_ids
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
        global_new_clients += 1    

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

    elif instance == "send":
            print("(send):", message)

    elif instance == "msg":
        id_elem = root.find('id').text
        msg = root.find('msg').text
        print("(msg):", message)
        decrypted_text = decrypt_message(msg)
    
    else:
        print(message)


async def monitor_global_new_clients():
    global global_new_clients
    while True:
        if global_new_clients >= 1:
            break
        await asyncio.sleep(1)

async def connect_and_listen(uri):
    connFlag = 0    
    while True:  # Loop to handle reconnection        
        try:
            async with websockets.connect(uri) as websocket:
                print("Connected")
                
                # Start a background task to handle messages
                async def handle_messages():
                    nonlocal connFlag
                    while True:
                        try:
                            message = await websocket.recv()
                            print("Received message:", message)
                            response_to_send = await process_message(message)
                            if response_to_send:
                                await websocket.send(response_to_send)
                                print("Sent response:", response_to_send)
                        except websockets.ConnectionClosed:
                            print("WebSocket connection closed.")
                            connFlag = 1
                            break  # Exit loop and reconnect
                        except Exception as e:
                            print(f"Error in message handling: {e}")
                            break

                # Start message handling in the background
                asyncio.create_task(handle_messages())

                # Perform your client logic (Ensure these are non-blocking)
                await clients(websocket)
                await monitor_global_new_clients()

                if not global_ids:
                    print("---No client IDs found---")
                else:
                    print("---Clients download---")

                for mid in global_ids:
                    await pls_key(mid, websocket)

                # Send periodic messages
                while True and  connFlag != 1:
                    message = await encrypt_message(global_myId, global_ids[0], "TestMessage")
                    await websocket.send(message)
                    await asyncio.sleep(1)
        
        except (websockets.ConnectionClosed, ConnectionRefusedError) as e:
            print(f"Connection error: {e}, retrying in 2 seconds...")
            await asyncio.sleep(2)  # Wait before attempting reconnection
        except Exception as e:
            print(f"Unexpected error: {e}")
            break 

def encrypt_message(id, mid, message):
    try:
        print(mid)
        index = global_ids.index(mid)
        print(global_ids)
        print()
        print(index)  
        print()
        pubKey = global_pub_keys[index]          
    except ValueError:
        raise Exception(f"User ID {mid} not found in global_ids")

    public_key = serialization.load_pem_public_key(pubKey.encode('utf-8'))

    encrypted_message = public_key.encrypt(
        message.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    tb = "<tb>"
    tb += "<instance>send</instance>"
    tb += f"<id>{id}</id>"
    tb += f"<msg>{encrypted_message.hex()}</msg>"  
    tb += f"<mid>{mid}</mid>"
    tb += "</tb>"

    return tb

def decrypt_message(encrypted_msg):
    return encrypted_msg

async def clients(websocket):
    tb  = "<tb>"
    tb += "<instance>clients</instance>"
    tb += "<id></id>"
    tb += "<msg></msg>"
    tb += "<mid></mid>"
    tb += "</tb>"
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