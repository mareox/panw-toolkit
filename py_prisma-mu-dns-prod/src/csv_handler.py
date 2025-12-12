"""
CSV handler for importing domain lists
"""

import csv
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


class CSVHandler:
    """Handle CSV operations for domain lists"""

    @staticmethod
    def load_domains(csv_path: str) -> List[str]:
        """
        Load domains from CSV file

        Args:
            csv_path: Path to CSV file containing domains

        Returns:
            List of domain strings

        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If CSV format is invalid
        """
        domains = []
        csv_file = Path(csv_path)

        if not csv_file.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        try:
            logger.info(f"Loading domains from {csv_path}")

            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)

                # Skip header if present
                headers = next(reader, None)
                if headers and headers[0].lower() in ['domain', 'domains', 'domain_name']:
                    logger.debug("Skipping header row")
                else:
                    # First row is data, not header
                    if headers and headers[0].strip():
                        domains.append(headers[0].strip())

                # Read remaining rows
                for row in reader:
                    if row and row[0].strip():
                        domain = row[0].strip()
                        domains.append(domain)

            # Remove duplicates while preserving order
            domains = list(dict.fromkeys(domains))

            logger.info(f"Loaded {len(domains)} unique domains from CSV")

            if not domains:
                raise ValueError("No domains found in CSV file")

            return domains

        except Exception as e:
            logger.error(f"Error loading CSV file: {str(e)}")
            raise

    @staticmethod
    def validate_domains(domains: List[str]) -> bool:
        """
        Validate domain list format

        Args:
            domains: List of domain strings

        Returns:
            True if all domains are valid

        Raises:
            ValueError: If any domain is invalid
        """
        if not domains:
            raise ValueError("Domain list is empty")

        invalid_domains = []

        for domain in domains:
            # Basic validation: check for valid characters and structure
            if not domain:
                invalid_domains.append("(empty string)")
                continue

            # Check for invalid characters (spaces, special chars except . - *)
            if any(char in domain for char in [' ', ',', ';', '|', '\t', '\n']):
                invalid_domains.append(domain)
                continue

            # Check basic domain format (allow wildcards)
            parts = domain.replace('*', 'wildcard').split('.')
            if len(parts) < 2:
                invalid_domains.append(domain)

        if invalid_domains:
            logger.error(f"Invalid domains found: {invalid_domains}")
            raise ValueError(f"Invalid domains: {', '.join(invalid_domains[:5])}")

        logger.info(f"All {len(domains)} domains validated successfully")
        return True
