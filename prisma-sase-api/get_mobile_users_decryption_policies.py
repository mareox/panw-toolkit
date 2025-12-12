#!/usr/bin/env python3
"""
Final script to get decryption policies (decryption profiles) from Mobile Users folder
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

def get_decryption_policies(bearer_token):
    """Get decryption policies (profiles) from Mobile Users folder"""

    # Correct endpoint for decryption profiles in Mobile Users folder
    api_url = "https://api.sase.paloaltonetworks.com/sse/config/v1/decryption-profiles?folder=Mobile%20Users"

    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'Content-Type': 'application/json'
    }

    try:
        print(f"🔍 Fetching decryption policies from Mobile Users folder...")
        print(f"🌐 URL: {api_url}")
        print(f"📅 Timestamp: {datetime.now().isoformat()}")
        print("-" * 70)

        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            policies = data.get('data', [])

            print(f"✅ Successfully retrieved {len(policies)} decryption policies!")
            print("=" * 70)

            # Display each policy
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
                    print(f"      Key Exchange: {ssl_settings.get('key_exchange_algorithms', 'N/A')}")
                    print(f"      Encryption: {ssl_settings.get('encryption_algorithms', 'N/A')}")
                    print(f"      Authentication: {ssl_settings.get('authentication_algorithms', 'N/A')}")

                # SSL Forward Proxy
                forward_proxy = policy.get('ssl_forward_proxy', {})
                if forward_proxy:
                    print(f"   🔄 SSL Forward Proxy:")
                    print(f"      Auto Include: {forward_proxy.get('auto_include_altname', 'N/A')}")
                    print(f"      Block Client Cert: {forward_proxy.get('block_client_cert', 'N/A')}")
                    print(f"      Block Expired Cert: {forward_proxy.get('block_expired_certificate', 'N/A')}")
                    print(f"      Block Unknown Cert: {forward_proxy.get('block_unknown_certificate', 'N/A')}")
                    print(f"      Strip ALG: {forward_proxy.get('strip_alpn', 'N/A')}")

                # SSL No Proxy
                no_proxy = policy.get('ssl_no_proxy', {})
                if no_proxy:
                    print(f"   🚫 SSL No Proxy:")
                    print(f"      Block Expired Cert: {no_proxy.get('block_expired_certificate', 'N/A')}")
                    print(f"      Block Unknown Cert: {no_proxy.get('block_unknown_certificate', 'N/A')}")

                print("-" * 50)

            # Save to file
            output_file = 'mobile_users_decryption_policies_final.json'
            with open(output_file, 'w') as f:
                json.dump(policies, f, indent=2)

            print(f"\n💾 Results saved to {output_file}")

            return policies

        else:
            print(f"❌ Failed to retrieve decryption policies")
            print(f"📊 Status Code: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return None

def main():
    print("🎯 Prisma SASE - Mobile Users Decryption Policies")
    print("=" * 70)

    # Load bearer token
    bearer_token = load_bearer_token()
    if not bearer_token:
        sys.exit(1)

    # Get decryption policies
    policies = get_decryption_policies(bearer_token)

    if policies:
        print(f"\n🎉 Successfully retrieved {len(policies)} decryption policies from Mobile Users folder!")

        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"   📁 Folder: Mobile Users")
        print(f"   📋 Total Policies: {len(policies)}")
        print(f"   📅 Retrieved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Policy names list
        print(f"\n📝 Policy Names:")
        for i, policy in enumerate(policies, 1):
            print(f"   {i}. {policy.get('name', 'Unnamed')}")

    else:
        print(f"\n❌ Failed to retrieve decryption policies")
        sys.exit(1)

if __name__ == "__main__":
    main()