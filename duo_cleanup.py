from duo_client import Admin
import os
import csv
from dotenv import load_dotenv
from collections import defaultdict
from datetime import datetime

load_dotenv()

# Load Duo API credentials
DUO_IKEY = os.getenv("DUO_IKEY")
DUO_SKEY = os.getenv("DUO_SKEY")
DUO_HOST = os.getenv("DUO_HOST")

# Initialize Duo Admin API client
admin_api = Admin(
    ikey=DUO_IKEY,
    skey=DUO_SKEY,
    host=DUO_HOST
)

# Create unique CSV filename for removal log
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
CSV_FILE = f"duo_device_cleanup_{timestamp}.csv"


def cleanup():

    # Retrieve phones and users for reporting
    phones = admin_api.get_phones()
    users = admin_api.get_users()

    # Map user_id -> username
    user_map = {u["user_id"]: u["username"] for u in users}

    # Group phones by user
    user_phones = defaultdict(list)

    for phone in phones:
        for owner in phone.get("users", []):
            user_phones[owner["user_id"]].append(phone)

    # Open CSV log file
    with open(CSV_FILE, "w", newline="") as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow([
            "username",
            "phone_number",
            "phone_id",
            "removal_time"
        ])

        # Process each user's devices
        for user_id, phones in user_phones.items():

            if len(phones) < 2:
                continue

            username = user_map.get(user_id, "unknown_user")

            # Sort phones by activation date
            phones_sorted = sorted(
                phones,
                key=lambda p: p.get("activated", 0)
            )

            # All phones except newest will be removed
            phones_to_delete = phones_sorted[:-1]

            for index, phone in enumerate(phones_to_delete, start=1):

                phone_id = phone.get("phone_id")
                phone_number = phone.get("number") or "NO NUMBER PRESENT"

                # Remove phone from Duo
                admin_api.delete_phone(phone_id)

                removal_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                print(
                    f"removed phone {index}: {phone_number} | phone id: {phone_id}"
                )

                # Log removal to CSV
                writer.writerow([
                    username,
                    phone_number,
                    phone_id,
                    removal_time
                ])


if __name__ == "__main__":
    cleanup()
