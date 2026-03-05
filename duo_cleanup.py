from duo_client import Admin
import os
import csv
from dotenv import load_dotenv
from collections import defaultdict
from datetime import datetime

load_dotenv()

# =========================
# CONFIGURATION
# =========================

# TEST_USER = "james.vincent"   # Set to username to test single user
TEST_USER = None            # Uncomment to run for ALL users

DRY_RUN = True                # True = preview only (no deletions)
# DRY_RUN = False             # False = actually remove devices


# =========================
# DUO API SETUP
# =========================

DUO_IKEY = os.getenv("DUO_IKEY")
DUO_SKEY = os.getenv("DUO_SKEY")
DUO_HOST = os.getenv("DUO_HOST")

admin_api = Admin(
    ikey=DUO_IKEY,
    skey=DUO_SKEY,
    host=DUO_HOST
)

# =========================
# CSV LOG SETUP
# =========================

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
CSV_FILE = f"duo_device_cleanup_{timestamp}.csv"


def cleanup():

    print("\n========== DUO DEVICE CLEANUP ==========\n")

    if TEST_USER:
        print(f"Scanning for ONE User -> Only scanning user: {TEST_USER}")

    if DRY_RUN:
        print("DRY RUN MODE -> No devices will be deleted\n")

    phones = admin_api.get_phones()
    users = admin_api.get_users()

    user_map = {u["user_id"]: u["username"] for u in users}

    user_phones = defaultdict(list)

    for phone in phones:
        for owner in phone.get("users", []):
            user_phones[owner["user_id"]].append(phone)

    devices_to_remove = []

    # =========================
    # SCAN USERS
    # =========================

    for user_id, phones in user_phones.items():

        username = user_map.get(user_id, "unknown_user")

        # Skip users not matching TEST_USER
        if TEST_USER and username != TEST_USER:
            continue

        if len(phones) < 2:
            continue

        phones_sorted = sorted(
            phones,
            key=lambda p: p.get("activated", 0)
        )

        phones_to_delete = phones_sorted[:-1]

        for phone in phones_to_delete:

            devices_to_remove.append({
                "username": username,
                "phone_id": phone.get("phone_id"),
                "phone_number": phone.get("number") or "NO NUMBER PRESENT"
            })

    # =========================
    # SHOW PREVIEW
    # =========================

    if not devices_to_remove:
        print("No devices require cleanup.")
        return

    print("\nDevices marked for removal:\n")

    for i, device in enumerate(devices_to_remove, start=1):

        print(
            f"{i}. user: {device['username']} | "
            f"phone: {device['phone_number']} | "
            f"phone_id: {device['phone_id']}"
        )

    print(f"\nTotal devices to remove: {len(devices_to_remove)}")

    # =========================
    # CONFIRMATION PROMPT
    # =========================

    confirm = input("\nProceed with removal? (y/n): ")

    if confirm.lower() != "y":
        print("\nOperation cancelled.")
        return

    # =========================
    # CSV LOG FILE
    # =========================

    with open(CSV_FILE, "w", newline="") as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow([
            "username",
            "phone_number",
            "phone_id",
            "removal_time"
        ])

        # =========================
        # REMOVE DEVICES
        # =========================

        for index, device in enumerate(devices_to_remove, start=1):

            username = device["username"]
            phone_number = device["phone_number"]
            phone_id = device["phone_id"]

            if not DRY_RUN:
                admin_api.delete_phone(phone_id)

            removal_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print(
                f"removed phone {index}: {phone_number} | phone id: {phone_id}"
            )

            writer.writerow([
                username,
                phone_number,
                phone_id,
                removal_time
            ])

    print(f"\nCleanup complete. Log saved to: {CSV_FILE}")


if __name__ == "__main__":
    cleanup()
