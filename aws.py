import asyncio
import websockets
import xml.etree.ElementTree as ET
import time
import traceback

connFlag = 0   
global_myId = 'main'
global_ids  = []
global_pub_keys = []
global_new_clients = 0

async def process_message(message):
    global global_new_clients
    global global_pub_keys
    global global_ids
    root = ET.fromstring(message)
    
    instance = root.find('instance').text
    print("Message:" + message)
    print("INSTANCE: " + instance)    

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
        my_pub_key = global_myId
        print("pls:", client_id)
        tb = f"<tb><instance>key</instance><id>{client_id}</id><msg>{my_pub_key}</msg><mid>{client_id}</mid></tb>"
        return tb  

    elif instance == "key":
        print(message)
        
        reciver_client_id = root.find('id').text
        reciver_pub_key = root.find('msg').text

        for index, global_client_id in enumerate(global_ids):
            if global_client_id == reciver_client_id:
                if 0 <= index < len(global_pub_keys):
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
    global connFlag
    while True:
        if connFlag == 1:
            break
        if global_new_clients >= 1:
            break
        await asyncio.sleep(1)


async def monitor_global_public_key(websocket):
    global global_ids
    global global_pub_keys
    global connFlag
    
    prev_length = len(global_pub_keys)  

    while True:
        #print(global_pub_keys)
        #for mid in global_ids:
            #await pls_key(mid, websocket)

        if global_pub_keys:
            if len(global_pub_keys) > prev_length:
                print(f"New public key added: {global_pub_keys[-1]}")  
                prev_length = len(global_pub_keys)

        if connFlag == 1:
            break
        
        if len(global_ids) == len(global_pub_keys):
            print("Number of initialized elements matches the number of public keys.")
            break
        
        await asyncio.sleep(1)


async def connect_and_listen(uri):
    global connFlag
    connFlag = 0  
    async with websockets.connect(uri) as websocket:
        print("Try connected")
        
        async def handle_messages():
            global connFlag
            while True:
                try:
                    #message = await asyncio.wait_for(websocket.recv(), timeout=1)
                    message = await websocket.recv()
                    print("Received message:", message)
                    response_to_send = await process_message(message)
                    if response_to_send:
                        await websocket.send(response_to_send)
                        print("Sent response:", response_to_send)
                    print()
                except websockets.ConnectionClosed:
                    print("WebSocket connection closed.")
                    connFlag = 1
                    break  
                except Exception as e:
                    print(f"Error in message handling: {e}")
                    traceback.print_exc()
                    #break

        asyncio.create_task(handle_messages())

        if connFlag != 1:
            print("")
            print("-Get-Clients-")
            await clients(websocket)
            await monitor_global_new_clients()
                  
            print("")
            print("-Wait-for-keys-")
            if not global_ids:
                print("---No client IDs found---")
            else:
                print("---Clients download---")

            for mid in global_ids:
                await pls_key(mid, websocket)
              
        await monitor_global_public_key(websocket)

        if connFlag != 1:
            print("-Public_key_Load-")
            print()

        while True and  connFlag != 1:
            message = await encrypt_message(global_myId, global_ids[0], "TestMessage")
            await websocket.send(message)
            await asyncio.sleep(1)

def encrypt_message(id, mid, message):
    try:
        print(mid)
        index = global_ids.index(mid)
        print(global_ids)
        print()
        print(index)  
        print()
        pubKey = global_pub_keys[index]          
        print(global_pub_keys)
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