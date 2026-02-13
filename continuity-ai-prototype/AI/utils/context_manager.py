"""Context and session management."""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ContextManager:
    """Manages user sessions and conversation context."""

    def __init__(self, max_history: int = 10, timeout_minutes: int = 30):
        """
        Initialize context manager.

        Args:
            max_history: Maximum messages to keep in history
            timeout_minutes: Session timeout in minutes
        """
        self.max_history = max_history
        self.timeout_minutes = timeout_minutes
        self.sessions: Dict[str, Dict] = {}
        logger.info(f"ContextManager initialized with max_history={max_history}")

    def create_session(self, user_id: str) -> Dict:
        """
        Create a new session for a user.

        Args:
            user_id: Unique user identifier

        Returns:
            Session dict
        """
        session = {
            "user_id": user_id,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "messages": [],
            "metadata": {},
        }
        self.sessions[user_id] = session
        logger.info(f"Created session for user: {user_id}")
        return session

    def get_session(self, user_id: str) -> Optional[Dict]:
        """Get existing session or create new one."""
        if user_id not in self.sessions:
            return self.create_session(user_id)

        session = self.sessions[user_id]

        # Check if session has timed out
        if self._is_session_expired(session):
            logger.info(f"Session expired for user: {user_id}, creating new")
            return self.create_session(user_id)

        # Update activity time
        session["last_activity"] = datetime.now()
        return session

    def add_message(self, user_id: str, role: str, content: str) -> None:
        """
        Add a message to user's conversation history.

        Args:
            user_id: User identifier
            role: Message role ('user' or 'assistant')
            content: Message content
        """
        session = self.get_session(user_id)
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(),
        }
        session["messages"].append(message)

        # Keep only recent messages
        if len(session["messages"]) > self.max_history:
            session["messages"] = session["messages"][-self.max_history :]

        logger.debug(f"Added {role} message for user: {user_id}")

    def get_history(self, user_id: str, max_messages: int = None) -> List[Dict]:
        """
        Get conversation history for a user.

        Args:
            user_id: User identifier
            max_messages: Maximum messages to return (default: max_history)

        Returns:
            List of message dicts
        """
        session = self.get_session(user_id)
        max_messages = max_messages or self.max_history

        history = [
            {
                "role": msg["role"],
                "content": msg["content"],
            }
            for msg in session["messages"][-max_messages:]
        ]
        return history

    def clear_history(self, user_id: str) -> None:
        """Clear conversation history for a user."""
        if user_id in self.sessions:
            self.sessions[user_id]["messages"] = []
            logger.info(f"Cleared history for user: {user_id}")

    def delete_session(self, user_id: str) -> None:
        """Delete a user session."""
        if user_id in self.sessions:
            del self.sessions[user_id]
            logger.info(f"Deleted session for user: {user_id}")

    def cleanup_expired_sessions(self) -> int:
        """
        Remove expired sessions.

        Returns:
            Number of sessions removed
        """
        expired_users = [
            uid for uid, session in self.sessions.items()
            if self._is_session_expired(session)
        ]

        for user_id in expired_users:
            self.delete_session(user_id)

        if expired_users:
            logger.info(f"Cleaned up {len(expired_users)} expired sessions")
        return len(expired_users)

    def _is_session_expired(self, session: Dict) -> bool:
        """Check if a session has expired."""
        timeout = timedelta(minutes=self.timeout_minutes)
        return datetime.now() - session["last_activity"] > timeout

    def get_session_info(self, user_id: str) -> Optional[Dict]:
        """Get session metadata."""
        if user_id in self.sessions:
            session = self.sessions[user_id]
            return {
                "user_id": user_id,
                "messages_count": len(session["messages"]),
                "created_at": session["created_at"],
                "last_activity": session["last_activity"],
            }
        return None
