import requests
from requests.auth import HTTPBasicAuth
import csv
from collections import defaultdict

# Replace these values with your Duo API credentials
DUO_IKEY = "EXAMPLE_IKEY"
DUO_SKEY = "EXAMPLE_SKEY"
DUO_HOST = "api-example.duosecurity.com"

BASE_URL = f"https://{DUO_HOST}/admin/v1"

# CSV file where cleanup actions will be recorded
CSV_FILE = "duo_cleanup_log.csv"


# Retrieve all users
def get_users():

    url = f"{BASE_URL}/users"

    response = requests.get(
        url,
        auth=HTTPBasicAuth(DUO_IKEY, DUO_SKEY)
    )

    return response.json()["response"]


# Retrieve all phones
def get_phones():

    url = f"{BASE_URL}/phones"

    response = requests.get(
        url,
        auth=HTTPBasicAuth(DUO_IKEY, DUO_SKEY)
    )

    return response.json()["response"]


# Delete a device from Duo
def delete_device(phone_id):

    url = f"{BASE_URL}/phones/{phone_id}"

    response = requests.delete(
        url,
        auth=HTTPBasicAuth(DUO_IKEY, DUO_SKEY)
    )

    return response.status_code


# Main cleanup process
def run_cleanup():

    users = get_users()
    phones = get_phones()

    # Map user_id to username
    user_map = {u["user_id"]: u["username"] for u in users}

    user_devices = defaultdict(list)

    for phone in phones:

        for owner in phone.get("users", []):

            user_id = owner["user_id"]

            user_devices[user_id].append({
                "phone_id": phone["phone_id"],
                "activated": phone["activated"]
            })

    with open(CSV_FILE, "w", newline="") as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow([
            "username",
            "kept_device",
            "removed_device"
        ])

        for user_id, devices in user_devices.items():

            if len(devices) <= 1:
                continue

            devices_sorted = sorted(
                devices,
                key=lambda x: x["activated"],
                reverse=True
            )

            newest = devices_sorted[0]

            for old_device in devices_sorted[1:]:

                username = user_map.get(user_id)

                phone_id = old_device["phone_id"]

                print(f"Removing {phone_id} for {username}")

                delete_device(phone_id)

                writer.writerow([
                    username,
                    newest["phone_id"],
                    phone_id
                ])


if __name__ == "__main__":
    run_cleanup()
