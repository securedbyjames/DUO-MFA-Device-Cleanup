import requests
from requests.auth import HTTPBasicAuth
import csv

DUO_IKEY = "EXAMPLE_IKEY"
DUO_SKEY = "EXAMPLE_SKEY"
DUO_HOST = "api-example.duosecurity.com"

# Example format:
# DUO_HOST = "api-123456.duosecurity.com"

BASE_URL = f"https://{DUO_HOST}/admin/v1"

# CSV file to store results
CSV_FILE = "duo_device_discovery.csv"


# Retrieve all users

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


# Discovery

def run_discovery():

    users = get_users()

    with open(CSV_FILE, "w", newline="") as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow([
            "username",
            "phone_id",
            "activated_timestamp"
        ])

        for user in users:

            username = user["username"]
            user_id = user["user_id"]

            devices = get_user_devices(user_id)

            if not devices:
                continue

            for device in devices:

                phone_id = device.get("phone_id")
                activated = device.get("activated")

                print(
                    f"User: {username} | Device: {phone_id} | Activated: {activated}"
                )

                writer.writerow([
                    username,
                    phone_id,
                    activated
                ])

# Run

if __name__ == "__main__":
    run_discovery()
