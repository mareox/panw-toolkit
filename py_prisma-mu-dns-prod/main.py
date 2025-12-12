#!/usr/bin/env python3
"""
Prisma Access Mobile Users DNS Configuration Updater

This script updates the Mobile Users Client DNS configuration by:
1. Adding an internal domain resolution rule named "CustomDNS" with domains from CSV
2. Changing public DNS settings to "Prisma Access Default"
"""

import argparse
import logging
import sys
import yaml
from pathlib import Path
from typing import Dict, Any

from src.auth import PrismaAuth
from src.csv_handler import CSVHandler
from src.dns_config import MobileUsersDNSConfig
from src.validator import ConfigValidator


# Configure logging
def setup_logging(log_level: str = "INFO", log_file: str = None):
    """Setup logging configuration"""

    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        handlers.append(logging.FileHandler(log_dir / log_file))

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers
    )


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # Validate configuration structure
        ConfigValidator.validate_config_structure(config)
        ConfigValidator.validate_credentials(config['api'])

        return config

    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error loading configuration: {str(e)}")
        sys.exit(1)


def main():
    """Main execution function"""

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Update Prisma Access Mobile Users DNS Configuration"
    )
    parser.add_argument(
        '-c', '--config',
        default='config/config.yaml',
        help='Path to configuration file (default: config/config.yaml)'
    )
    parser.add_argument(
        '-d', '--domains',
        default='config/domains.csv',
        help='Path to domains CSV file (default: config/domains.csv)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without applying them'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--log-file',
        help='Log file name (stored in logs/ directory)'
    )
    parser.add_argument(
        '--rule-name',
        default='CustomDNS',
        help='Name of the DNS resolution rule (default: CustomDNS)'
    )
    parser.add_argument(
        '--regions',
        help='Comma-separated list of regions to update (e.g., worldwide,emea,apac). If not specified, all regions will be updated.'
    )
    parser.add_argument(
        '--list-regions',
        action='store_true',
        help='List all available regions and exit'
    )

    args = parser.parse_args()

    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level, args.log_file)

    logger = logging.getLogger(__name__)

    try:
        logger.info("=" * 80)
        logger.info("Prisma Access Mobile Users DNS Configuration Updater")
        logger.info("=" * 80)

        if args.dry_run:
            logger.warning("DRY RUN MODE - No changes will be applied")

        # Load configuration
        logger.info("Loading configuration...")
        config = load_config(args.config)

        # Load domains from CSV
        logger.info("Loading domains from CSV...")
        csv_handler = CSVHandler()
        domains = csv_handler.load_domains(args.domains)

        # Validate domains
        logger.info("Validating domains...")
        csv_handler.validate_domains(domains)

        logger.info(f"Loaded {len(domains)} domains:")
        for i, domain in enumerate(domains[:5], 1):
            logger.info(f"  {i}. {domain}")
        if len(domains) > 5:
            logger.info(f"  ... and {len(domains) - 5} more")

        # Authenticate to Prisma SASE
        logger.info("Authenticating to Prisma SASE...")
        auth = PrismaAuth(
            client_id=config['api']['client_id'],
            client_secret=config['api']['client_secret'],
            tsg_id=config['api']['tsg_id']
        )
        sdk = auth.authenticate()

        # Initialize DNS configuration manager
        dns_manager = MobileUsersDNSConfig(sdk)

        # Get all regions
        logger.info("Retrieving configured regions...")
        regions = dns_manager.get_all_regions()
        logger.info(f"Found {len(regions)} regions")

        # List regions and exit if requested
        if args.list_regions:
            from src.dns_config import load_region_mappings, get_friendly_region_name

            region_mappings = load_region_mappings()

            logger.info("=" * 80)
            logger.info("Available regions:")
            logger.info("=" * 80)

            if region_mappings:
                logger.info("  (Showing: Friendly Name - Technical Name)")
                logger.info("")

            for i, region in enumerate(regions, 1):
                friendly_name = get_friendly_region_name(region, region_mappings)

                if friendly_name != region:
                    logger.info(f"  {i:2d}. {friendly_name} - {region}")
                else:
                    logger.info(f"  {i:2d}. {region}")

            logger.info("=" * 80)

            if not region_mappings:
                logger.info("\nTIP: Create config/region_mappings.yaml to display friendly region names")
                logger.info("See config/region_mappings.yaml.template for format")
                logger.info("")

            logger.info(f"To update specific regions, use: --regions {regions[0]},...")
            logger.info("You can use either technical names (ip-pool-group-X) or friendly names")
            auth.logout()
            sys.exit(0)

        # Filter regions if specified
        selected_regions = regions
        if args.regions:
            requested_regions = [r.strip() for r in args.regions.split(',')]
            selected_regions = [r for r in regions if r in requested_regions]

            if not selected_regions:
                logger.error(f"None of the requested regions found: {requested_regions}")
                logger.error(f"Available regions: {', '.join(regions)}")
                auth.logout()
                sys.exit(1)

            missing_regions = set(requested_regions) - set(selected_regions)
            if missing_regions:
                logger.warning(f"Requested regions not found: {', '.join(missing_regions)}")

            logger.info(f"Selected {len(selected_regions)} of {len(regions)} regions: {', '.join(selected_regions)}")
        else:
            logger.info("No --regions specified, will update ALL regions")

        # Update DNS configuration
        logger.info("Updating DNS configuration...")
        logger.info(f"  - Adding '{args.rule_name}' rule with {len(domains)} domains")
        logger.info(f"  - Setting Public DNS to 'Prisma Access Default'")

        result = dns_manager.update_dns_config(
            domains=domains,
            rule_name=args.rule_name,
            dry_run=args.dry_run,
            regions=selected_regions if args.regions else None
        )

        # Display results
        logger.info("=" * 80)
        if args.dry_run:
            logger.info("DRY RUN COMPLETED - Review changes above")
            logger.info("Run without --dry-run to apply changes")
        else:
            logger.info("DNS CONFIGURATION UPDATED SUCCESSFULLY")
            logger.info(f"  - Added/Updated rule: {args.rule_name}")
            logger.info(f"  - Configured {len(domains)} internal domains")
            logger.info(f"  - Updated Public DNS to Prisma Access Default")

        logger.info("=" * 80)

        # Logout
        auth.logout()

        sys.exit(0)

    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user")
        sys.exit(130)

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=args.verbose)
        sys.exit(1)


if __name__ == "__main__":
    main()
