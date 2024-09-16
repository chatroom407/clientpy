import urllib.parse
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

import xml.etree.ElementTree as ET
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import base64


class KeyManager:
    def __init__(self):
        self.private_key_pem = None
        self.public_key_pem = None

    def parse_xml(self, text):
        xmlDoc = ET.fromstring(text)
        session = xmlDoc.find('session').text if xmlDoc.find('session') is not None else None

        enc_match = xmlDoc.find('enc')
        enc_content = enc_match.text if enc_match is not None else None

        if enc_content is None:
            raise ValueError("<enc> tag not found or empty.")
        
        return session, enc_content

    def decrypt_rsa(self, private_key_pem, encrypted_data):
        private_key = RSA.import_key(private_key_pem)
        cipher_rsa = PKCS1_OAEP.new(private_key)
        decrypted_key = cipher_rsa.decrypt(encrypted_data)
        return decrypted_key

    def encrypt_aes(self, data, key_hex):
        key = bytes.fromhex(key_hex)
        iv = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted_data = cipher.encrypt(pad(data.encode(), AES.block_size))

        iv_ciphertext = base64.b64encode(iv + encrypted_data).decode('utf-8')
        return iv_ciphertext
    
    def generate_key_pair(self):
        """Generuje parę kluczy RSA i zapisuje je jako PEM."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        self.private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_key = private_key.public_key()
        self.public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return self.private_key_pem.decode('utf-8'), self.public_key_pem.decode('utf-8')

    def get_server_key(self, url):
        """Pobiera klucz serwera przy użyciu publicznego klucza."""
        try:
            self.generate_key_pair()

            print("Public Key (PEM format):\n", self.public_key_pem.decode('utf-8'))
            print("Private Key (PEM format):\n", self.private_key_pem.decode('utf-8'))

            encoded_public_key = urllib.parse.quote(base64.b64encode(self.public_key_pem).decode())

            response = requests.get(f"http://{url}/room407/deliveryKey.php?pk={encoded_public_key}")

            if response.status_code != 200:
                raise Exception(f"Błąd: {response.status_code}")

            return response.text

        except Exception as e:
            print(f"Err: {e}")
            raise
    