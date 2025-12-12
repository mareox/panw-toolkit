"""
DNS Configuration Manager for Prisma Access Mobile Users
"""

import json
import logging
import requests
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import prisma_sase

logger = logging.getLogger(__name__)


def load_region_mappings() -> Dict[str, str]:
    """
    Load region name mappings from config file if it exists.

    Returns:
        Dictionary mapping technical names to friendly display names
    """
    mappings_file = Path("config/region_mappings.yaml")

    if mappings_file.exists():
        try:
            with open(mappings_file, 'r') as f:
                data = yaml.safe_load(f)
                return data.get('region_names', {})
        except Exception as e:
            logger.warning(f"Could not load region mappings: {e}")
            return {}
    return {}


def get_friendly_region_name(technical_name: str, mappings: Dict[str, str] = None) -> str:
    """
    Get friendly display name for a region.

    Args:
        technical_name: Technical region name (e.g., 'ip-pool-group-1')
        mappings: Optional mapping dictionary

    Returns:
        Friendly name if mapping exists, otherwise technical name
    """
    if mappings is None:
        mappings = load_region_mappings()

    return mappings.get(technical_name, technical_name)


class MobileUsersDNSConfig:
    """Manage Mobile Users DNS Configuration"""

    def __init__(self, sdk: prisma_sase.API):
        """
        Initialize DNS Configuration Manager

        Args:
            sdk: Authenticated Prisma SASE SDK instance
        """
        self.sdk = sdk
        self.base_url = "https://api.sase.paloaltonetworks.com"

    def _get_access_token(self) -> str:
        """
        Get OAuth2 access token from the SDK session.

        Returns:
            Access token string

        Raises:
            Exception: If no valid session found
        """
        # The SDK stores the access token in the authorization header
        if hasattr(self.sdk, '_session') and self.sdk._session:
            # Check if authorization header exists
            if hasattr(self.sdk._session, 'headers') and 'authorization' in self.sdk._session.headers:
                auth_header = self.sdk._session.headers['authorization']
                # Extract token from "Bearer <token>"
                if auth_header.startswith('Bearer '):
                    return auth_header.replace('Bearer ', '')

        # Fallback: Try to get from token_session dict if it exists
        if hasattr(self.sdk, 'token_session') and isinstance(self.sdk.token_session, dict):
            token = self.sdk.token_session.get('access_token', '')
            if token:
                return token

        raise Exception("No valid access token found. Please authenticate first.")

    def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for API requests.

        Returns:
            Dictionary of headers
        """
        return {
            'Authorization': f'Bearer {self._get_access_token()}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def get_dns_settings(self) -> Dict[str, Any]:
        """
        Retrieve current Mobile Users DNS settings from Prisma Access.

        Uses the Mobile Agent Infrastructure Settings API:
        GET /sse/config/v1/mobile-agent/infrastructure-settings

        Returns:
            dict: Current DNS configuration including all regions and dns_servers
        """
        try:
            logger.info("Fetching Mobile Users DNS configuration...")

            # Mobile Agent Infrastructure Settings endpoint
            url = f"{self.base_url}/sse/config/v1/mobile-agent/infrastructure-settings"

            response = requests.get(url, headers=self._get_headers(), timeout=30)

            if response.status_code == 200:
                data = response.json()
                # API returns a list with one configuration object
                if isinstance(data, list) and len(data) > 0:
                    config = data[0]
                    logger.info(f"Successfully retrieved configuration for: {config.get('name')}")
                    logger.info(f"Regions found: {[r.get('name') for r in config.get('dns_servers', [])]}")
                    return config
                else:
                    raise Exception("Unexpected response format: expected list with configuration")
            else:
                error_text = response.text[:500]
                raise Exception(f"Failed to retrieve DNS settings: {response.status_code} - {error_text}")

        except Exception as e:
            logger.error(f"Error retrieving DNS settings: {e}")
            raise

    def backup_config(self, config: Dict[str, Any], backup_dir: str = "backup") -> str:
        """
        Backup current configuration to file

        Args:
            config: Configuration to backup
            backup_dir: Directory to store backup

        Returns:
            Path to backup file
        """
        try:
            backup_path = Path(backup_dir)
            backup_path.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_path / f"dns_config_backup_{timestamp}.json"

            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)

            logger.info(f"Configuration backed up to {backup_file}")
            return str(backup_file)

        except Exception as e:
            logger.error(f"Error backing up configuration: {str(e)}")
            raise

    def update_dns_config(
        self,
        domains: List[str],
        rule_name: str = "CustomDNS",
        dry_run: bool = True,
        regions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Update DNS configuration with custom domain resolution rule.

        This will:
        1. Add a new Internal DNS Match rule named {rule_name} to specified regions (or ALL if not specified)
        2. Include the provided domains in the domain_list
        3. Use existing DNS servers (primary/secondary from first region)

        Args:
            domains: List of domains for internal resolution
            rule_name: Name of the DNS resolution rule (default: CustomDNS)
            dry_run: If True, only simulate changes without applying
            regions: Optional list of region names to update. If None, updates all regions.

        Returns:
            Updated configuration dictionary

        Raises:
            Exception: If update fails
        """
        try:
            logger.info(f"{'[DRY RUN] ' if dry_run else ''}Updating DNS configuration...")

            # Get current configuration
            current_config = self.get_dns_settings()

            # Backup current configuration
            if not dry_run:
                backup_file = self.backup_config(current_config)
                logger.info(f"Configuration backed up to: {backup_file}")

            # Process configuration updates
            updated_config = self._process_dns_update(
                current_config,
                domains,
                rule_name,
                regions
            )

            if dry_run:
                logger.info("\n" + "=" * 80)
                logger.info("[DRY RUN] Changes Preview")
                logger.info("=" * 80)
                self._show_changes_preview(current_config, updated_config, rule_name, domains)
                logger.info("=" * 80)
                return updated_config

            # Apply changes via PUT request
            logger.info("Applying DNS configuration changes...")
            config_id = current_config.get('id')
            # Note: ID must be a query parameter, not in the path
            url = f"{self.base_url}/sse/config/v1/mobile-agent/infrastructure-settings?id={config_id}"

            response = requests.put(
                url,
                headers=self._get_headers(),
                json=updated_config,
                timeout=30
            )

            if response.status_code in [200, 201]:
                logger.info("✓ DNS configuration updated successfully")
                logger.info("\nNOTE: You must COMMIT the changes in Strata Cloud Manager for them to take effect!")
                return response.json()
            else:
                error_text = response.text[:500]
                raise Exception(f"Failed to update DNS configuration: {response.status_code} - {error_text}")

        except Exception as e:
            logger.error(f"Error updating DNS configuration: {str(e)}")
            raise

    def _process_dns_update(
        self,
        config: Dict[str, Any],
        domains: List[str],
        rule_name: str,
        regions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Process DNS configuration updates.

        Structure:
        {
            "dns_servers": [
                {
                    "name": "worldwide",
                    "internal_dns_match": [
                        {
                            "name": "CustomDNS",
                            "primary": {"dns_server": "10.208.140.13"},
                            "secondary": {"dns_server": "10.213.13.13"},
                            "domain_list": ["*.example.com", ...]
                        }
                    ]
                }
            ]
        }

        Args:
            config: Current configuration
            domains: List of domains for internal resolution
            rule_name: Name of the DNS resolution rule
            regions: Optional list of region names to update. If None, updates all regions.

        Returns:
            Updated configuration dictionary
        """
        import copy
        updated_config = copy.deepcopy(config)

        # Get DNS servers from existing configuration
        dns_servers = updated_config.get('dns_servers', [])

        if not dns_servers:
            raise Exception("No DNS servers/regions found in current configuration")

        # Fallback DNS servers if a region has no existing internal_dns_match rules
        fallback_primary = "10.208.140.13"
        fallback_secondary = "10.213.13.13"

        # Add CustomDNS rule to specified regions (or ALL if regions=None)
        regions_updated = []
        for server in dns_servers:
            region_name = server.get('name')

            # Skip if regions filter is specified and this region is not in the list
            if regions is not None and region_name not in regions:
                continue

            # Ensure internal_dns_match exists
            if 'internal_dns_match' not in server:
                server['internal_dns_match'] = []

            internal_dns_match = server['internal_dns_match']

            # Check if rule already exists
            existing_rule = None
            for rule in internal_dns_match:
                if rule.get('name') == rule_name:
                    existing_rule = rule
                    break

            if existing_rule:
                logger.info(f"Region '{region_name}': Updating existing rule '{rule_name}' - preserving DNS servers")
                # Merge domains (add new ones, keep existing unique)
                # IMPORTANT: Do NOT modify primary/secondary DNS servers - only update domain_list
                existing_domains = existing_rule.get('domain_list', [])
                merged_domains = list(set(existing_domains + domains))
                existing_rule['domain_list'] = sorted(merged_domains)
                logger.info(f"  Preserved Primary DNS: {existing_rule.get('primary', {}).get('dns_server', 'N/A')}")
                logger.info(f"  Preserved Secondary DNS: {existing_rule.get('secondary', {}).get('dns_server', 'N/A')}")
            else:
                # Get DNS servers from THIS region's existing internal_dns_match rules
                region_primary = fallback_primary
                region_secondary = fallback_secondary

                # Look for existing rules in this specific region to get DNS servers
                if internal_dns_match and len(internal_dns_match) > 0:
                    first_rule = internal_dns_match[0]
                    if 'primary' in first_rule and 'dns_server' in first_rule['primary']:
                        region_primary = first_rule['primary']['dns_server']
                    if 'secondary' in first_rule and 'dns_server' in first_rule['secondary']:
                        region_secondary = first_rule['secondary']['dns_server']

                logger.info(f"Region '{region_name}': Creating new rule '{rule_name}'")
                logger.info(f"  Using Primary DNS: {region_primary}")
                logger.info(f"  Using Secondary DNS: {region_secondary}")

                new_rule = {
                    'name': rule_name,
                    'primary': {
                        'dns_server': region_primary
                    },
                    'secondary': {
                        'dns_server': region_secondary
                    },
                    'domain_list': sorted(domains)
                }
                internal_dns_match.append(new_rule)

            regions_updated.append(region_name)

        logger.info(f"Updated {len(regions_updated)} regions: {', '.join(regions_updated)}")

        return updated_config

    def _show_changes_preview(
        self,
        current_config: Dict[str, Any],
        updated_config: Dict[str, Any],
        rule_name: str,
        domains: List[str]
    ):
        """
        Show preview of changes that will be made.

        Args:
            current_config: Current configuration
            updated_config: Updated configuration
            rule_name: Name of the DNS rule
            domains: List of domains
        """
        dns_servers = updated_config.get('dns_servers', [])
        region_mappings = load_region_mappings()

        print(f"\nConfiguration ID: {updated_config.get('id')}")
        print(f"Name: {updated_config.get('name')}")
        print(f"Folder: {updated_config.get('folder')}")
        print()
        print(f"Will add/update rule '{rule_name}' with {len(domains)} domains")
        print()

        for server in dns_servers:
            region_name = server.get('name')
            friendly_name = get_friendly_region_name(region_name, region_mappings)
            internal_matches = server['internal_dns_match']

            # Find the CustomDNS rule
            custom_rule = None
            for rule in internal_matches:
                if rule.get('name') == rule_name:
                    custom_rule = rule
                    break

            if custom_rule:
                # Show friendly name if different from technical name
                if friendly_name != region_name:
                    print(f"Region: {friendly_name} ({region_name})")
                else:
                    print(f"Region: {region_name}")

                print(f"  Rule: {custom_rule.get('name')}")
                print(f"  Primary DNS: {custom_rule['primary']['dns_server']}")
                print(f"  Secondary DNS: {custom_rule['secondary']['dns_server']}")
                print(f"  Domains ({len(custom_rule['domain_list'])}):")
                for domain in custom_rule['domain_list'][:10]:
                    print(f"    - {domain}")
                if len(custom_rule['domain_list']) > 10:
                    print(f"    ... and {len(custom_rule['domain_list']) - 10} more")
                print()

        print("\nNOTE: This is a dry-run. No changes will be applied.")
        print("Run without --dry-run to apply changes.")

    def get_all_regions(self) -> List[str]:
        """
        Get list of all configured DNS regions.

        Returns:
            List of region names
        """
        try:
            logger.info("Fetching all regions...")

            config = self.get_dns_settings()
            dns_servers = config.get('dns_servers', [])

            regions = [server.get('name', '') for server in dns_servers]
            logger.info(f"Found {len(regions)} regions: {', '.join(regions)}")

            return regions

        except Exception as e:
            logger.error(f"Error fetching regions: {str(e)}")
            raise

    def validate_update(self, config: Dict[str, Any]) -> bool:
        """
        Validate DNS configuration before applying.

        Args:
            config: Configuration to validate

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        try:
            logger.info("Validating DNS configuration...")

            if not config:
                raise ValueError("Configuration is empty")

            # Validate required fields
            if 'id' not in config:
                raise ValueError("Configuration missing 'id' field")

            if 'dns_servers' not in config:
                raise ValueError("Configuration missing 'dns_servers' field")

            dns_servers = config.get('dns_servers', [])
            if not dns_servers:
                raise ValueError("No DNS servers/regions found")

            # Validate each region
            for server in dns_servers:
                region_name = server.get('name')
                if not region_name:
                    raise ValueError("Region missing 'name' field")

                internal_matches = server.get('internal_dns_match', [])
                for rule in internal_matches:
                    if 'name' not in rule:
                        raise ValueError(f"Region '{region_name}': DNS rule missing 'name' field")
                    if 'domain_list' not in rule:
                        raise ValueError(f"Region '{region_name}': DNS rule '{rule['name']}' missing 'domain_list'")
                    if 'primary' not in rule or 'dns_server' not in rule['primary']:
                        raise ValueError(f"Region '{region_name}': DNS rule '{rule['name']}' missing primary DNS server")

            logger.info("✓ Configuration validation passed")
            return True

        except Exception as e:
            logger.error(f"Configuration validation failed: {str(e)}")
            raise
