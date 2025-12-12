#!/usr/bin/env python3
"""
Detailed Authentication Test for Prisma SASE
Tests authentication with verbose output
"""

import sys
import yaml
import json
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

print("=" * 80)
print("Prisma SASE Detailed Authentication Test")
print("=" * 80)
print()

# Load config
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

client_id = config['api']['client_id']
client_secret = config['api']['client_secret']
tsg_id = config['api']['tsg_id']

print(f"Client ID: {client_id}")
print(f"TSG ID: {tsg_id}")
print()

# Import SDK
import prisma_sase

print("Attempting authentication with detailed logging...")
print("-" * 80)
print()

# Initialize SDK
sdk = prisma_sase.API(controller="https://api.sase.paloaltonetworks.com")

# Try authentication
try:
    result = sdk.interactive.login_secret(
        client_id=client_id,
        client_secret=client_secret,
        tsg_id=tsg_id
    )

    print()
    print("=" * 80)
    print("Authentication result:")
    print(f"  Result: {result}")
    print(f"  Type: {type(result)}")
    print()

    if result:
        print("✅ Authentication appears successful!")
        print()
        print("Testing API access...")
        print("-" * 80)
        print()

        # Try various endpoints to see what works
        endpoints = [
            ("Tenant Service Groups", lambda: sdk.get.tenant_service_groups()),
            ("Service Setup", lambda: sdk.get.servicesetup()),
            ("Locations", lambda: sdk.get.locations()),
            ("Prisma Access Configs", lambda: sdk.get.prisma_access_configs()),
        ]

        for name, func in endpoints:
            try:
                print(f"→ Testing: {name}")
                response = func()
                if response:
                    print(f"  ✓ Success")
                    if isinstance(response, dict):
                        print(f"  Keys: {list(response.keys())[:5]}")
                else:
                    print(f"  ✗ No data returned")
            except AttributeError as e:
                print(f"  ⚠ Method not available: {e}")
            except Exception as e:
                print(f"  ✗ Error: {str(e)[:100]}")
            print()

        # Logout
        try:
            sdk.get.logout()
        except:
            pass

        print("=" * 80)
        print("CONCLUSION:")
        print("=" * 80)
        print()
        print("Authentication succeeded, but some API calls may have failed.")
        print("This is likely because:")
        print("  1. Service Account needs specific permissions")
        print("  2. Certain features/services are not enabled")
        print("  3. The API endpoints are different for your deployment")
        print()
        print("NEXT STEP:")
        print("  Use browser DevTools to discover the correct API endpoints")
        print("  See: API_IMPLEMENTATION_NOTES.md for detailed instructions")
        print()

    else:
        print("❌ Authentication failed - SDK returned False/None")
        print()
        print("This means the credentials were rejected.")
        print()
        print("CHECK:")
        print("  1. Is the Service Account enabled in Prisma Access UI?")
        print("  2. Does it have the correct permissions?")
        print("     - Prisma Access Config: Read & Write")
        print("     - Service Setup: Read & Write")
        print("  3. Is the TSG ID correct?")
        print()

except Exception as e:
    print()
    print("=" * 80)
    print("❌ ERROR DURING AUTHENTICATION")
    print("=" * 80)
    print()
    print(f"Exception: {e}")
    print()
    import traceback
    traceback.print_exc()
    print()
    print("This indicates a problem with the credentials or network.")
    print()
