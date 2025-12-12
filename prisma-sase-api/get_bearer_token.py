#!/usr/bin/env python3
"""
Script to obtain bearer token for Prisma SASE API
"""

import requests
import json
import sys
from datetime import datetime

def get_bearer_token(client_id, client_secret, tsg_id):
    """
    Get bearer token from Prisma SASE API

    Args:
        client_id (str): Service account client ID
        client_secret (str): Service account client secret
        tsg_id (str): TSG ID extracted from the service account name

    Returns:
        dict: Token response containing access_token and other details
    """

    # Prisma SASE token endpoint
    token_url = "https://auth.apps.paloaltonetworks.com/oauth2/access_token"

    # Request headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Request payload
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': f'tsg_id:{tsg_id}'
    }

    try:
        print(f"Requesting bearer token for TSG ID: {tsg_id}")
        print(f"Client ID: {client_id}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("-" * 50)

        response = requests.post(token_url, headers=headers, data=data)

        if response.status_code == 200:
            token_data = response.json()
            print("✅ Bearer token obtained successfully!")
            print(f"Access Token: {token_data.get('access_token')}")
            print(f"Token Type: {token_data.get('token_type')}")
            print(f"Expires In: {token_data.get('expires_in')} seconds")

            return token_data
        else:
            print(f"❌ Failed to obtain bearer token")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Error making request: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing response: {e}")
        return None

def main():
    # Credentials from user input
    service_account = "scm-config-clone@1714969341.iam.panserviceaccount.com"
    client_secret = "e8c3ca45-0f0a-49f4-9ec9-cf8f5eefffd8"

    # Extract TSG ID from service account name
    tsg_id = service_account.split('@')[1].split('.')[0]
    client_id = service_account

    print("Prisma SASE API Bearer Token Generator")
    print("=" * 50)

    # Get the bearer token
    token_data = get_bearer_token(client_id, client_secret, tsg_id)

    if token_data:
        # Save token to file for future use
        with open('bearer_token.json', 'w') as f:
            json.dump(token_data, f, indent=2)
        print(f"\n💾 Token saved to bearer_token.json")

        return token_data.get('access_token')
    else:
        sys.exit(1)

if __name__ == "__main__":
    token = main()