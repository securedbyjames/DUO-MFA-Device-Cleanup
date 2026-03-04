import requests
from requests.auth import HTTPBasicAuth
import csv

DUO_IKEY = "EXAMPLE_IKEY"
DUO_SKEY = "EXAMPLE_SKEY"
DUO_HOST = "api-example.duosecurity.com"

BASE_URL = f"https://{DUO_HOST}/admin/v1"

CSV_FILE = "duo_cleanup_log.csv"

# Retrieve users

def get_users():

    url = f"{BASE_URL}/users"

    response = requests.get(
        url,
        auth=HTTPBasicAuth(DUO_IKEY, DUO_SKEY)
    )

    return response.json()["response"]

# Get user devices

def get_user_devices(user_id):

    url = f"{BASE_URL}/users/{user_id}"

    response = requests.get(
        url,
        auth=HTTPBasicAuth(DUO_IKEY, DUO_SKEY)
    )

    return response.json()["response"]["phones"]


# Delete device

def delete_device(phone_id):

    url = f"{BASE_URL}/phones/{phone_id}"

    response = requests.delete(
        url,
        auth=HTTPBasicAuth(DUO_IKEY, DUO_SKEY)
    )

    return response.status_code


# Cleanup

def run_cleanup():

    users = get_users()

    with open(CSV_FILE, "w", newline="") as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow([
            "username",
            "kept_device",
            "removed_device"
        ])

        for user in users:

            username = user["username"]
            user_id = user["user_id"]

            devices = get_user_devices(user_id)

            # Skip if user only has one device
            if len(devices) <= 1:
                continue

            # Sort devices newest → oldest
            devices_sorted = sorted(
                devices,
                key=lambda x: x["activated"],
                reverse=True
            )

            newest_device = devices_sorted[0]
            old_devices = devices_sorted[1:]

            for device in old_devices:

                phone_id = device["phone_id"]

                print(
                    f"Removing device {phone_id} for user {username}"
                )

                delete_device(phone_id)

                writer.writerow([
                    username,
                    newest_device["phone_id"],
                    phone_id
                ])


# Run

if __name__ == "__main__":
    run_cleanup()
