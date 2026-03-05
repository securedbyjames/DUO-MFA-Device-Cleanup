from duo_client import Admin
import csv
import os
from dotenv import load_dotenv
from datetime import datetime
from collections import defaultdict

load_dotenv()

# Load Duo API credentials from .env
DUO_IKEY = os.getenv("DUO_IKEY")
DUO_SKEY = os.getenv("DUO_SKEY")
DUO_HOST = os.getenv("DUO_HOST")

# Initialize Duo Admin API client
admin_api = Admin(
    ikey=DUO_IKEY,
    skey=DUO_SKEY,
    host=DUO_HOST
)

# Create unique CSV name so files never overwrite
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
CSV_FILE = f"duo_device_discovery_{timestamp}.csv"


# Convert Unix timestamps returned by Duo into readable dates
def format_timestamp(ts):

    if not ts:
        return ""

    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def run_discovery():

    # Pull full datasets from Duo
    users = admin_api.get_users()
    phones = admin_api.get_phones()
    tokens = admin_api.get_tokens()

    # Map user_id -> user object for fast lookups
    user_map = {u["user_id"]: u for u in users}

    # Dictionaries mapping users to their phones/tokens
    user_phones = defaultdict(list)
    user_tokens = defaultdict(list)

    # Attach phones to users
    for phone in phones:
        for owner in phone.get("users", []):
            user_phones[owner["user_id"]].append(phone)

    # Attach hardware tokens to users
    for token in tokens:
        owner = token.get("user")
        if owner:
            user_tokens[owner["user_id"]].append(token)

    with open(CSV_FILE, "w", newline="") as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow([
            "username",
            "name",
            "email",
            "created",
            "last_login",
            "status",
            "phone_count",
            "hardware_tokens",
            "removal_plan"
        ])

        # Process users that have phones
        for user_id, phones in user_phones.items():

            if len(phones) < 2:
                continue

            user = user_map.get(user_id)
            if not user:
                continue

            username = user["username"]
            name = f"{user.get('firstname','')} {user.get('lastname','')}".strip()
            email = user.get("email") or ""
            status = user["status"]

            created = format_timestamp(user.get("created"))
            last_login = format_timestamp(user.get("last_login"))

            token_count = len(user_tokens[user_id])

            # Sort phones so oldest devices appear first
            phones_sorted = sorted(phones, key=lambda p: p.get("activated", 0))

            # Keep newest phone
            phones_to_remove = phones_sorted[:-1]

            removal_messages = []

            # Build list of devices that will be removed
            for index, phone in enumerate(phones_to_remove, start=1):

                phone_number = phone.get("number") or "NO NUMBER PRESENT"
                phone_id = phone.get("phone_id")

                removal_messages.append(
                    f"will remove phone {index}: {phone_number} | phone id: {phone_id}"
                )

            removal_message = ", ".join(removal_messages)

            print(
                f"{username} has {len(phones)} phones and {token_count} hardware tokens. {removal_message}"
            )

            writer.writerow([
                username,
                name,
                email,
                created,
                last_login,
                status,
                len(phones),
                token_count,
                removal_message
            ])

# Run
if __name__ == "__main__":
    run_discovery()
