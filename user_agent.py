"""
Dynamic User-Agent generator for Sportivity iOS app.
"""
import uuid
from typing import Optional
from datetime import datetime, timedelta

from config import Config

class iOSUserAgent:
    """Generate and maintain up-to-date Sportivity app User-Agent strings."""
    
    # Sentry trace ID for tracking (generates random one per session)
    _trace_id: Optional[str] = None
    _span_id: Optional[str] = None
    
    @classmethod
    def _get_trace_ids(cls) -> tuple[str, str]:
        """Generate Sentry trace IDs if not already set."""
        if not cls._trace_id:
            cls._trace_id = uuid.uuid4().hex
        if not cls._span_id:
            cls._span_id = uuid.uuid4().hex[:16]
        return cls._trace_id, cls._span_id
    
    @classmethod
    def get_darwin_version(cls) -> str:
        """
        Get Darwin version for iOS version.
        Darwin 24.6.0 = iOS 18.0
        """
        ios_version = Config.IOS_VERSION
        if ios_version.startswith('18.'):
            return '24.6.0'
        elif ios_version.startswith('17.'):
            return '23.5.0'
        else:
            return '24.6.0'  # Default to latest
    
    @classmethod
    def generate(cls) -> str:
        """
        Generate Sportivity app User-Agent string.
        Format: Sportivity/[build] CFNetwork/[version] Darwin/[version]
        
        Returns:
            Sportivity-specific User-Agent string
        """
        darwin_version = cls.get_darwin_version()
        cfnetwork_version = '3826.600.41'  # iOS 18.0 CFNetwork version
        
        user_agent = f"Sportivity/{Config.APP_VERSION} CFNetwork/{cfnetwork_version} Darwin/{darwin_version}"
        return user_agent
    
    @classmethod
    def get_headers(cls) -> dict:
        """
        Get a complete set of headers that mimic the Sportivity iOS app.
        
        Returns:
            Dictionary of HTTP headers matching the app
        """
        trace_id, span_id = cls._get_trace_ids()
        
        return {
            'Host': 'bossnl.mendixcloud.com',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'bundleidentifier': Config.BUNDLE_ID,
            'User-Agent': cls.generate(),
            'Accept-Language': 'nl-NL,nl;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            # Sentry tracking headers
            'sentry-trace': f'{trace_id}-{span_id}-0',
            'baggage': (
                f'sentry-environment=production,'
                f'sentry-public_key=90a27f781c0bb6fd105c35717764a55b,'
                f'sentry-release={Config.BUNDLE_ID}%402.0.43%2B{Config.APP_VERSION},'
                f'sentry-trace_id={trace_id}'
            ),
        }
