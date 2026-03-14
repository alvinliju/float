from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Merchant(Base):
    __tablename__ = "merchants"
    id           = Column(Integer, primary_key=True)
    name         = Column(String)
    location     = Column(String)
    category     = Column(String)      # pharmacy, restaurant, retail, grocery, apparel
    monthly_gmv  = Column(Float)
    created_at   = Column(DateTime, default=datetime.utcnow)

    settlements  = relationship("Settlement", back_populates="merchant")
    tax_events   = relationship("TaxEvent",   back_populates="merchant")
    offers       = relationship("CreditOffer", back_populates="merchant")


class Settlement(Base):
    __tablename__ = "settlements"
    id          = Column(Integer, primary_key=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"))
    date        = Column(Date)
    amount      = Column(Float)
    created_at  = Column(DateTime, default=datetime.utcnow)

    merchant    = relationship("Merchant", back_populates="settlements")


class TaxEvent(Base):
    __tablename__ = "tax_events"
    id               = Column(Integer, primary_key=True)
    merchant_id      = Column(Integer, ForeignKey("merchants.id"))
    event_type       = Column(String)   # GST_QUARTERLY, TDS, ADVANCE_TAX
    due_date         = Column(Date)
    estimated_amount = Column(Float)
    status           = Column(String, default="PENDING")

    merchant         = relationship("Merchant", back_populates="tax_events")


class CreditOffer(Base):
    __tablename__ = "credit_offers"
    id                  = Column(Integer, primary_key=True)
    merchant_id         = Column(Integer, ForeignKey("merchants.id"))
    amount              = Column(Float)
    duration_days       = Column(Integer)
    annual_rate         = Column(Float, default=0.18)
    daily_repayment_pct = Column(Float, default=0.08)
    gap_detected        = Column(Float)
    status              = Column(String, default="PENDING_REVIEW")
    diagnosis           = Column(Text)
    agent_reasoning     = Column(Text)
    created_at          = Column(DateTime, default=datetime.utcnow)
    approved_at         = Column(DateTime, nullable=True)
    disbursed_at        = Column(DateTime, nullable=True)

    merchant            = relationship("Merchant", back_populates="offers")
