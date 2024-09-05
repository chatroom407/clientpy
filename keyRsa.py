import base64
import urllib.parse
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

private_key_pem = None
public_key_pem = None

def generate_key_pair():
    global private_key_pem, public_key_pem  
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_key = private_key.public_key()
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_key_pem.decode('utf-8'), public_key_pem.decode('utf-8')

def get_server_key(url):
    try:
        generate_key_pair()

        print("Public Key (PEM format):\n", public_key_pem.decode('utf-8'))
        print("Private Key (PEM format):\n", private_key_pem.decode('utf-8'))

        encoded_public_key = urllib.parse.quote(base64.b64encode(public_key_pem).decode())

        response = requests.get(f"http://{url}/room407/server/deliveryKey.php?pk={encoded_public_key}")

        if response.status_code != 200:
            raise Exception(f"Błąd: {response.status_code}")

        return response.text

    except Exception as e:
        print(f"Err: {e}")
        raise

