import asyncio
import websockets
import xml.etree.ElementTree as ET
import time
import traceback
import xml.dom.minidom

class AwsRequest:
    def __init__(self, aws):
        self.aws = aws
        
    def encrypt_message(self, id, mid, message):
        try:
            print(mid)
            index = self.aws.global_ids.index(mid)
            print(self.aws.global_ids)
            print()
            print(index)  
            print()
            pubKey = self.aws.global_pub_keys[index]          
            print(self.aws.global_pub_keys)
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

    def decrypt_message(self, encrypted_msg):
        
        return encrypted_msg

    async def clients(self, websocket):
        print("#CLIENTS#")
        tb  = "<tb>"
        tb += "<instance>clients</instance>"
        tb += "<id></id>"
        tb += "<msg></msg>"
        tb += "<mid></mid>"
        tb += "</tb>"
        await websocket.send(tb)

    async def pls_key(self, client_id, websocket):
        print("#PLS_KEY#")
        tb = "<tb>"
        tb += "<instance>pls_key</instance>"
        tb += f"<id>{client_id}</id>"
        tb += "<msg></msg>"
        tb += f"<mid>{self.aws.global_myId}</mid>"
        tb += "</tb>"                
        
        xml_str = xml.dom.minidom.parseString(tb).toprettyxml(indent="  ")
        print(xml_str)
        with open("loggs/send/pls_key", "a") as file:
            file.write(xml_str)
        await websocket.send(tb) 