#!/usr/bin/env python3
"""
Script to get decryption policies from Mobile+Users folder (with plus sign)
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

def get_decryption_policies_mobile_plus_users(bearer_token):
    """Get decryption policies from Mobile+Users folder"""

    # Try different URL encoding variations for "Mobile+Users"
    folder_variations = [
        "Mobile+Users",           # Direct plus
        "Mobile%2BUsers",         # URL encoded plus
        "Mobile%20+%20Users",     # Space plus space encoded
        "Mobile%20%2B%20Users",   # Spaces and plus encoded
    ]

    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'Content-Type': 'application/json'
    }

    print(f"🔍 Searching for decryption policies in Mobile+Users folder...")
    print(f"📅 Timestamp: {datetime.now().isoformat()}")
    print("-" * 70)

    successful_results = []

    for folder_name in folder_variations:
        api_url = f"https://api.sase.paloaltonetworks.com/sse/config/v1/decryption-profiles?folder={folder_name}"

        print(f"\n🌐 Trying: {api_url}")

        try:
            response = requests.get(api_url, headers=headers)

            print(f"   📊 Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                policies = data.get('data', [])

                print(f"   ✅ SUCCESS! Found {len(policies)} decryption policies!")

                if policies:
                    successful_results.extend(policies)

                    for i, policy in enumerate(policies, 1):
                        print(f"      {i}. {policy.get('name', 'Unnamed')} (ID: {policy.get('id', 'N/A')})")
                        print(f"         Folder: {policy.get('folder', 'N/A')}")

            elif response.status_code == 400:
                error_data = response.json()
                print(f"   ⚠️  Bad request: {error_data.get('_errors', [{}])[0].get('message', 'Unknown error')}")
            elif response.status_code == 401:
                print(f"   ❌ Token expired or invalid")
            elif response.status_code == 403:
                print(f"   ❌ Access denied")
            elif response.status_code == 404:
                print(f"   ❌ Folder not found")
            else:
                print(f"   ❌ Status {response.status_code}: {response.text[:100]}")

        except requests.exceptions.RequestException as e:
            print(f"   ❌ Network error: {e}")
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON parsing error: {e}")

    return successful_results

def display_policies(policies):
    """Display policies in detailed format"""
    if not policies:
        print(f"\n❌ No decryption policies found in Mobile+Users folder.")
        return

    print(f"\n🎯 Decryption Policies in Mobile+Users folder:")
    print("=" * 70)

    for i, policy in enumerate(policies, 1):
        print(f"\n📋 {i}. {policy.get('name', 'Unnamed Policy')}")
        print(f"   🆔 ID: {policy.get('id', 'N/A')}")
        print(f"   📁 Folder: {policy.get('folder', 'N/A')}")
        print(f"   📝 Snippet: {policy.get('snippet', 'N/A')}")

        # SSL Protocol Settings
        ssl_settings = policy.get('ssl_protocol_settings', {})
        if ssl_settings:
            print(f"   🔐 SSL Protocol Settings:")
            print(f"      Min Version: {ssl_settings.get('min_version', 'N/A')}")
            print(f"      Max Version: {ssl_settings.get('max_version', 'N/A')}")

        # SSL Forward Proxy
        forward_proxy = policy.get('ssl_forward_proxy', {})
        if forward_proxy:
            print(f"   🔄 SSL Forward Proxy:")
            print(f"      Auto Include: {forward_proxy.get('auto_include_altname', 'N/A')}")
            print(f"      Block Client Cert: {forward_proxy.get('block_client_cert', 'N/A')}")
            print(f"      Block Expired Cert: {forward_proxy.get('block_expired_certificate', 'N/A')}")

        # SSL No Proxy
        no_proxy = policy.get('ssl_no_proxy', {})
        if no_proxy:
            print(f"   🚫 SSL No Proxy:")
            print(f"      Block Expired Cert: {no_proxy.get('block_expired_certificate', 'N/A')}")

        print("-" * 50)

def main():
    print("🎯 Prisma SASE - Mobile+Users Decryption Policies")
    print("=" * 70)

    # Load bearer token
    bearer_token = load_bearer_token()
    if not bearer_token:
        sys.exit(1)

    # Get decryption policies from Mobile+Users folder
    policies = get_decryption_policies_mobile_plus_users(bearer_token)

    # Display results
    display_policies(policies)

    if policies:
        # Save to file
        output_file = 'mobile_plus_users_decryption_policies.json'
        with open(output_file, 'w') as f:
            json.dump(policies, f, indent=2)

        print(f"\n💾 Results saved to {output_file}")

        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"   📁 Folder: Mobile+Users")
        print(f"   📋 Total Policies: {len(policies)}")
        print(f"   📅 Retrieved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Policy names list
        print(f"\n📝 Policy Names:")
        for i, policy in enumerate(policies, 1):
            print(f"   {i}. {policy.get('name', 'Unnamed')}")

        print(f"\n🎉 Successfully retrieved {len(policies)} decryption policies from Mobile+Users folder!")
    else:
        print(f"\n❌ No decryption policies found in Mobile+Users folder")

if __name__ == "__main__":
    main()