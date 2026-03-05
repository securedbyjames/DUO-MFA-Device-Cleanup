from duo_client import Admin
import csv
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# DUO CONFIG

DUO_IKEY = os.getenv("DUO_IKEY")
DUO_SKEY = os.getenv("DUO_SKEY")
DUO_HOST = os.getenv("DUO_HOST")

if not DUO_IKEY or not DUO_SKEY or not DUO_HOST:
    raise ValueError("Missing Duo API environment variables.")

admin_api = Admin(
    ikey=DUO_IKEY,
    skey=DUO_SKEY,
    host=DUO_HOST
)

# Create unique CSV

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
CSV_FILE = f"duo_device_discovery_{timestamp}.csv"


# Timestamp formatter

def format_timestamp(ts):

    if not ts:
        return ""

    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


# Main functions

def run_discovery():

    users = admin_api.get_users()
    phones = admin_api.get_phones()
    tokens = admin_api.get_tokens()

    # Map Users

    user_map = {u["user_id"]: u for u in users}

    # Map phone to users

    user_phones = {}

    for phone in phones:

        owners = phone.get("users", [])

        for owner in owners:

            user_id = owner.get("user_id")

            if user_id not in user_phones:
                user_phones[user_id] = []

            user_phones[user_id].append(phone)

    # Map tokens

    user_tokens = {}

    for token in tokens:

        owner = token.get("user")

        if owner:

            user_id = owner.get("user_id")

            if user_id not in user_tokens:
                user_tokens[user_id] = []

            user_tokens[user_id].append(token)

    # Write CSV

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
            "phone1",
            "phone1_type",
            "phone2",
            "phone2_type",
            "action"
        ])

        # Processing users

        for user_id, phones in user_phones.items():

            user = user_map.get(user_id)

            if not user:
                continue

            phone_count = len(phones)

            if phone_count < 2:
                continue

            username = user.get("username")
            name = user.get("realname")
            email = user.get("email")
            status = user.get("status")

            created = format_timestamp(user.get("created"))
            last_login = format_timestamp(user.get("last_login"))

            token_count = len(user_tokens.get(user_id, []))

            # Sort phones by activation (oldest first)
            phones_sorted = sorted(
                phones,
                key=lambda p: p.get("activated", 0)
            )

            phone1 = phones_sorted[0]   # oldest phone
            phone2 = phones_sorted[-1]  # newest phone

            phone1_number = phone1.get("number")
            phone1_type = phone1.get("type")

            phone2_number = phone2.get("number")
            phone2_type = phone2.get("type")

            # Handle missing phone numbers
            if not phone1_number:
                display_number = "NO NUMBER PRESENT"
            else:
                display_number = phone1_number

            action = "WILL REMOVE PHONE 1"

            print(f"{username} has {phone_count} phones and {token_count} hardware tokens, WILL REMOVE PHONE 1 {display_number}")

            writer.writerow([
                username,
                name,
                email,
                created,
                last_login,
                status,
                phone_count,
                token_count,
                phone1_number,
                phone1_type,
                phone2_number,
                phone2_type,
                action
            ])

# Run 

if __name__ == "__main__":
    run_discovery()
