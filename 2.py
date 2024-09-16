import time
import sys
import os

sys.path.append(os.path.abspath('Aws'))
sys.path.append(os.path.abspath('Encrypt'))

from KeyManager import *
from ClientAuth import *
from Aws import *

from AwsRequest import AwsRequest
from Monitor import *

async def loop():
    while True:
        url = "193.93.89.68"
        keyMenager = KeyManager()
        server_response = keyMenager.get_server_key(url)
        print("Response from server:", server_response)
        
        session, enc_content = keyMenager.parse_xml(server_response)            

        encrypted_data = base64.b64decode(enc_content)
        try:
            decrypted_aes_key = keyMenager.decrypt_rsa(keyMenager.private_key_pem, encrypted_data)
            print("<enc> decrypted AES key:", decrypted_aes_key)
            print("<enc> decrypted AES key:", str(decrypted_aes_key))
            decrypted_aes_key = decrypted_aes_key.decode('utf-8', errors='replace')
            print("<enc> decrypted AES key:", decrypted_aes_key)
        except Exception as e:
            print("Błąd odszyfrowania:", e)
            exit()

        client_auth = ClientAuth.from_auth_file('auth2')
        password = client_auth.get_password()
        login = client_auth.get_login()

        print(password)
        print(login)

        password_encrypted = keyMenager.encrypt_aes(password, decrypted_aes_key)
        login_encrypted = keyMenager.encrypt_aes(login, decrypted_aes_key)

        url = "193.93.89.68"
        port = "8081"
        ws = f"ws://{url}:{port}?room={password_encrypted}&session={session}&login={login_encrypted}"

        print("Generated ws URL:", ws)
        print("---------------------------------------------------------")
        
        #asyncio.get_event_loop().run_until_complete(connect_and_send(ws))

        aws = Aws("main2")
        await aws.connect_and_listen(ws)
        time.sleep(1)

asyncio.run(loop())