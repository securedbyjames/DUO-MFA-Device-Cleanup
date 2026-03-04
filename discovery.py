import requests
from requests.auth import HTTPBasicAuth
import csv

# Replace these with your Duo Admin API credentials
DUO_IKEY = "EXAMPLE_IKEY"
DUO_SKEY = "EXAMPLE_SKEY"
DUO_HOST = "api-example.duosecurity.com"

BASE_URL = f"https://{DUO_HOST}/admin/v1"

# CSV file where discovery results will be written
CSV_FILE = "duo_device_discovery.csv"


# Retrieve all users from Duo
def get_users():

    url = f"{BASE_URL}/users"

    response = requests.get(
        url,
        auth=HTTPBasicAuth(DUO_IKEY, DUO_SKEY)
    )

    return response.json()["response"]


# Retrieve all phones from Duo
def get_phones():

    url = f"{BASE_URL}/phones"

    response = requests.get(
        url,
        auth=HTTPBasicAuth(DUO_IKEY, DUO_SKEY)
    )

    return response.json()["response"]


# Main discovery function
def run_discovery():

    users = get_users()
    phones = get_phones()

    # Create a mapping of user_id to username
    user_map = {u["user_id"]: u["username"] for u in users}

    with open(CSV_FILE, "w", newline="") as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow([
            "username",
            "phone_id",
            "activated_timestamp"
        ])

        for phone in phones:

            phone_id = phone.get("phone_id")
            activated = phone.get("activated")

            owners = phone.get("users", [])

            for owner in owners:

                user_id = owner.get("user_id")

                username = user_map.get(user_id, "unknown_user")

                print(f"{username} | {phone_id} | {activated}")

                writer.writerow([
                    username,
                    phone_id,
                    activated
                ])


if __name__ == "__main__":
    run_discovery()
