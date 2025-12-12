"""
Authentication handler for Prisma SASE API
"""

import prisma_sase
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PrismaAuth:
    """Handle authentication to Prisma SASE"""

    def __init__(self, client_id: str, client_secret: str, tsg_id: str):
        """
        Initialize authentication handler

        Args:
            client_id: Service Account Client ID
            client_secret: Service Account Client Secret
            tsg_id: Tenant Service Group ID
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tsg_id = tsg_id
        self.sdk: Optional[prisma_sase.API] = None

    def authenticate(self) -> prisma_sase.API:
        """
        Authenticate and return SDK instance

        Returns:
            Authenticated Prisma SASE SDK instance

        Raises:
            Exception: If authentication fails
        """
        try:
            logger.info("Authenticating to Prisma SASE...")

            # Initialize SDK
            self.sdk = prisma_sase.API(controller="https://api.sase.paloaltonetworks.com")

            # Authenticate using service account
            # Note: login_secret() may return False if SD-WAN profile retrieval fails,
            # but OAuth2 authentication can still succeed for Prisma Access
            result = self.sdk.interactive.login_secret(
                client_id=self.client_id,
                client_secret=self.client_secret,
                tsg_id=self.tsg_id
            )

            # Check if we actually got an access token (even if result is False)
            # This handles Prisma Access deployments that don't have SD-WAN
            if hasattr(self.sdk, 'operator') and hasattr(self.sdk.operator, 'operator_id'):
                # We have a valid authenticated session
                logger.info("Successfully authenticated to Prisma SASE (Prisma Access)")
                return self.sdk
            elif result:
                # Standard success case
                logger.info("Successfully authenticated to Prisma SASE")
                return self.sdk
            else:
                # Check if we at least have an access token stored
                if hasattr(self.sdk, '_session') and self.sdk._session:
                    logger.warning("OAuth2 authentication succeeded but profile retrieval failed")
                    logger.warning("This is normal for Prisma Access-only deployments")
                    logger.info("Continuing with limited SDK functionality...")
                    return self.sdk
                else:
                    raise Exception("Authentication failed - no access token obtained")

        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise

    def logout(self):
        """Logout from Prisma SASE"""
        if self.sdk:
            try:
                self.sdk.get.logout()
                logger.info("Logged out from Prisma SASE")
            except Exception as e:
                logger.warning(f"Logout failed: {str(e)}")
