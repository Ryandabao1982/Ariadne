"""Subscription model for managing user subscriptions and billing."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, Index, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class SubscriptionPlan(Base):
    """Subscription plan configuration."""
    
    __tablename__ = "subscription_plans"
    
    # Primary identity
    plan_id = Column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
        comment="Unique plan identifier"
    )
    
    # Plan details
    plan_name = Column(
        String(100),
        unique=True,
        nullable=False,
        comment="Plan name (explorer, researcher, team)"
    )
    
    display_name = Column(
        String(100),
        nullable=False,
        comment="Human-readable plan name"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Plan description"
    )
    
    # Pricing
    price_monthly = Column(
        DECIMAL(10, 2),
        nullable=False,
        comment="Monthly price in USD"
    )
    
    price_yearly = Column(
        DECIMAL(10, 2),
        nullable=False,
        comment="Yearly price in USD"
    )
    
    # Features and limits
    queries_per_month = Column(
        Integer,
        nullable=False,
        comment="Monthly query limit"
    )
    
    queries_per_day = Column(
        Integer,
        nullable=False,
        comment="Daily query limit"
    )
    
    storage_gb = Column(
        Integer,
        nullable=False,
        comment="Storage limit in GB"
    )
    
    team_members_limit = Column(
        Integer,
        nullable=True,
        comment="Team member limit (None for unlimited)"
    )
    
    api_access = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether plan includes API access"
    )
    
    priority_support = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether plan includes priority support"
    )
    
    advanced_features = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether plan includes advanced features"
    )
    
    # Plan status
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether plan is currently available"
    )
    
    is_public = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether plan is shown to users"
    )
    
    # Time tracking
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="When plan was created"
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="When plan was last updated"
    )
    
    # Relationships
    subscriptions = relationship("UserSubscription", back_populates="plan")
    
    def __repr__(self) -> str:
        """String representation of the subscription plan."""
        return f"<SubscriptionPlan(name='{self.plan_name}', price=${self.price_monthly}/month)>"
    
    @property
    def is_free(self) -> bool:
        """Check if this is a free plan."""
        return self.price_monthly == 0
    
    @property
    def annual_savings(self) -> float:
        """Calculate savings for annual vs monthly billing."""
        monthly_total = self.price_monthly * 12
        savings = monthly_total - self.price_yearly
        return float(savings)
    
    @property
    def annual_discount_percentage(self) -> float:
        """Calculate percentage discount for annual billing."""
        if self.price_monthly == 0:
            return 0
        monthly_total = self.price_monthly * 12
        savings = self.annual_savings
        return (savings / monthly_total) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to dictionary."""
        return {
            "plan_id": str(self.plan_id),
            "plan_name": self.plan_name,
            "display_name": self.display_name,
            "description": self.description,
            "price_monthly": float(self.price_monthly),
            "price_yearly": float(self.price_yearly),
            "queries_per_month": self.queries_per_month,
            "queries_per_day": self.queries_per_day,
            "storage_gb": self.storage_gb,
            "team_members_limit": self.team_members_limit,
            "api_access": self.api_access,
            "priority_support": self.priority_support,
            "advanced_features": self.advanced_features,
            "is_free": self.is_free,
            "annual_savings": self.annual_savings,
            "annual_discount_percentage": round(self.annual_discount_percentage, 1),
        }


