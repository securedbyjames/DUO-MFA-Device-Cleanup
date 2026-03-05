from duo_client import Admin
import os
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

# Load Duo API credentials
DUO_IKEY = os.getenv("DUO_IKEY")
DUO_SKEY = os.getenv("DUO_SKEY")
DUO_HOST = os.getenv("DUO_HOST")

# Initialize Duo API client
admin_api = Admin(
    ikey=DUO_IKEY,
    skey=DUO_SKEY,
    host=DUO_HOST
)


def cleanup():

    # Retrieve all phones from the Duo tenant
    phones = admin_api.get_phones()

    # Map user_id -> phones
    user_phones = defaultdict(list)

    for phone in phones:
        for owner in phone.get("users", []):
            user_phones[owner["user_id"]].append(phone)

    # Process each user's phones
    for user_id, phones in user_phones.items():

        if len(phones) < 2:
            continue

        # Sort by activation so oldest devices come first
        phones_sorted = sorted(phones, key=lambda p: p.get("activated", 0))

        # Delete every phone except the newest one
        phones_to_delete = phones_sorted[:-1]

        for index, phone in enumerate(phones_to_delete, start=1):

            phone_id = phone.get("phone_id")
            phone_number = phone.get("number") or "NO NUMBER PRESENT"

            admin_api.delete_phone(phone_id)

            print(
                f"removed phone {index}: {phone_number} | phone id: {phone_id}"
            )


if __name__ == "__main__":
    cleanup()
