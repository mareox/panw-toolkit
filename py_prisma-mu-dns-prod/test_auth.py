#!/usr/bin/env python3
"""
Authentication Test Script for Prisma SASE

This script tests ONLY the authentication to help diagnose credential issues.
"""

import sys
import yaml
import json
from pathlib import Path

print("=" * 80)
print("Prisma SASE Authentication Test")
print("=" * 80)
print()

# Load configuration
config_path = Path("config/config.yaml")

if not config_path.exists():
    print("❌ ERROR: config/config.yaml not found")
    print()
    print("Please create config/config.yaml from config/config.yaml.template")
    sys.exit(1)

print("[1/4] Loading configuration...")
try:
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    print("✓ Configuration loaded")
    print()
except Exception as e:
    print(f"❌ ERROR loading config: {e}")
    sys.exit(1)

# Display configuration (masked)
print("[2/4] Configuration details:")
print("-" * 80)
client_id = config['api']['client_id']
client_secret = config['api']['client_secret']
tsg_id = config['api']['tsg_id']

print(f"  Client ID:     {client_id}")
print(f"  Client Secret: {client_secret[:8]}...{client_secret[-4:]} (masked)")
print(f"  TSG ID:        {tsg_id}")
print()

# Check for placeholder values
warnings = []
if "your-client-id" in client_id.lower() or "example" in client_id.lower():
    warnings.append("⚠️  Client ID appears to be a placeholder/example value")

if len(client_secret) < 20:
    warnings.append("⚠️  Client Secret seems too short (should be a UUID)")

if "your" in str(tsg_id).lower() or "example" in str(tsg_id).lower():
    warnings.append("⚠️  TSG ID appears to be a placeholder/example value")

if warnings:
    print("Configuration Warnings:")
    for warning in warnings:
        print(f"  {warning}")
    print()

# Import SDK
print("[3/4] Loading Prisma SASE SDK...")
try:
    import prisma_sase
    print("✓ SDK loaded")
    print()
except ImportError:
    print("❌ ERROR: prisma_sase module not found")
    print()
    print("Please install dependencies:")
    print("  source mudns/bin/activate")
    print("  pip install -r requirements.txt")
    sys.exit(1)

# Test authentication
print("[4/4] Testing authentication...")
print("-" * 80)
print()

try:
    # Initialize SDK
    sdk = prisma_sase.API(controller="https://api.sase.paloaltonetworks.com")
    print("→ Connecting to: https://api.sase.paloaltonetworks.com")
    print()

    # Attempt authentication
    print("→ Authenticating with Service Account...")
    print(f"  Client ID: {client_id}")
    print(f"  TSG ID: {tsg_id}")
    print()

    result = sdk.interactive.login_secret(
        client_id=client_id,
        client_secret=client_secret,
        tsg_id=tsg_id
    )

    if result:
        print("=" * 80)
        print("✅ AUTHENTICATION SUCCESSFUL!")
        print("=" * 80)
        print()

        # Try to get some basic info
        print("Retrieving tenant information...")
        print()

        try:
            # Try to get profile or tenant info
            tenant_info = sdk.get.tenant_service_groups()

            if tenant_info and 'items' in tenant_info:
                print("Tenant Service Groups:")
                for tsg in tenant_info.get('items', []):
                    print(f"  - Name: {tsg.get('name', 'N/A')}")
                    print(f"    ID: {tsg.get('id', 'N/A')}")
                    print()

        except Exception as e:
            print(f"Note: Could not retrieve tenant info ({e})")
            print("This is normal - authentication was successful.")
            print()

        # Logout
        try:
            sdk.get.logout()
            print("✓ Logged out successfully")
        except:
            pass

        print()
        print("=" * 80)
        print("NEXT STEPS:")
        print("=" * 80)
        print()
        print("Your credentials are working! You can now run the main script:")
        print()
        print("  # Dry-run test:")
        print("  ./run.sh --dry-run -v")
        print()
        print("  # Or manually:")
        print("  source mudns/bin/activate")
        print("  python3 main.py --dry-run -v")
        print()

        sys.exit(0)

    else:
        print("=" * 80)
        print("❌ AUTHENTICATION FAILED")
        print("=" * 80)
        print()
        print("The SDK returned no result (login failed)")
        print()
        print("Possible reasons:")
        print("  1. Invalid Client ID or Client Secret")
        print("  2. Service Account has been disabled or deleted")
        print("  3. Incorrect TSG ID")
        print("  4. Service Account permissions are insufficient")
        print()
        print("To fix:")
        print("  1. Log into Prisma Access UI")
        print("  2. Go to: Settings → Identity & Access → Service Accounts")
        print("  3. Verify your Service Account exists and is enabled")
        print("  4. Check the Client ID matches exactly")
        print("  5. If needed, regenerate the Client Secret")
        print("  6. Verify TSG ID at: Settings → Service Setup → Tenant Service Group")
        print("  7. Update config/config.yaml with correct values")
        print()

        sys.exit(1)

except Exception as e:
    print("=" * 80)
    print("❌ AUTHENTICATION FAILED")
    print("=" * 80)
    print()
    print(f"Error: {str(e)}")
    print()

    error_str = str(e).lower()

    # Provide specific guidance based on error
    if "invalid_client" in error_str or "authentication failed" in error_str:
        print("This error means the credentials are invalid or expired.")
        print()
        print("SOLUTION:")
        print("  1. Log into Prisma Access UI")
        print("  2. Go to: Settings → Identity & Access → Service Accounts")
        print("  3. Check if 'scm-config-clone' service account exists")
        print("  4. If it exists, verify it's enabled")
        print("  5. If not, create a new Service Account:")
        print("     - Name: DNS-Config-Updater")
        print("     - Permissions:")
        print("       ✓ Prisma Access Config: Read & Write")
        print("       ✓ Service Setup: Read & Write")
        print("  6. Copy the NEW Client ID and Client Secret")
        print("  7. Get your TSG ID from: Settings → Service Setup")
        print("  8. Update config/config.yaml with the new credentials")
        print()

    elif "connection" in error_str or "network" in error_str:
        print("This appears to be a network connectivity issue.")
        print()
        print("SOLUTION:")
        print("  1. Check your internet connection")
        print("  2. Verify you can reach: https://api.sase.paloaltonetworks.com")
        print("  3. Check if you're behind a proxy or firewall")
        print()

    else:
        print("TROUBLESHOOTING:")
        print("  1. Verify credentials in config/config.yaml are correct")
        print("  2. Check Service Account status in Prisma Access UI")
        print("  3. Ensure Service Account has required permissions")
        print("  4. Verify TSG ID is correct")
        print()

    print("For more help, see: README.md - Troubleshooting section")
    print()

    sys.exit(1)
