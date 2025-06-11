from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from typing import cast
from cryptography.fernet import Fernet

KEYSIZE = 2048
MESSAGE = "12345678"

class Cryptopher:
    def __init__(self, fernet_key: bytes) -> None:
        self.fernet_key = fernet_key
        self.f = Fernet(fernet_key)
    
    def encrypt(self, plaintext: bytes) -> bytes:
        return self.f.encrypt(plaintext)
    def decrypt(self, ciphertext: bytes) -> bytes:
        return self.f.decrypt(ciphertext)

class PubPriv:
    def __init__(self):
        self.initialised = False
        self.cryptopher: Cryptopher
    def setup(self, fernet_key: bytes) -> None:
        self.cryptopher = Cryptopher(fernet_key)
        self.initialised = True
    def encrypt(self, plaintext: bytes) -> bytes:
        if not self.initialised: raise Exception("Use setup to setup")
        return self.cryptopher.encrypt(plaintext)
    def decrypt(self, ciphertext: bytes) -> bytes:
        if not self.initialised: raise Exception("Use setup to setup")
        return self.cryptopher.decrypt(ciphertext)

class Private(PubPriv):
    def __init__(self) -> None:
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=KEYSIZE,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        self.public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        super().__init__()

    def gen_signature(self) -> bytes:
        return self.private_key.sign(
            MESSAGE.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
    
    def private_decrypt_bytes(self, ciphertext: bytes) -> bytes:
        return self.private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    def setup_with_encrypted_fernet_key(self, encrypted_fernet_key: bytes) -> None:
        self.setup(self.private_decrypt_bytes(encrypted_fernet_key))
    

class Public(PubPriv):
    def __init__(self, public_bytes: bytes) -> None:
        self.public_key = self.public_key_from_public_bytes(public_bytes)
        super().__init__()
        self.setup(Fernet.generate_key())

    def public_key_from_public_bytes(self, public_bytes: bytes) -> rsa.RSAPublicKey:
        return cast(rsa.RSAPublicKey, serialization.load_pem_public_key(
            data=public_bytes,
            backend=default_backend()
        ))
    
    def check_signature(self, signature: bytes) -> bool:
        try:
            self.public_key.verify(
                signature,
                MESSAGE.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except: return False

    def private_encrypt_bytes(self, plaintext: bytes) -> bytes:
        return self.public_key.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    def encrypted_fernet_key(self) -> bytes:
        return self.private_encrypt_bytes(self.cryptopher.fernet_key)

    
if __name__ == "__main__":
    private = Private()
    public = Public(private.public_bytes)
    print(public.check_signature(private.gen_signature()))

    encrypted_fernet_key = public.encrypted_fernet_key()
    private.setup_with_encrypted_fernet_key(encrypted_fernet_key)
    
    plaintext = "Testing123!"
    ciphertext = public.encrypt(plaintext.encode())
    print(plaintext == private.decrypt(ciphertext).decode())
    ciphertext = private.encrypt(plaintext.encode())
    print(plaintext == public.decrypt(ciphertext).decode())
