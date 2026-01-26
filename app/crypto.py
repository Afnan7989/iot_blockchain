import json
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from dotenv import load_dotenv

load_dotenv()

AES_KEY = os.getenv("AES_SECRET_KEY").encode()  # 32 bytes

def encrypt_json(data: dict):
    aesgcm = AESGCM(AES_KEY)
    nonce = os.urandom(12)
    encrypted = aesgcm.encrypt(nonce, json.dumps(data).encode(), None)
    return {
        "nonce": nonce.hex(),
        "ciphertext": encrypted.hex()
    }

def decrypt_json(payload: dict):
    aesgcm = AESGCM(AES_KEY)
    decrypted = aesgcm.decrypt(
        bytes.fromhex(payload["nonce"]),
        bytes.fromhex(payload["ciphertext"]),
        None
    )
    return json.loads(decrypted.decode())
