import pickle
import sys
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad
from base64 import b64encode
import os


class Encryption:
    def __init__(self, key):
        self.key = self.pad_key(key)

    def pad_key(self, key):
        key_length = len(key)
        if key_length < 8:
            padded_key = key + (8 - key_length) * b'\x00'
        elif key_length > 8:
            padded_key = key[:8]
        else:
            padded_key = key
        return padded_key

    def encrypt(self, plaintext):
        cipher = DES.new(self.key, DES.MODE_ECB)
        padded_plaintext = pad(plaintext.encode(), DES.block_size)
        ciphertext = cipher.encrypt(padded_plaintext)
        return b64encode(ciphertext).decode()


def generate_and_save_passwords(filename, key, combination_length, start_index):
    encryptor = Encryption(key)
    num_passwords = 10 ** combination_length
    progress_interval = max(num_passwords // 100, 1)  # Update progress every 1% of passwords

    with open(filename, 'wb') as f:
        for i, password in enumerate(generate_passwords(combination_length, start_index), start=start_index):
            encrypted_password = encryptor.encrypt(password)
            password_data = {password: encrypted_password}
            pickle.dump(password_data, f)

            if i % progress_interval == 0:
                sys.stdout.write(f"\rProgress: {i}/{num_passwords} ({i * 100 / num_passwords:.2f}%)")
                sys.stdout.flush()


def generate_passwords(length, start_index):
    for combination in range(start_index, start_index + 50000):
        yield str(combination).zfill(length)


if __name__ == "__main__":
    key = b"$VfXlM^U#*"
    combination_length = 8
    start_index = 0

    num_passwords = 10 ** combination_length
    num_files = num_passwords // 50000 + (num_passwords % 50000 > 0)

    for i in range(num_files):
        filename = f'passwords-{i}.bin'
        generate_and_save_passwords(filename, key, combination_length, start_index)
        start_index += 50000

    print("\nPassword generation and saving complete.")
