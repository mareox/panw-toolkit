#!/usr/bin/env python3
"""
Script to discover available Prisma SASE API endpoints and their structure
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

def test_endpoint(url, bearer_token, description=""):
    """Test a single endpoint"""
    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'Content-Type': 'application/json'
    }

    try:
        print(f"\n🔍 Testing: {description}")
        print(f"URL: {url}")

        response = requests.get(url, headers=headers, timeout=10)

        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ SUCCESS!")
                print(f"Response preview: {json.dumps(data, indent=2)[:500]}...")
                return True, data
            except:
                print("✅ SUCCESS! (Non-JSON response)")
                print(f"Response preview: {response.text[:500]}...")
                return True, response.text
        else:
            print(f"❌ FAILED: {response.text[:200]}")
            return False, None

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False, None

def main():
    print("Prisma SASE API Endpoint Discovery")
    print("=" * 50)

    bearer_token = load_bearer_token()
    if not bearer_token:
        sys.exit(1)

    # Common base URLs for Prisma SASE
    base_urls = [
        "https://api.sase.paloaltonetworks.com",
        "https://api.gpcloudservice.com",
        "https://api.prismaaccess.com"
    ]

    # Common endpoint patterns to test
    endpoint_patterns = [
        "/sse/config/v1",
        "/config/security/v1",
        "/config/v1",
        "/prisma-access/api/v1",
        "/api/sase/v1.0",
        "/restapi/v1.0",
        "/restapi/v2.0"
    ]

    # Policy-specific endpoints
    policy_endpoints = [
        "decryption-policies",
        "decryption-policy",
        "security-policies",
        "security-policy",
        "policies",
        "policy"
    ]

    successful_endpoints = []

    print(f"Testing base endpoints...")
    for base_url in base_urls:
        for pattern in endpoint_patterns:
            test_url = f"{base_url}{pattern}"
            success, data = test_endpoint(test_url, bearer_token, f"Base endpoint: {pattern}")
            if success:
                successful_endpoints.append(test_url)

                # If base endpoint works, try policy-specific endpoints
                for policy_endpoint in policy_endpoints:
                    policy_url = f"{test_url}/{policy_endpoint}"
                    p_success, p_data = test_endpoint(policy_url, bearer_token, f"Policy endpoint: {policy_endpoint}")
                    if p_success:
                        successful_endpoints.append(policy_url)

    print(f"\n" + "=" * 50)
    print(f"SUMMARY")
    print(f"=" * 50)

    if successful_endpoints:
        print(f"✅ Working endpoints found:")
        for endpoint in successful_endpoints:
            print(f"  • {endpoint}")
    else:
        print(f"❌ No working endpoints found")

    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "successful_endpoints": successful_endpoints
    }

    with open('endpoint_discovery_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Results saved to endpoint_discovery_results.json")

if __name__ == "__main__":
    main()