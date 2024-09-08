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
        message = await websocket.recv()
        await process_message(message)
        await clients(websocket)
        message = await websocket.recv()
        await process_message(message)

        print(len(global_ids))
        for client_id in global_ids:
            await pls_key(client_id, websocket)


            ##message = await websocket.recv()
            #await process_message(message)

def encrypt_message(id, mid, message):
    try:
        index = global_ids.index(mid)  
        pubKey = global_pub_keys[index]  # Get the corresponding public key
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
    tb += f"<msg>{encrypted_message.hex()}</msg>"  # Convert encrypted bytes to hex
    tb += f"<mid>{mid}</mid>"
    tb += "</tb>"

    return tb

async def send_message(tb_message, websocket_url):
    await websocket.send(tb_message)

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
    tb = "<tb>"
    tb += "<instance>pls_key</instance>"
    tb += f"<id>{client_id}</id>"
    tb += "<msg></msg>"
    tb += f"<mid>{global_myId}</mid>"
    tb += "</tb>"
    print(tb)
    await websocket.send(tb) 