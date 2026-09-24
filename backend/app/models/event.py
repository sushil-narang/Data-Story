"""Event models for news ingestion and enrichment."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


class EventCategory(str, Enum):
    """High-level event categories for routing to data catalogs."""
    ECONOMY = "economy"
    LABOR = "labor"
    INFLATION = "inflation"
    TRADE = "trade"
    ENERGY = "energy"
    CLIMATE = "climate"
    TECHNOLOGY = "technology"
    HEALTH = "health"
    POLITICS = "politics"
    DEMOGRAPHICS = "demographics"
    FINANCE = "finance"
    HOUSING = "housing"
    TRANSPORT = "transport"
    EDUCATION = "education"
    CRIME = "crime"


class EventSeverity(str, Enum):
    """Perceived significance of the event."""
    BREAKING = "breaking"
    MAJOR = "major"
    MODERATE = "moderate"
    MINOR = "minor"


class RawEvent(BaseModel):
    """Raw event from news ingestion before enrichment."""
    id: str = Field(..., description="Unique identifier from source")
    source: str = Field(..., description="News source identifier")
    source_url: HttpUrl
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    published_at: datetime
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    language: str = "en"
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)


class Entity(BaseModel):
    """Extracted named entity from event text."""
    text: str
    label: str  # PERSON, ORG, GPE, DATE, MONEY, PERCENT, etc.
    start: int
    end: int
    confidence: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EventSignal(BaseModel):
    """Quantitative signal extracted from event text."""
    metric: str  # e.g., "unemployment_rate", "cpi_yoy", "fed_funds_rate"
    value: Optional[float] = None
    unit: Optional[str] = None
    direction: Optional[str] = None  # up, down, stable, record_high, record_low
    period: Optional[str] = None  # e.g., "2024-03", "Q1 2024"
    confidence: float = 0.0
    context: str = ""  # Surrounding text for verification


class EnrichedEvent(BaseModel):
    """Event after NLP enrichment and entity extraction."""
    raw: RawEvent
    category: EventCategory
    severity: EventSeverity
    entities: List[Entity] = Field(default_factory=list)
    signals: List[EventSignal] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    geographic_scope: List[str] = Field(default_factory=list)  # ISO country codes
    enriched_at: datetime = Field(default_factory=datetime.utcnow)
    confidence: float = 0.0


class EventCluster(BaseModel):
    """Group of related events for deduplication."""
    id: str
    events: List[EnrichedEvent] = Field(default_factory=list)
    primary_event: Optional[EnrichedEvent] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    story_generated: bool = False