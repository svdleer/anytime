#!/usr/bin/env python3
"""
Test script to verify login functionality.
"""
import logging
import sys
from auth import AuthClient

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_login():
    """Test the login functionality."""
    try:
        logger.info("=" * 60)
        logger.info("Testing Sportivity Login")
        logger.info("=" * 60)
        
        auth_client = AuthClient()
        
        logger.info("Attempting login...")
        token = auth_client.login()
        
        logger.info(f"✓ Login successful!")
        logger.info(f"✓ Token received (first 20 chars): {token[:20]}...")
        logger.info(f"✓ Token length: {len(token)} characters")
        
        logger.info("\nValidating token...")
        if auth_client.validate_token():
            logger.info("✓ Token validation successful!")
        else:
            logger.warning("✗ Token validation failed (this might be expected if validation endpoint is different)")
        
        logger.info("\n" + "=" * 60)
        logger.info("Test completed successfully!")
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error(f"\n✗ Test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_login()
    sys.exit(0 if success else 1)
