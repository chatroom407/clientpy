import asyncio
import websockets
import xml.etree.ElementTree as ET
import time
import traceback

from AwsRequest import AwsRequest
from Monitor import *

#connFlag = 0   
#global_myId = 'main'
#global_ids  = []
#global_pub_keys = []
#global_new_clients = 0

class Aws:    
    def __init__(self, myId):
        self.connFlag = 0   
        self.global_myId = myId
        self.global_ids  = []
        self.global_pub_keys = []
        self.global_new_clients = 0    
        self.aws_request = AwsRequest(self)
        self.monitor = Monitor(self)

    async def process_message(self, message):
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
                    self.global_ids.append(elem.text)
            self.global_new_clients += 1    

        elif instance == "pls":
            client_id = root.find('mid').text
            my_pub_key = self.global_myId
            print("pls:", client_id)
            tb = f"<tb><instance>key</instance><id>{client_id}</id><msg>{my_pub_key}</msg><mid>{client_id}</mid></tb>"
            return tb  

        elif instance == "key":
            print(message)
            
            reciver_client_id = root.find('id').text
            reciver_pub_key = root.find('msg').text

            for index, self.global_client_id in enumerate(self.global_ids):
                if self.global_client_id == reciver_client_id:
                    if 0 <= index < len(self.global_pub_keys):
                        self.global_pub_keys[index] = [reciver_client_id, reciver_pub_key]
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

    async def connect_and_listen(self, uri):    
        self.connFlag = 0  
        async with websockets.connect(uri) as websocket:
            print("Try connected")
            
            async def handle_messages():            
                while True:
                    try:
                        message = await websocket.recv()
                        print("Received message:", message)
                        response_to_send = await self.process_message(message)
                        if response_to_send:
                            await websocket.send(response_to_send)
                            print("Sent response:", response_to_send)
                        print()
                    except websockets.ConnectionClosed:
                        print("WebSocket connection closed.")
                        self.connFlag = 1
                        break  
                    except Exception as e:
                        print(f"Error in message handling: {e}")
                        traceback.print_exc()
                        #break

            asyncio.create_task(handle_messages())

            if self.connFlag != 1:
                await self.aws_request.clients(websocket)
                await self.monitor.monitor_global_new_clients()

                for mid in self.global_ids:
                    await self.aws_request.pls_key(mid, websocket)
                
            await self.monitor.monitor_global_public_key(websocket)

            while True and  self.connFlag != 1:
                message = await self.aws_request.encrypt_message(self.global_myId, self.global_ids[0], "TestMessage")
                await websocket.send(message)
                await asyncio.sleep(1)