class UserSubscription(Base):
    """User subscription tracking."""
    
    __tablename__ = "user_subscriptions"
    
    # Primary identity
    subscription_id = Column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
        comment="Unique subscription identifier"
    )
    
    # Relationships
    user_id = Column(
        PostgresUUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="User this subscription belongs to"
    )
    
    plan_id = Column(
        PostgresUUID(as_uuid=True),
        ForeignKey("subscription_plans.plan_id"),
        nullable=False,
        index=True,
        comment="Plan this subscription is based on"
    )
    
    # Subscription details
    status = Column(
        String(20),
        default="active",
        nullable=False,
        comment="Subscription status (active, cancelled, expired, suspended)"
    )
    
    billing_cycle = Column(
        String(10),
        default="monthly",
        nullable=False,
        comment="Billing cycle (monthly, yearly)"
    )
    
    # Pricing
    amount = Column(
        DECIMAL(10, 2),
        nullable=False,
        comment="Subscription amount"
    )
    
    currency = Column(
        String(3),
        default="USD",
        nullable=False,
        comment="Currency code (USD, EUR, etc.)"
    )
    
    # Usage tracking
    queries_used_current_period = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Queries used in current billing period"
    )
    
    storage_used_mb = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Storage used in MB"
    )
    
    team_members_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of team members"
    )
    
    # Period tracking
    current_period_start = Column(
        DateTime,
        nullable=False,
        comment="Start of current billing period"
    )
    
    current_period_end = Column(
        DateTime,
        nullable=False,
        comment="End of current billing period"
    )
    
    # Billing dates
    next_billing_date = Column(
        DateTime,
        nullable=True,
        comment="Next billing date"
    )
    
    trial_end = Column(
        DateTime,
        nullable=True,
        comment="Trial period end date"
    )
    
    # Cancellation tracking
    cancelled_at = Column(
        DateTime,
        nullable=True,
        comment="When subscription was cancelled"
    )
    
    cancellation_reason = Column(
        String(255),
        nullable=True,
        comment="Reason for cancellation"
    )
    
    cancel_at_period_end = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether to cancel at end of current period"
    )
    
    # External billing
    external_subscription_id = Column(
        String(255),
        nullable=True,
        comment="External billing system subscription ID"
    )
    
    external_customer_id = Column(
        String(255),
        nullable=True,
        comment="External billing system customer ID"
    )
    
    # Time tracking
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="When subscription was created"
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="When subscription was last updated"
    )
    
    # Relationships
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    usage_logs = relationship("SubscriptionUsageLog", back_populates="subscription")
    invoices = relationship("SubscriptionInvoice", back_populates="subscription")
    
    def __repr__(self) -> str:
        """String representation of the subscription."""
        return f"<UserSubscription(user_id='{self.user_id}', plan='{self.plan.plan_name}', status='{self.status}')>"
    
    @property
    def is_active(self) -> bool:
        """Check if subscription is active."""
        return self.status == "active"
    
    @property
    def is_trial(self) -> bool:
        """Check if subscription is in trial period."""
        return (self.trial_end and 
                datetime.utcnow() < self.trial_end and 
                not self.cancelled_at)
    
    @property
    def is_expired(self) -> bool:
        """Check if subscription has expired."""
        return datetime.utcnow() > self.current_period_end
    
    @property
    def days_until_expiry(self) -> int:
        """Get days until subscription expires."""
        if self.is_expired:
            return 0
        return (self.current_period_end - datetime.utcnow()).days
    
    @property
    def days_until_billing(self) -> int:
        """Get days until next billing."""
        if not self.next_billing_date:
            return 0
        return (self.next_billing_date - datetime.utcnow()).days
    
    @property
    def usage_percentage(self) -> float:
        """Get percentage of monthly usage used."""
        if self.plan.queries_per_month == 0:
            return 0
        return (self.queries_used_current_period / self.plan.queries_per_month) * 100
    
    @property
    def storage_percentage(self) -> float:
        """Get percentage of storage used."""
        storage_gb_mb = self.plan.storage_gb * 1024  # Convert GB to MB
        if storage_gb_mb == 0:
            return 0
        return (self.storage_used_mb / storage_gb_mb) * 100
    
    def can_perform_query(self) -> bool:
        """Check if user can perform another query."""
        # Check if subscription is active
        if not self.is_active:
            return False
        
        # Check if in trial
        if self.is_trial:
            return True
        
        # Check query limits
        if self.queries_used_current_period >= self.plan.queries_per_month:
            return False
        
        return True
    
    def increment_usage(self, queries: int = 1):
        """Increment usage counters."""
        self.queries_used_current_period += queries
    
    def reset_usage_counters(self):
        """Reset usage counters for new billing period."""
        self.queries_used_current_period = 0
        self.storage_used_mb = 0
        self.current_period_start = datetime.utcnow()
        
        # Calculate new period end based on billing cycle
        if self.billing_cycle == "monthly":
            self.current_period_end = self.current_period_start + timedelta(days=30)
        else:  # yearly
            self.current_period_end = self.current_period_start + timedelta(days=365)
        
        # Update next billing date
        self.next_billing_date = self.current_period_end
    
    def cancel(self, reason: str = "", at_period_end: bool = True):
        """Cancel the subscription."""
        self.cancelled_at = datetime.utcnow()
        self.cancellation_reason = reason
        self.cancel_at_period_end = at_period_end
        
        if at_period_end:
            self.status = "active"  # Will become cancelled after period ends
        else:
            self.status = "cancelled"
    
    def activate(self):
        """Activate the subscription."""
        self.status = "active"
        self.cancelled_at = None
        self.cancellation_reason = None
        self.cancel_at_period_end = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert subscription to dictionary."""
        return {
            "subscription_id": str(self.subscription_id),
            "user_id": str(self.user_id),
            "plan": self.plan.to_dict() if self.plan else None,
            "status": self.status,
            "billing_cycle": self.billing_cycle,
            "amount": float(self.amount),
            "currency": self.currency,
            "queries_used_current_period": self.queries_used_current_period,
            "storage_used_mb": self.storage_used_mb,
            "team_members_count": self.team_members_count,
            "current_period_start": self.current_period_start.isoformat(),
            "current_period_end": self.current_period_end.isoformat(),
            "next_billing_date": (
                self.next_billing_date.isoformat() 
                if self.next_billing_date else None
            ),
            "trial_end": (
                self.trial_end.isoformat() 
                if self.trial_end else None
            ),
            "is_active": self.is_active,
            "is_trial": self.is_trial,
            "is_expired": self.is_expired,
            "days_until_expiry": self.days_until_expiry,
            "days_until_billing": self.days_until_billing,
            "usage_percentage": round(self.usage_percentage, 1),
            "storage_percentage": round(self.storage_percentage, 1),
        }


class SubscriptionUsageLog(Base):
    """Daily usage tracking for subscriptions."""
    
    __tablename__ = "subscription_usage_logs"
    
    # Primary identity
    log_id = Column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
        comment="Unique log identifier"
    )
    
    # Relationships
    subscription_id = Column(
        PostgresUUID(as_uuid=True),
        ForeignKey("user_subscriptions.subscription_id"),
        nullable=False,
        index=True,
        comment="Subscription this log belongs to"
    )
    
    # Date tracking
    log_date = Column(
        DateTime,
        nullable=False,
        comment="Date for this usage log"
    )
    
    # Usage data
    queries_used = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Queries used on this date"
    )
    
    storage_used_mb = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Storage used on this date (MB)"
    )
    
    api_calls = Column(
        Integer,
        default=0,
        nullable=False,
        comment="API calls made on this date"
    )
    
    exports_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Exports performed on this date"
    )
    
    # Time tracking
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="When log was created"
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="When log was last updated"
    )
    
    # Relationships
    subscription = relationship("UserSubscription", back_populates="usage_logs")
    
    def __repr__(self) -> str:
        """String representation of the usage log."""
        return f"<SubscriptionUsageLog(date='{self.log_date.date()}', queries={self.queries_used})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert usage log to dictionary."""
        return {
            "log_id": str(self.log_id),
            "subscription_id": str(self.subscription_id),
            "log_date": self.log_date.date().isoformat(),
            "queries_used": self.queries_used,
            "storage_used_mb": self.storage_used_mb,
            "api_calls": self.api_calls,
            "exports_count": self.exports_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class SubscriptionInvoice(Base):
    """Invoice tracking for subscriptions."""
    
    __tablename__ = "subscription_invoices"
    
    # Primary identity
    invoice_id = Column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
        comment="Unique invoice identifier"
    )
    
    # Relationships
    subscription_id = Column(
        PostgresUUID(as_uuid=True),
        ForeignKey("user_subscriptions.subscription_id"),
        nullable=False,
        index=True,
        comment="Subscription this invoice belongs to"
    )
    
    # Invoice details
    invoice_number = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="Human-readable invoice number"
    )
    
    status = Column(
        String(20),
        default="draft",
        nullable=False,
        comment="Invoice status (draft, sent, paid, failed, refunded)"
    )
    
    amount_due = Column(
        DECIMAL(10, 2),
        nullable=False,
        comment="Amount due"
    )
    
    amount_paid = Column(
        DECIMAL(10, 2),
        default=0,
        nullable=False,
        comment="Amount paid"
    )
    
    currency = Column(
        String(3),
        default="USD",
        nullable=False,
        comment="Currency code"
    )
    
    # Billing period
    period_start = Column(
        DateTime,
        nullable=False,
        comment="Start of billing period"
    )
    
    period_end = Column(
        DateTime,
        nullable=False,
        comment="End of billing period"
    )
    
    # Due dates
    due_date = Column(
        DateTime,
        nullable=False,
        comment="Payment due date"
    )
    
    paid_at = Column(
        DateTime,
        nullable=True,
        comment="When invoice was paid"
    )
    
    # External references
    external_invoice_id = Column(
        String(255),
        nullable=True,
        comment="External billing system invoice ID"
    )
    
    external_payment_intent_id = Column(
        String(255),
        nullable=True,
        comment="External payment intent ID"
    )
    
    # Line items
    line_items = Column(
        Text,
        nullable=True,
        comment="JSON string of line items"
    )
    
    # Time
