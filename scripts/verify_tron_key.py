import hashlib
import ecdsa
import base58

def private_key_to_address(priv_key_hex):
    # Remove 0x if present
    if priv_key_hex.startswith('0x'):
        priv_key_hex = priv_key_hex[2:]

    # 1. Private Key to Public Key (Uncompressed)
    priv_key_bytes = bytes.fromhex(priv_key_hex)
    sk = ecdsa.SigningKey.from_string(priv_key_bytes, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    pub_key_bytes = vk.to_string() # 64 bytes

    # 2. Keccak-256 of Public Key
    # Tron uses Keccak-256 (not SHA3-256)
    from Crypto.Hash import keccak
    k = keccak.new(digest_bits=256)
    k.update(pub_key_bytes)
    pub_key_hash = k.digest()

    # 3. Last 20 bytes + 0x41 prefix
    address_bytes = b'\x41' + pub_key_hash[-20:]

    # 4. Base58Check Encoding
    address = base58.b58encode_check(address_bytes).decode()
    return address

if __name__ == "__main__":
    # Test from previous run
    test_pk = "afb2feee321cecb57c0891e45c0e14a14e45892d4ea9d348ac725a1595cd5659"
    expected_addr = "THJUNHZRcyrTnvTCYLUNtrVQrDqDLU6Yyz"

    print(f"Testing Private Key: {test_pk}")
    generated_addr = private_key_to_address(test_pk)
    print(f"Generated Address: {generated_addr}")
    print(f"Expected Address:  {expected_addr}")

    if generated_addr == expected_addr:
        print("✅ VERIFICATION SUCCESSFUL!")
    else:
        print("❌ VERIFICATION FAILED!")
