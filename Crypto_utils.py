from quantcrypt import (
    dss,      # Digital Signature Scheme algos      - secret-key signatures

    errors,   # All errors QuantCrypt may raise     - also available from other modules
    utils,    # Helper utilities from all modules   - gathered into one module
    compiler  # Tools for compiling PQA binaries    - requires optional dependencies
)

from quantcrypt.kem import MLKEM_1024
from quantcrypt.dss import MLDSA_87
import secrets
from quantcrypt.cipher import Krypton

def generate_keyPair():
    # First, we create an instance of a KEM algorithm.
    kem = MLKEM_1024()
    # Next, we generate a PK and SK pair.
    public_key, secret_key = kem.keygen()

    return public_key, secret_key
    
def encrypt_with_pub(pub_key):
    kem = MLKEM_1024()
    cipher_text, shared_secret = kem.encaps(pub_key)
    return cipher_text, shared_secret

def decrypt_with_pr(pr_key, cipher):
    kem = MLKEM_1024()
    shared_secret_copy = kem.decaps(pr_key, cipher)
    return shared_secret_copy


def sign(key, message):
    dss = MLDSA_87()
    signature = dss.sign(key, message)
    return signature


def unsign(key, message, signature):
    return dss.verify(key, message, signature)
    