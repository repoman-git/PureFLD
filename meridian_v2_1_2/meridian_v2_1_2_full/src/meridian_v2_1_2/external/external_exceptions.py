"""
Exception classes for external API integration.
"""


class ExternalDataException(Exception):
    """Base exception for external data errors"""
    pass


class APIKeyException(ExternalDataException):
    """API key validation failed"""
    pass


class RateLimitException(ExternalDataException):
    """Rate limit exceeded"""
    pass


class ConnectionException(ExternalDataException):
    """Connection to external API failed"""
    pass


class DataNormalizationException(ExternalDataException):
    """Failed to normalize external data"""
    pass


class OrderRejectionException(ExternalDataException):
    """Order rejected by safety checks or broker"""
    pass


