#!/usr/bin/env python3
"""
Generate Bearer Token for Prisma SASE API

This script generates an OAuth2 bearer token that you can use to:
- Test API endpoints manually with curl or Postman
- Explore the Prisma Access API
- Debug authentication issues
"""

import sys
import yaml
import json
import requests
from datetime import datetime, timedelta

print("=" * 80)
print("Prisma SASE Bearer Token Generator")
print("=" * 80)
print()

# Load configuration
try:
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    print("❌ ERROR: config/config.yaml not found")
    sys.exit(1)

client_id = config['api']['client_id']
client_secret = config['api']['client_secret']
tsg_id = config['api']['tsg_id']

print("[1/3] Loaded credentials from config/config.yaml")
print(f"  Client ID: {client_id}")
print(f"  TSG ID: {tsg_id}")
print()

# Request token
print("[2/3] Requesting OAuth2 token from Prisma SASE...")
print()

auth_url = "https://auth.apps.paloaltonetworks.com/auth/v1/oauth2/access_token"

try:
    response = requests.post(
        auth_url,
        auth=(client_id, client_secret),
        data={
            'grant_type': 'client_credentials',
            'scope': f'tsg_id:{tsg_id} email profile'
        },
        headers={
            'Accept': 'application/json'
        }
    )

    if response.status_code == 200:
        token_data = response.json()

        access_token = token_data['access_token']
        expires_in = token_data['expires_in']
        token_type = token_data['token_type']

        # Calculate expiration time
        expires_at = datetime.now() + timedelta(seconds=expires_in)

        print("✅ Token generated successfully!")
        print()
        print("=" * 80)
        print("TOKEN INFORMATION")
        print("=" * 80)
        print()
        print(f"Token Type: {token_type}")
        print(f"Expires In: {expires_in} seconds ({expires_in // 60} minutes)")
        print(f"Expires At: {expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("=" * 80)
        print("BEARER TOKEN")
        print("=" * 80)
        print()
        print(access_token)
        print()

        # Save to file
        print("[3/3] Saving token information...")
        print()

        token_file = {
            'access_token': access_token,
            'token_type': token_type,
            'expires_in': expires_in,
            'expires_at': expires_at.isoformat(),
            'tsg_id': tsg_id,
            'generated_at': datetime.now().isoformat()
        }

        with open('bearer_token.json', 'w') as f:
            json.dump(token_file, f, indent=2)

        print("✓ Token saved to: bearer_token.json")
        print()

        # Show usage examples
        print("=" * 80)
        print("USAGE EXAMPLES")
        print("=" * 80)
        print()
        print("1. Using curl:")
        print()
        print('curl -H "Authorization: Bearer YOUR_TOKEN" \\')
        print('     -H "Content-Type: application/json" \\')
        print('     https://api.sase.paloaltonetworks.com/sse/config/v1/...')
        print()
        print("2. Using Postman:")
        print()
        print("   - Authorization Type: Bearer Token")
        print(f"   - Token: {access_token[:50]}...")
        print()
        print("3. Load from file in scripts:")
        print()
        print("   import json")
        print("   with open('bearer_token.json') as f:")
        print("       token_data = json.load(f)")
        print("       token = token_data['access_token']")
        print()

        # Create a ready-to-use curl example
        print("=" * 80)
        print("QUICK TEST - List Locations")
        print("=" * 80)
        print()
        print("Run this command to test your token:")
        print()
        print(f'curl -H "Authorization: Bearer {access_token}" \\')
        print('     https://api.sase.paloaltonetworks.com/sse/config/v1/locations')
        print()

        # Export token as environment variable
        print("=" * 80)
        print("EXPORT AS ENVIRONMENT VARIABLE")
        print("=" * 80)
        print()
        print("Bash/Linux:")
        print(f'export PRISMA_TOKEN="{access_token}"')
        print()
        print("PowerShell:")
        print(f'$env:PRISMA_TOKEN="{access_token}"')
        print()
        print("Then use: curl -H \"Authorization: Bearer $PRISMA_TOKEN\" ...")
        print()

        # Important notes
        print("=" * 80)
        print("IMPORTANT NOTES")
        print("=" * 80)
        print()
        print(f"⏰ This token expires in {expires_in // 60} minutes")
        print("🔒 Keep this token secure - it has full API access")
        print("🔄 Run this script again to generate a new token when it expires")
        print()
        print("📝 Common API Base URLs:")
        print("   - Config API: https://api.sase.paloaltonetworks.com/sse/config/v1")
        print("   - MT Config:  https://api.sase.paloaltonetworks.com/mt/config/v1")
        print()

        sys.exit(0)

    else:
        print("❌ ERROR: Token generation failed")
        print()
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        print()

        if response.status_code == 401:
            print("This usually means:")
            print("  - Invalid Client ID or Client Secret")
            print("  - Service Account has been disabled")
            print("  - Incorrect credentials in config/config.yaml")

        sys.exit(1)

except requests.exceptions.RequestException as e:
    print("❌ ERROR: Network request failed")
    print()
    print(f"Error: {e}")
    print()
    print("Check your internet connection and try again.")
    sys.exit(1)

except Exception as e:
    print("❌ ERROR: Unexpected error")
    print()
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
