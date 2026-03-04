<h1>DUO Mobile MFA Device Cleanup Project</h1>

<h2>Purpose of Project</h2>

Users currently have to contact our IT team in order to replace their MFA device to sign in to Google Workspace. In order to activate Duo Central which allows users to use a self-service portal to add new MFA devices, I must ensure every security risk is taken in to account. After evaluating risk, we have decided that we only want to allow one device at a time to be registered. Instead of manually removing devices, I created a script to automatically remove the previous device that was assigned to the user once a new device is registered.

<h2>Key Features</h2>
  
  - Pulls users and devices via Duo Admin API

  - Detects users with multiple registered devices

  - Keeps the most recently activated device

  - Removes older devices automatically

  - Generates CSV audit logs

  - Provides dry-run mode for safe testing
  
  - Can be scheduled to run automatically (weekly or daily)

<h2>How It Works</h2>

  - Scheduler > Python Script > Duo Admin API > Retrieve Users > Retrieve Devices > Sort Devices by Activation Date > Keep Most Recent Device > Remove Older Device > Log Actions to CSV
  - The script is scheduled to run automatically using Task Scheduler on a weekly basis.

<h2>Safe Testing Process</h2>

  - Run discovery script

  - Verify API field names

  - Run dry-run script

  - Confirm expected devices would be removed

  - Test with a small user set

  - Deploy production script

  - Schedule automation
