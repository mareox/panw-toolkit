#!/usr/bin/env python3
"""
List current DNS configuration for all Mobile Users regions
"""

import json
import yaml
import logging
import sys
from pathlib import Path
from typing import Dict, Any

from src.auth import PrismaAuth
from src.dns_config import MobileUsersDNSConfig


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

logger = logging.getLogger(__name__)


def display_dns_config(config: Dict[str, Any]):
    """
    Display DNS configuration in a readable format

    Args:
        config: DNS configuration dictionary
    """
    print("=" * 100)
    print("MOBILE USERS DNS CONFIGURATION")
    print("=" * 100)
    print()

    print(f"Configuration ID: {config.get('id')}")
    print(f"Name: {config.get('name')}")
    print(f"Folder: {config.get('folder')}")
    print()

    dns_servers = config.get('dns_servers', [])

    if not dns_servers:
        print("No DNS configuration found.")
        return

    print(f"Found {len(dns_servers)} regions with DNS configuration:")
    print()

    # Display each region
    for idx, region in enumerate(dns_servers, 1):
        region_name = region.get('name', 'Unknown')
        print(f"{idx:2d}. Region: {region_name}")
        print("-" * 100)

        # Primary DNS
        primary_dns = region.get('primary', 'Not configured')
        print(f"    Primary DNS:   {primary_dns}")

        # Secondary DNS
        secondary_dns = region.get('secondary', 'Not configured')
        print(f"    Secondary DNS: {secondary_dns}")

        # Internal domain resolution rules
        internal_rules = region.get('internal_domain_resolution', [])
        if internal_rules:
            print(f"    Internal Domain Resolution Rules: {len(internal_rules)}")
            for rule_idx, rule in enumerate(internal_rules, 1):
                rule_name = rule.get('name', 'Unnamed')
                domains = rule.get('internal_domain_suffix', [])
                dns_servers_in_rule = rule.get('dns_servers', [])

                print(f"      Rule {rule_idx}: {rule_name}")
                print(f"        DNS Servers: {', '.join(dns_servers_in_rule) if dns_servers_in_rule else 'Not configured'}")
                print(f"        Domains ({len(domains)}): {', '.join(domains[:3])}{' ...' if len(domains) > 3 else ''}")
        else:
            print(f"    Internal Domain Resolution Rules: None")

        # Public DNS
        public_dns = region.get('public_dns', {})
        if public_dns:
            dns_type = public_dns.get('dns_type', 'Not configured')
            print(f"    Public DNS Type: {dns_type}")
            if dns_type == 'custom':
                custom_primary = public_dns.get('primary', '')
                custom_secondary = public_dns.get('secondary', '')
                print(f"      Custom Primary: {custom_primary}")
                print(f"      Custom Secondary: {custom_secondary}")

        print()


def save_to_file(config: Dict[str, Any], filename: str = "current_dns_config.json"):
    """Save configuration to a JSON file"""
    output_dir = Path("backup")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / filename

    with open(output_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"✓ Full configuration saved to: {output_path}")
    print()


def main():
    """Main execution function"""

    try:
        # Load configuration
        config_path = 'config/config.yaml'

        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # Authenticate to Prisma SASE
        logger.info("Authenticating to Prisma SASE...")
        print()

        auth = PrismaAuth(
            client_id=config['api']['client_id'],
            client_secret=config['api']['client_secret'],
            tsg_id=config['api']['tsg_id']
        )
        sdk = auth.authenticate()

        # Initialize DNS configuration manager
        dns_manager = MobileUsersDNSConfig(sdk)

        # Get current DNS settings
        logger.info("Retrieving current DNS configuration...")
        print()

        dns_config = dns_manager.get_dns_settings()

        # Display configuration
        display_dns_config(dns_config)

        # Save to file
        save_to_file(dns_config)

        print("=" * 100)
        print("REGION SELECTION")
        print("=" * 100)
        print()
        print("To update specific regions, you can:")
        print()
        print("1. Use the --regions option with main.py (if implemented)")
        print("   Example: python3 main.py --regions worldwide,emea,apac")
        print()
        print("2. Edit the configuration programmatically to filter regions")
        print()
        print("3. Current behavior: Updates ALL regions listed above")
        print()

        # Logout
        auth.logout()

        sys.exit(0)

    except KeyboardInterrupt:
        logger.warning("\nOperation cancelled by user")
        sys.exit(130)

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
