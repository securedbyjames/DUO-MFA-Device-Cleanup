<h1>DUO Mobile MFA Device Cleanup Project</h1>

<h2>Purpose of Project</h2>

Users currently have to contact our IT team in order to replace their MFA device to sign in to Google Workspace. In order to activate Duo Central which allows users to use a self-service portal to add new MFA devices, I must ensure every security risk is taken in to account. After evaluating risk, we have decided that we only want to allow one device at a time to be registered. Instead of manually removing devices, I created a script to automatically remove any and all devices that are not the most current device. 

<h2>Overview</h2>

This projects consists of two scripts: 

| Script | Purpose |
| ------- | ---------------- | 
| discovery.py     | Identifies users with multiple phones and reports which devices would be removed             | 
| cleanup.py       | Removes all phones except the newest device | 

<b>Workflow</b>

  1. Run the discovery script to generate a report
  2. Review the output CSV and console output
  3. Run the cleanup script to remove older devices

<h2>Key Features</h2>
  
  - Pulls users and devices via Duo Admin API
  - Detects users with multiple registered devices
  - Keeps the most recently activated device
  - Removes older devices automatically
  - Generates CSV audit logs
  - Provides dry-run mode for safe testing
  - Can be scheduled to run automatically (weekly or daily)

<h2>Summary</h2>

  - This project provides a simple automation workflow for managing MFA device sprawl in Duo:
  - Identify users with duplicate devices
  - Preserve the newest MFA device
  - Remove outdated registrations
  - Maintain a clean and secure MFA environment
