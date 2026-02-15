"""
Authentication module for client ID/secret activation
"""

import os
import json
import hashlib
import secrets
import time
from typing import Dict, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ClientCredentials:
    """Client credentials data class"""
    client_id: str
    client_secret: str
    name: Optional[str] = None
    created_at: Optional[float] = None
    expires_at: Optional[float] = None
    is_active: bool = True


class AuthManager:
    """Manage client authentication and page activation"""
    
    def __init__(self, credentials_file: str = ".credentials.json"):
        """Initialize authentication manager
        
        Args:
            credentials_file: Path to credentials storage file
        """
        self.credentials_file = credentials_file
        self._credentials: Dict[str, ClientCredentials] = {}
        self._active_sessions: Dict[str, dict] = {}
        self._load_credentials()
        
    def _load_credentials(self):
        """Load credentials from file"""
        if os.path.exists(self.credentials_file):
            try:
                with open(self.credentials_file, 'r') as f:
                    data = json.load(f)
                    for client_id, cred_data in data.get('credentials', {}).items():
                        self._credentials[client_id] = ClientCredentials(
                            client_id=cred_data['client_id'],
                            client_secret=cred_data['client_secret'],
                            name=cred_data.get('name'),
                            created_at=cred_data.get('created_at'),
                            expires_at=cred_data.get('expires_at'),
                            is_active=cred_data.get('is_active', True)
                        )
                logger.info(f"Loaded {len(self._credentials)} credentials")
            except Exception as e:
                logger.error(f"Failed to load credentials: {e}")
    
    def _save_credentials(self):
        """Save credentials to file"""
        try:
            data = {
                'credentials': {
                    cred.client_id: {
                        'client_id': cred.client_id,
                        'client_secret': cred.client_secret,
                        'name': cred.name,
                        'created_at': cred.created_at,
                        'expires_at': cred.expires_at,
                        'is_active': cred.is_active
                    }
                    for cred in self._credentials.values()
                }
            }
            with open(self.credentials_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("Credentials saved successfully")
        except Exception as e:
            logger.error(f"Failed to save credentials: {e}")
    
    def generate_credentials(self, name: str = None, expires_in_days: int = None) -> Tuple[str, str]:
        """Generate new client credentials
        
        Args:
            name: Optional name for the client
            expires_in_days: Optional expiration in days
            
        Returns:
            Tuple of (client_id, client_secret)
        """
        # Generate secure random credentials
        client_id = secrets.token_urlsafe(16)
        client_secret = secrets.token_urlsafe(32)
        
        # Hash the secret for storage
        secret_hash = self._hash_secret(client_secret)
        
        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = time.time() + (expires_in_days * 24 * 60 * 60)
        
        # Store credentials
        self._credentials[client_id] = ClientCredentials(
            client_id=client_id,
            client_secret=secret_hash,
            name=name,
            created_at=time.time(),
            expires_at=expires_at,
            is_active=True
        )
        
        self._save_credentials()
        logger.info(f"Generated new credentials for: {name or 'unnamed'}")
        
        return client_id, client_secret
    
    def _hash_secret(self, secret: str) -> str:
        """Hash a secret for secure storage"""
        return hashlib.sha256(secret.encode()).hexdigest()
    
    def validate_credentials(self, client_id: str, client_secret: str) -> Tuple[bool, Optional[str]]:
        """Validate client credentials
        
        Args:
            client_id: The client ID
            client_secret: The client secret
            
        Returns:
            Tuple of (is_valid, session_token or error_message)
        """
        # Check if client exists
        if client_id not in self._credentials:
            logger.warning(f"Invalid client ID: {client_id[:8]}...")
            return False, "Invalid client ID"
        
        cred = self._credentials[client_id]
        
        # Check if active
        if not cred.is_active:
            logger.warning(f"Inactive client: {client_id[:8]}...")
            return False, "Client is not active"
        
        # Check expiration
        if cred.expires_at and time.time() > cred.expires_at:
            logger.warning(f"Expired client: {client_id[:8]}...")
            return False, "Credentials have expired"
        
        # Validate secret
        secret_hash = self._hash_secret(client_secret)
        if cred.client_secret != secret_hash:
            logger.warning(f"Invalid secret for client: {client_id[:8]}...")
            return False, "Invalid client secret"
        
        # Generate session token
        session_token = secrets.token_urlsafe(32)
        self._active_sessions[session_token] = {
            'client_id': client_id,
            'created_at': time.time(),
            'expires_at': time.time() + (24 * 60 * 60)  # 24 hour session
        }
        
        logger.info(f"Successful authentication for client: {client_id[:8]}...")
        return True, session_token
    
    def validate_session(self, session_token: str) -> bool:
        """Validate an active session
        
        Args:
            session_token: The session token to validate
            
        Returns:
            True if session is valid
        """
        if session_token not in self._active_sessions:
            return False
        
        session = self._active_sessions[session_token]
        
        # Check session expiration
        if time.time() > session['expires_at']:
            del self._active_sessions[session_token]
            return False
        
        return True
    
    def revoke_session(self, session_token: str):
        """Revoke a session
        
        Args:
            session_token: The session token to revoke
        """
        if session_token in self._active_sessions:
            del self._active_sessions[session_token]
            logger.info("Session revoked")
    
    def deactivate_client(self, client_id: str):
        """Deactivate a client
        
        Args:
            client_id: The client ID to deactivate
        """
        if client_id in self._credentials:
            self._credentials[client_id].is_active = False
            self._save_credentials()
            logger.info(f"Client deactivated: {client_id[:8]}...")
    
    def activate_client(self, client_id: str):
        """Activate a client
        
        Args:
            client_id: The client ID to activate
        """
        if client_id in self._credentials:
            self._credentials[client_id].is_active = True
            self._save_credentials()
            logger.info(f"Client activated: {client_id[:8]}...")
    
    def delete_client(self, client_id: str):
        """Delete a client
        
        Args:
            client_id: The client ID to delete
        """
        if client_id in self._credentials:
            del self._credentials[client_id]
            self._save_credentials()
            logger.info(f"Client deleted: {client_id[:8]}...")
    
    def list_clients(self) -> list:
        """List all registered clients
        
        Returns:
            List of client info dictionaries
        """
        return [
            {
                'client_id': cred.client_id[:8] + '...',
                'name': cred.name,
                'created_at': cred.created_at,
                'expires_at': cred.expires_at,
                'is_active': cred.is_active
            }
            for cred in self._credentials.values()
        ]


# Singleton instance
_auth_manager: Optional[AuthManager] = None


def get_auth_manager(credentials_file: str = ".credentials.json") -> AuthManager:
    """Get the authentication manager singleton
    
    Args:
        credentials_file: Path to credentials file
        
    Returns:
        AuthManager instance
    """
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager(credentials_file)
    return _auth_manager


def authenticate(client_id: str, client_secret: str) -> Tuple[bool, Optional[str]]:
    """Convenience function to authenticate
    
    Args:
        client_id: Client ID
        client_secret: Client secret
        
    Returns:
        Tuple of (is_valid, session_token or error_message)
    """
    return get_auth_manager().validate_credentials(client_id, client_secret)


def is_authenticated(session_token: str) -> bool:
    """Check if a session is authenticated
    
    Args:
        session_token: Session token to check
        
    Returns:
        True if authenticated
    """
    return get_auth_manager().validate_session(session_token)


__all__ = ['AuthManager', 'ClientCredentials', 'get_auth_manager', 'authenticate', 'is_authenticated']
