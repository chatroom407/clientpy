import asyncio
import websockets
import xml.etree.ElementTree as ET
import time
import traceback
import xml.dom.minidom

import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

class AwsRequest:
    def __init__(self, aws):
        self.aws = aws
        
    def encrypt_message(self, pub_key_pem, recipient_username, sender_id, message):
        public_key = serialization.load_pem_public_key(pub_key_pem.encode('utf-8'))
        encrypted_message = public_key.encrypt(
            message.encode('utf-8'),
            padding.PKCS1v15()  
        )

        encrypted_message_b64 = base64.b64encode(encrypted_message).decode('utf-8')

        tb = "<tb>"
        tb += "<instance>send</instance>"
        tb += f"<id>{recipient_username}</id>"
        tb += f"<msg>{encrypted_message_b64}</msg>" 
        tb += f"<mid>{sender_id}</mid>"
        tb += "</tb>"

        print(tb)

        return tb

    def decrypt_message(self, encrypted_msg):
        private_key = serialization.load_pem_private_key(
            self.aws.keyMenager.private_key_pem,  
            password=None,  
            backend=default_backend() 
        )

        if isinstance(encrypted_msg, str):
            encrypted_msg = base64.b64decode(encrypted_msg)  

        decrypted_message = private_key.decrypt(
            encrypted_msg,  
            padding.PKCS1v15()  
        )

        return decrypted_message

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