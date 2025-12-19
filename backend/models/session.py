"""Session model for managing user authentication sessions."""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, Index, JSON
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class UserSession(Base):
    """Session model for tracking user authentication sessions."""
    
    __tablename__ = "user_sessions"
    
    # Primary identity
    session_id = Column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
        comment="Unique session identifier"
    )
    
    # User relationship
    user_id = Column(
        PostgresUUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="User this session belongs to"
    )
    
    # Session data
    jwt_token_hash = Column(
        String(255),
        nullable=False,
        comment="Hash of the JWT token for security"
    )
    
    device_info = Column(
        JSON,
        nullable=True,
        comment="Device information (browser, OS, etc.)"
    )
    
    ip_address = Column(
        String(45),  # IPv6 compatible
        nullable=True,
        comment="User's IP address when session was created"
    )
    
    user_agent = Column(
        Text,
        nullable=True,
        comment="User agent string from the client"
    )
    
    # Session state
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether session is currently active"
    )
    
    is_anonymous = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether this is an anonymous session"
    )
    
    # Token refresh tracking
    refresh_token_hash = Column(
        String(255),
        nullable=True,
        comment="Hash of the refresh token"
    )
    
    last_refresh_at = Column(
        DateTime,
        nullable=True,
        comment="When session was last refreshed"
    )
    
    # Activity tracking
    last_activity_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="When session was last active"
    )
    
    activity_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of activities in this session"
    )
    
    # Session metadata
    location = Column(
        String(255),
        nullable=True,
        comment="User's location (country/region)"
    )
    
    mfa_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether multi-factor authentication was verified"
    )
    
    # Time tracking
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="When session was created"
    )
    
    expires_at = Column(
        DateTime,
        nullable=False,
        comment="When session expires"
    )
    
    last_seen_at = Column(
        DateTime,
        nullable=True,
        comment="When user was last seen"
    )
    
    terminated_at = Column(
        DateTime,
        nullable=True,
        comment="When session was terminated"
    )
    
    termination_reason = Column(
        String(100),
        nullable=True,
        comment="Reason for session termination (logout, timeout, etc.)"
    )
    
    def __repr__(self) -> str:
        """String representation of the session."""
        return f"<UserSession(user_id='{self.user_id}', active={self.is_active})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Check if session is still valid."""
        return (self.is_active and 
                not self.is_expired and 
                self.terminated_at is None)
    
    @property
    def age_hours(self) -> float:
        """Get session age in hours."""
        return (datetime.utcnow() - self.created_at).total_seconds() / 3600
    
    @property
    def time_until_expiry_hours(self) -> float:
        """Get time until expiry in hours."""
        if self.is_expired:
            return 0
        return (self.expires_at - datetime.utcnow()).total_seconds() / 3600
    
    def update_activity(self, increment_count: bool = True):
        """Update session activity tracking."""
        self.last_activity_at = datetime.utcnow()
        self.last_seen_at = datetime.utcnow()
        
        if increment_count:
            self.activity_count += 1
    
    def extend_session(self, additional_hours: int = 24):
        """Extend session expiry."""
        from datetime import timedelta
        self.expires_at = datetime.utcnow() + timedelta(hours=additional_hours)
    
    def terminate(self, reason: str = "user_logout"):
        """Terminate the session."""
        self.is_active = False
        self.terminated_at = datetime.utcnow()
        self.termination_reason = reason
    
    def refresh(self):
        """Refresh the session tokens."""
        self.last_refresh_at = datetime.utcnow()
        # Session would be extended here based on refresh token logic
        self.extend_session()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "session_id": str(self.session_id),
            "user_id": str(self.user_id),
            "device_info": self.device_info,
            "ip_address": self.ip_address,
            "is_active": self.is_active,
            "is_anonymous": self.is_anonymous,
            "mfa_verified": self.mfa_verified,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "last_activity_at": self.last_activity_at.isoformat(),
            "age_hours": round(self.age_hours, 2),
            "time_until_expiry_hours": round(self.time_until_expiry_hours, 2),
            "is_valid": self.is_valid,
            "activity_count": self.activity_count,
        }


# Database indexes for performance
Index("idx_sessions_user_id", UserSession.user_id)
Index("idx_sessions_jwt_hash", UserSession.jwt_token_hash)
Index("idx_sessions_refresh_hash", UserSession.refresh_token_hash)
Index("idx_sessions_active", UserSession.is_active)
Index("idx_sessions_expires_at", UserSession.expires_at)
Index("idx_sessions_created_at", UserSession.created_at)


class SessionActivity(Base):
    """Session activity log for tracking user actions."""
    
    __tablename__ = "session_activities"
    
    # Primary identity
    activity_id = Column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
        comment="Unique activity identifier"
    )
    
    # Relationships
    session_id = Column(
        PostgresUUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Session this activity belongs to"
    )
    
    user_id = Column(
        PostgresUUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="User who performed the activity"
    )
    
    # Activity details
    activity_type = Column(
        String(100),
        nullable=False,
        comment="Type of activity (query, export, etc.)"
    )
    
    activity_description = Column(
        Text,
        nullable=True,
        comment="Description of the activity"
    )
    
    endpoint = Column(
        String(255),
        nullable=True,
        comment="API endpoint accessed"
    )
    
    method = Column(
        String(10),
        nullable=True,
        comment="HTTP method used"
    )
    
    # Response data
    status_code = Column(
        Integer,
        nullable=True,
        comment="HTTP status code of the response"
    )
    
    response_time_ms = Column(
        Integer,
        nullable=True,
        comment="Response time in milliseconds"
    )
    
    # Context data
    request_data = Column(
        JSON,
        nullable=True,
        comment="Request data (sanitized)"
    )
    
    response_data = Column(
        JSON,
        nullable=True,
        comment="Response data (sanitized)"
    )
    
    # Location data
    ip_address = Column(
        String(45),
        nullable=True,
        comment="IP address when activity occurred"
    )
    
    user_agent = Column(
        Text,
        nullable=True,
        comment="User agent when activity occurred"
    )
    
    # Time tracking
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="When activity occurred"
    )
    
    def __repr__(self) -> str:
        """String representation of the session activity."""
        return f"<SessionActivity(type='{self.activity_type}', user_id='{self.user_id}')>"
    
    @property
    def is_successful(self) -> bool:
        """Check if the activity was successful."""
        return self.status_code and 200 <= self.status_code < 300
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert activity to dictionary."""
        return {
            "activity_id": str(self.activity_id),
            "session_id": str(self.session_id),
            "user_id": str(self.user_id),
            "activity_type": self.activity_type,
            "activity_description": self.activity_description,
            "endpoint": self.endpoint,
            "method": self.method,
            "status_code": self.status_code,
            "response_time_ms": self.response_time_ms,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat(),
            "is_successful": self.is_successful,
        }


# Database indexes for session activities
Index("idx_activities_session_id", SessionActivity.session_id)
Index("idx_activities_user_id", SessionActivity.user_id)
Index("idx_activities_type", SessionActivity.activity_type)
Index("idx_activities_created_at", SessionActivity.created_at)
Index("idx_activities_status", SessionActivity.status_code)
