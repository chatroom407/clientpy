import asyncio
import websockets
import xml.etree.ElementTree as ET

async def process_message(message):
    root = ET.fromstring(message)
    
    instance = root.find('instance').text
    print(instance)

    if instance == "you":
        my_id = root.find('id').text
        print("My ID:", my_id)

    elif instance == "clients":
        ids = root.findall('id')
        login_temp = "globalLogin"  
        clients = ""
        for id_elem in ids:
            id_value = id_elem.text
            if id_value == login_temp:
                continue
            print(id_value)
            clients += f"<button class='cli btn-clients' onclick=\"getInner('{id_value}')\">{id_value}</br></button>"

    elif instance == "send":
        print("(send):", message)

    elif instance == "msg":
        id_elem = root.find('id').text
        msg = root.find('msg').text
        print("(msg):", message)
        decrypted_text = decrypt_message(msg)

    elif instance == "pls":
        client_id = root.find('mid').text
        my_pub_key = "myPublicKey"  
        print("pls:", client_id)
        tb = f"<tb><instance>key</instance><id>{client_id}</id><msg>{my_pub_key}</msg><mid>{client_id}</mid></tb>"
        return tb  

    elif instance == "key":
        print(message)
        reciver_pub_key = root.find('msg').text

    else:
        print(message)

async def connect_and_listen(uri):
    async with websockets.connect(uri) as websocket:
        print("Connected")
        while True:
            message = await websocket.recv()
            response_to_send = await process_message(message)
            if response_to_send:
                await websocket.send(response_to_send)

def decrypt_message(encrypted_msg):
    return encrypted_msg  
