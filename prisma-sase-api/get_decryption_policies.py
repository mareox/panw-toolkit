#!/usr/bin/env python3
"""
Script to get decryption policies from Prisma SASE API, filtered by Mobile Users folder
"""

import requests
import json
import sys
from datetime import datetime

def load_bearer_token():
    """Load bearer token from saved file"""
    try:
        with open('bearer_token.json', 'r') as f:
            token_data = json.load(f)
            return token_data.get('access_token')
    except FileNotFoundError:
        print("❌ Bearer token file not found. Please run get_bearer_token.py first.")
        return None
    except json.JSONDecodeError:
        print("❌ Error reading bearer token file.")
        return None

def get_decryption_policies(bearer_token, tsg_id):
    """
    Get decryption policies from Prisma SASE API

    Args:
        bearer_token (str): Bearer token for authentication
        tsg_id (str): TSG ID for the tenant

    Returns:
        list: List of decryption policies
    """

    # Try different Prisma SASE API endpoints for decryption policies
    base_urls = [
        f"https://api.sase.paloaltonetworks.com/sse/config/v1/decryption-policies",
        f"https://api.sase.paloaltonetworks.com/config/security/v1/decryption-policies",
        f"https://api.sase.paloaltonetworks.com/prisma-access/api/v1/decryption-policies"
    ]

    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'Content-Type': 'application/json',
        'X-PANW-Region': 'us'  # Adjust region if needed
    }

    try:
        print(f"Fetching decryption policies...")
        print(f"TSG ID: {tsg_id}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("-" * 50)

        # Try each URL until one works
        for i, api_url in enumerate(base_urls, 1):
            print(f"Trying endpoint {i}: {api_url}")
            response = requests.get(api_url, headers=headers)

            if response.status_code == 200:
                policies_data = response.json()
                print("✅ Successfully retrieved decryption policies!")
                return policies_data.get('data', []) or policies_data.get('result', []) or policies_data
            elif response.status_code == 404:
                print(f"   Endpoint not found (404), trying next...")
                continue
            else:
                print(f"   Status Code: {response.status_code}, Response: {response.text}")
                continue

        print(f"❌ All endpoints failed to retrieve decryption policies")
        return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Error making request: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing response: {e}")
        return None

def filter_mobile_users_policies(policies):
    """
    Filter policies that are under Mobile Users folder

    Args:
        policies (list): List of all decryption policies

    Returns:
        list: Filtered policies under Mobile Users folder
    """
    mobile_users_policies = []

    for policy in policies:
        # Check if policy is in Mobile Users folder
        folder = policy.get('folder', '')
        if 'Mobile Users' in folder or folder == 'Mobile Users':
            mobile_users_policies.append(policy)

    return mobile_users_policies

def display_policies(policies, folder_filter="Mobile Users"):
    """Display policies in a readable format"""
    if not policies:
        print(f"No decryption policies found in {folder_filter} folder.")
        return

    print(f"\n📋 Decryption Policies in {folder_filter} folder:")
    print("=" * 80)

    for i, policy in enumerate(policies, 1):
        print(f"{i}. Name: {policy.get('name', 'N/A')}")
        print(f"   ID: {policy.get('id', 'N/A')}")
        print(f"   Folder: {policy.get('folder', 'N/A')}")
        print(f"   Description: {policy.get('description', 'N/A')}")
        print(f"   Disabled: {policy.get('disabled', False)}")

        # Show source and destination if available
        if 'source' in policy:
            print(f"   Source: {policy['source']}")
        if 'destination' in policy:
            print(f"   Destination: {policy['destination']}")

        print("-" * 40)

    print(f"\nTotal policies found: {len(policies)}")

def main():
    print("Prisma SASE Decryption Policies Retrieval")
    print("=" * 50)

    # Load bearer token
    bearer_token = load_bearer_token()
    if not bearer_token:
        sys.exit(1)

    # TSG ID from the service account
    tsg_id = "1714969341"

    # Get all decryption policies
    all_policies = get_decryption_policies(bearer_token, tsg_id)

    if all_policies is None:
        sys.exit(1)

    print(f"Retrieved {len(all_policies)} total decryption policies")

    # Filter for Mobile Users folder
    mobile_users_policies = filter_mobile_users_policies(all_policies)

    # Display the filtered policies
    display_policies(mobile_users_policies)

    # Save results to file
    output_file = 'mobile_users_decryption_policies.json'
    with open(output_file, 'w') as f:
        json.dump(mobile_users_policies, f, indent=2)

    print(f"\n💾 Results saved to {output_file}")

if __name__ == "__main__":
    main()