#!/usr/bin/env python3
"""
Error Handling

This module defines custom exception classes for the application.
"""

from typing import Optional, Any, Dict


class BaseError(Exception):
    """Base exception class for the application."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)
    
    def __str__(self):
        return self.message


class APIError(BaseError):
    """Raised when there's an error with an external API call."""
    pass


class MessageHandlingError(BaseError):
    """Raised when there's an error handling an agent message."""
    pass


class ConfigurationError(BaseError):
    """Raised when there's an error with agent configuration."""
    pass


class BlockchainError(BaseError):
    """Raised when there's an error with blockchain operations."""
    pass


class CommunicationError(BaseError):
    """Exception raised for inter-agent communication errors."""
    pass


class DataValidationError(BaseError):
    """Exception raised for data validation errors."""
    pass


class SwapError(BaseError):
    """Exception raised for swap-related errors."""
    pass


class LLMError(BaseError):
    """Exception raised for LLM (AI) related errors."""
    pass


class AuthenticationError(BaseError):
    """Exception raised for authentication errors."""
    pass


def format_error(error: Exception) -> Dict[str, Any]:
    """
    Format an exception into a standardized error dictionary.
    
    Args:
        error: The exception to format
        
    Returns:
        Dict: Formatted error information
    """
    if isinstance(error, CryptoAgentError):
        result = {
            "error": error.__class__.__name__,
            "message": error.message,
            "details": error.details
        }
    else:
        result = {
            "error": error.__class__.__name__,
            "message": str(error),
            "details": {}
        }
    
    return result 