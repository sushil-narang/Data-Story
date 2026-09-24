"""Story models for data story generation and presentation."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, HttpUrl


class ChartType(str, Enum):
    """Supported chart types for data stories."""
    LINE = "line"
    BAR = "bar"
    AREA = "area"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    CHOROPLETH = "choropleth"
    COMBO = "combo"  # Line + bar


class ChartSpec(BaseModel):
    """Specification for a chart in a data story."""
    id: str
    type: ChartType
    title: str
    subtitle: Optional[str] = None
    # Data
    series_ids: List[str]  # References to DatasetSeries IDs
    x_field: str = "date"
    y_fields: List[str] = Field(default_factory=list)  # Value field names
    # Visual encoding
    color_scheme: str = "category10"
    show_legend: bool = True
    show_tooltip: bool = True
    # Annotations
    annotations: List[Dict[str, Any]] = Field(default_factory=list)
    # Sizing
    width: Optional[int] = None
    height: int = 350
    # Narrative link
    insight: str = ""  # Key takeaway this chart illustrates
    caption: Optional[str] = None


class NarrativeBlock(BaseModel):
    """A block of narrative text with optional data references."""
    type: Literal["lead", "context", "chart_ref", "analysis", "implication", "caveat"]
    content: str
    chart_id: Optional[str] = None  # If chart_ref, which chart
    data_refs: List[str] = Field(default_factory=list)  # Series IDs referenced
    order: int = 0


class DataStory(BaseModel):
    """Complete generated data story."""
    id: str
    event_id: str
    title: str
    dek: str  # One-sentence summary/deck
    category: str
    severity: str
    published_at: datetime
    charts: List[ChartSpec] = Field(default_factory=list)
    narrative: List[NarrativeBlock] = Field(default_factory=list)
    data_sources: List[Dict[str, str]] = Field(default_factory=list)  # [{name, url}]
    methodology: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    reading_time_minutes: int = 2
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = 1


class StoryFeedItem(BaseModel):
    """Lightweight story for feed/list views."""
    id: str
    title: str
    dek: str
    category: str
    severity: str
    published_at: datetime
    thumbnail_chart_id: Optional[str] = None
    reading_time_minutes: int
    tags: List[str] = Field(default_factory=list)


class StoryGenerationRequest(BaseModel):
    """Request to generate a story for an event."""
    event_id: str
    force_regenerate: bool = False
    max_charts: int = 2
    narrative_length: Literal["short", "medium", "long"] = "medium"


class StoryGenerationResponse(BaseModel):
    """Response from story generation."""
    story: Optional[DataStory] = None
    status: Literal["success", "pending", "failed", "no_data"]
    message: str = ""
    matched_datasets: List[str] = Field(default_factory=list)