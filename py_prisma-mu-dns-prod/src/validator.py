"""
Configuration validator
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ConfigValidator:
    """Validate configuration and inputs"""

    @staticmethod
    def validate_credentials(config: Dict[str, Any]) -> bool:
        """
        Validate API credentials

        Args:
            config: Configuration dictionary

        Returns:
            True if credentials are valid

        Raises:
            ValueError: If credentials are invalid or missing
        """
        required_fields = ['client_id', 'client_secret', 'tsg_id']

        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required credential: {field}")

            if not config[field] or not str(config[field]).strip():
                raise ValueError(f"Empty credential: {field}")

        logger.info("Credentials validation passed")
        return True

    @staticmethod
    def validate_config_structure(config: Dict[str, Any]) -> bool:
        """
        Validate configuration file structure

        Args:
            config: Configuration dictionary

        Returns:
            True if structure is valid

        Raises:
            ValueError: If structure is invalid
        """
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")

        if 'api' not in config:
            raise ValueError("Missing 'api' section in configuration")

        api_config = config['api']
        if not isinstance(api_config, dict):
            raise ValueError("'api' section must be a dictionary")

        logger.info("Configuration structure validation passed")
        return True
