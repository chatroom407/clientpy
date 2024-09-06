import base64
import xml.etree.ElementTree as ET
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes

def parse_xml(text):
    xmlDoc = ET.fromstring(text)
    session = xmlDoc.find('session').text if xmlDoc.find('session') is not None else None

    enc_match = xmlDoc.find('enc')
    enc_content = enc_match.text if enc_match is not None else None

    if enc_content is None:
        raise ValueError("<enc> tag not found or empty.")
    
    return session, enc_content

def decrypt_rsa(private_key_pem, encrypted_data):
    private_key = RSA.import_key(private_key_pem)
    cipher_rsa = PKCS1_OAEP.new(private_key)
    decrypted_key = cipher_rsa.decrypt(encrypted_data)
    return decrypted_key

def encrypt_aes(data, key_hex):
    key = bytes.fromhex(key_hex)
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_data = cipher.encrypt(pad(data.encode(), AES.block_size))

    iv_ciphertext = base64.b64encode(iv + encrypted_data).decode('utf-8')
    return iv_ciphertext