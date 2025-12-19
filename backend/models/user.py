"""User model for Ariadne authentication and profile management."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, Index
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    """User model for authentication and profile data."""
    
    __tablename__ = "users"
    
    # Primary identity
    user_id = Column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
        comment="Unique user identifier"
    )
    
    # Authentication data
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="User email address (used for login)"
    )
    
    email_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether email has been verified"
    )
    
    # Profile data
    full_name = Column(
        String(255),
        nullable=True,
        comment="User's full name"
    )
    
    profile_picture_url = Column(
        Text,
        nullable=True,
        comment="URL to user's profile picture"
    )
    
    # Research preferences
    persona = Column(
        String(50),
        default="academic",
        nullable=False,
        comment="User's research persona (academic, analyst, engineer)"
    )
    
    # Subscription and access control
    subscription_tier = Column(
        String(50),
        default="explorer",
        nullable=False,
        comment="User's subscription tier (anonymous, explorer, researcher, team)"
    )
    
    subscription_status = Column(
        String(20),
        default="active",
        nullable=False,
        comment="Subscription status (active, inactive, cancelled, suspended)"
    )
    
    subscription_expires_at = Column(
        DateTime,
        nullable=True,
        comment="When subscription expires (for time-limited plans)"
    )
    
    # Usage tracking
    queries_used_today = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of queries used today"
    )
    
    last_query_at = Column(
        DateTime,
        nullable=True,
        comment="When user last performed a query"
    )
    
    total_queries = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Total number of queries performed"
    )
    
    # Knowledge graph tracking
    tapestries_created = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of Tapestries created"
    )
    
    last_activity_at = Column(
        DateTime,
        nullable=True,
        comment="Last user activity timestamp"
    )
    
    # Time tracking
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="When user account was created"
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="When user profile was last updated"
    )
    
    last_login_at = Column(
        DateTime,
        nullable=True,
        comment="When user last logged in"
    )
    
    # Data export and deletion
    data_export_requested_at = Column(
        DateTime,
        nullable=True,
        comment="When user requested data export"
    )
    
    deletion_requested_at = Column(
        DateTime,
        nullable=True,
        comment="When user requested account deletion"
    )
    
    deletion_scheduled_for = Column(
        DateTime,
        nullable=True,
        comment="When account deletion is scheduled (GDPR compliance)"
    )
    
    # Privacy and preferences
    analytics_consent = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="User consent for analytics tracking"
    )
    
    marketing_consent = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="User consent for marketing communications"
    )
    
    # Additional profile fields
    bio = Column(
        Text,
        nullable=True,
        comment="User's bio or description"
    )
    
    organization = Column(
        String(255),
        nullable=True,
        comment="User's organization or institution"
    )
    
    location = Column(
        String(255),
        nullable=True,
        comment="User's location"
    )
    
    website = Column(
        String(255),
        nullable=True,
        comment="User's personal or professional website"
    )
    
    # API access for team users
    api_key_hash = Column(
        String(255),
        nullable=True,
        comment="Hashed API key for programmatic access"
    )
    
    api_key_created_at = Column(
        DateTime,
        nullable=True,
        comment="When API key was created"
    )
    
    # Team management
    team_id = Column(
        PostgresUUID(as_uuid=True),
        nullable=True,
        comment="ID of team user belongs to"
    )
    
    team_role = Column(
        String(50),
        nullable=True,
        comment="User's role within their team (member, admin, owner)"
    )
    
    def __repr__(self) -> str:
        """String representation of the user."""
        return f"<User(email='{self.email}', tier='{self.subscription_tier}')>"
    
    @property
    def is_anonymous(self) -> bool:
        """Check if user is anonymous (no email verification)."""
        return not self.email_verified
    
    @property
    def is_active(self) -> bool:
        """Check if user account is active."""
        return self.subscription_status == "active"
    
    @property
    def is_premium(self) -> bool:
        """Check if user has premium access."""
        return self.subscription_tier in ["researcher", "team_member", "team_admin"]
    
    @property
    def is_team_admin(self) -> bool:
        """Check if user is a team administrator."""
        return self.team_role in ["admin", "owner"]
    
    @property
    def has_api_access(self) -> bool:
        """Check if user has API access."""
        return bool(self.api_key_hash)
    
    def can_perform_query(self) -> bool:
        """Check if user can perform another query."""
        # Check subscription status
        if not self.is_active:
            return False
        
        # Check if subscription expired
        if (self.subscription_expires_at and 
            self.subscription_expires_at < datetime.utcnow()):
            return False
        
        # Check daily query limits
        if self.subscription_tier == "anonymous":
            # Anonymous users have very limited queries
            return self.queries_used_today < 3
        elif self.subscription_tier == "explorer":
            return self.queries_used_today < 10
        elif self.subscription_tier == "researcher":
            return self.queries_used_today < 100
        elif self.subscription_tier in ["team_member", "team_admin"]:
            return self.queries_used_today < 200
        
        # Default to anonymous limits
        return self.queries_used_today < 3
    
    def increment_query_count(self):
        """Increment query usage count."""
        now = datetime.utcnow()
        
        # Reset daily count if it's a new day
        if (not self.last_query_at or 
            self.last_query_at.date() != now.date()):
            self.queries_used_today = 1
        else:
            self.queries_used_today += 1
        
        self.last_query_at = now
        self.total_queries += 1
        self.last_activity_at = now
    
    def can_export_data(self) -> bool:
        """Check if user can request data export."""
        # Can export if no export is currently pending
        # Export requests are valid for 30 days
        if self.data_export_requested_at:
            days_since_request = (
                datetime.utcnow() - self.data_export_requested_at
            ).days
            return days_since_request > 30
        return True
    
    def can_delete_account(self) -> bool:
        """Check if user can request account deletion."""
        # Can delete if no deletion is currently pending
        # Deletion is scheduled after 30-day grace period
        if self.deletion_requested_at:
            days_since_request = (
                datetime.utcnow() - self.deletion_requested_at
            ).days
            return days_since_request > 30
        return True
    
    def to_dict(self) -> dict:
        """Convert user to dictionary (excluding sensitive data)."""
        return {
            "user_id": str(self.user_id),
            "email": self.email,
            "email_verified": self.email_verified,
            "full_name": self.full_name,
            "persona": self.persona,
            "subscription_tier": self.subscription_tier,
            "subscription_status": self.subscription_status,
            "subscription_expires_at": (
                self.subscription_expires_at.isoformat() 
                if self.subscription_expires_at else None
            ),
            "tapestries_created": self.tapestries_created,
            "total_queries": self.total_queries,
            "has_api_access": self.has_api_access,
            "is_premium": self.is_premium,
            "is_team_admin": self.is_team_admin,
            "bio": self.bio,
            "organization": self.organization,
            "location": self.location,
            "website": self.website,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_login_at": (
                self.last_login_at.isoformat() 
                if self.last_login_at else None
            ),
        }


# Database indexes for performance
Index("idx_users_email", User.email)
Index("idx_users_subscription_tier", User.subscription_tier)
Index("idx_users_created_at", User.created_at)
Index("idx_users_last_activity", User.last_activity_at)
Index("idx_users_team_id", User.team_id)
Index("idx_users_api_key", User.api_key_hash)
