"""Dataset models for the curated data catalog."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, HttpUrl


class DataSource(str, Enum):
    """Supported data providers."""
    FRED = "fred"                    # Federal Reserve Economic Data
    WORLD_BANK = "world_bank"        # World Bank Open Data
    IMF = "imf"                      # International Monetary Fund
    OECD = "oecd"                    # OECD Statistics
    BLS = "bls"                      # Bureau of Labor Statistics
    BEA = "bea"                      # Bureau of Economic Analysis
    CENSUS = "census"                # US Census Bureau
    EUROSTAT = "eurostat"            # Eurostat
    UN = "un"                        # UN Data
    WHO = "who"                      # World Health Organization
    IEA = "iea"                      # International Energy Agency
    CUSTOM = "custom"                # Custom/local datasets


class Frequency(str, Enum):
    """Data frequency."""
    DAILY = "D"
    WEEKLY = "W"
    MONTHLY = "M"
    QUARTERLY = "Q"
    ANNUAL = "A"
    IRREGULAR = "irregular"


class GeographyType(str, Enum):
    """Geographic granularity."""
    COUNTRY = "country"
    STATE = "state"
    COUNTY = "county"
    CITY = "city"
    REGION = "region"
    GLOBAL = "global"


class DatasetSeries(BaseModel):
    """A single time series within a dataset."""
    id: str
    name: str
    description: Optional[str] = None
    unit: str
    frequency: Frequency
    geography_type: GeographyType
    geography_codes: List[str] = Field(default_factory=list)  # ISO codes, FIPS, etc.
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Dataset(BaseModel):
    """A curated dataset in the catalog."""
    id: str
    source: DataSource
    source_id: str  # Provider's internal ID (e.g., FRED series ID)
    name: str
    description: str
    category: str  # Maps to EventCategory
    subcategory: Optional[str] = None
    series: List[DatasetSeries] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    url: Optional[HttpUrl] = None
    license: Optional[str] = None
    citation: Optional[str] = None
    is_active: bool = True
    priority: int = 0  # Higher = preferred for matching
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Runtime fields (populated at query time)
    latest_value: Optional[float] = None
    latest_date: Optional[datetime] = None
    trend: Optional[str] = None  # rising, falling, stable, volatile


class DataCatalog(BaseModel):
    """Collection of all available datasets."""
    datasets: List[Dataset] = Field(default_factory=list)
    version: str = "1.0.0"
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def get_by_category(self, category: str) -> List[Dataset]:
        return [d for d in self.datasets if d.category == category]
    
    def get_by_tag(self, tag: str) -> List[Dataset]:
        return [d for d in self.datasets if tag in d.tags]
    
    def search(self, query: str, limit: int = 10) -> List[Dataset]:
        """Simple text search across name, description, tags."""
        query = query.lower()
        scored = []
        for d in self.datasets:
            score = 0
            if query in d.name.lower():
                score += 10
            if query in d.description.lower():
                score += 5
            for tag in d.tags:
                if query in tag.lower():
                    score += 3
            if score > 0:
                scored.append((score, d))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [d for _, d in scored[:limit]]


class DataPoint(BaseModel):
    """A single data observation."""
    series_id: str
    date: datetime
    value: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SeriesData(BaseModel):
    """Time series data for a dataset series."""
    series_id: str
    series_name: str
    unit: str
    frequency: Frequency
    data: List[DataPoint] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)