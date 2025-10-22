"""
Secure WebSocket Authentication Service for Phase 3, Item 4
Following security-first blueprint and existing JWT patterns
"""
import logging
from typing import Optional, Dict, Any
from uuid import UUID
from fastapi import WebSocket, status
from jose import JWTError, jwt

from app.core.config import settings
from app.core.security import verify_token  # Reuse existing security

logger = logging.getLogger("safe_zone.websocket_auth")

class WebSocketAuthService:
    """
    WebSocket authentication service
    Maintains same security patterns as HTTP endpoints
    """
    
    async def authenticate_websocket(
        self, 
        websocket: WebSocket, 
        token: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate WebSocket connection using JWT token
        Follows same pattern as get_current_user dependency
        """
        if not token:
            await self._reject_connection(websocket, "No authentication token provided")
            return None

        try:
            # Use existing token verification from security.py
            payload = verify_token(token)
            if not payload:
                await self._reject_connection(websocket, "Invalid token")
                return None

            user_id = payload.get("sub")
            user_email = payload.get("email")
            
            if not user_id:
                await self._reject_connection(websocket, "Invalid token payload")
                return None

            logger.info(f"WebSocket authentication successful for user {user_id}")
            return {
                "user_id": UUID(user_id),
                "email": user_email,
                "payload": payload
            }

        except JWTError as e:
            await self._reject_connection(websocket, f"Token validation failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"WebSocket authentication error: {e}")
            await self._reject_connection(websocket, "Authentication error")
            return None

    async def _reject_connection(
        self, 
        websocket: WebSocket, 
        reason: str
    ):
        """Reject WebSocket connection with proper status code"""
        logger.warning(f"WebSocket connection rejected: {reason}")
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason=reason[:125]  # WebSocket reason max length
        )

# Global service instance
websocket_auth = WebSocketAuthService()
