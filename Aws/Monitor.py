
import asyncio
import websockets
import xml.etree.ElementTree as ET
import time
import traceback

class Monitor:
    def __init__(self, aws_instance):
        self.aws_instance = aws_instance

    async def monitor_global_new_clients(self):
        #global global_new_clients
        #global connFlag
        while True:
            if self.aws_instance.connFlag == 1:
                break
            if self.aws_instance.global_new_clients >= 1:
                break
            await asyncio.sleep(1)


    async def monitor_global_public_key(self, websocket):
        print("monitor_global_public_key")
        
        prev_length = len(self.aws_instance.global_pub_keys)  

        while True:
            print("a: " + str(prev_length))
            if self.aws_instance.global_pub_keys:                
                if len(self.aws_instance.global_pub_keys) > prev_length:
                    print(f"New public key added: {self.aws_instance.global_pub_keys[-1]}")  
                    prev_length = len(self.aws_instance.global_pub_keys)
                    break

            if self.aws_instance.connFlag == 1:
                break
            
            if len(self.aws_instance.global_ids) == len(self.aws_instance.global_pub_keys):
                print("Number of initialized elements matches the number of public keys.")
                break
            
            await asyncio.sleep(1)