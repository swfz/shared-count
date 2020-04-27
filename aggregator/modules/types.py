from typing_extensions import TypedDict
from typing import Optional, List, Union

class Pocket(TypedDict):
    url: str
    count: str

class Engagement(TypedDict):
    count: int
    social_sentence: str


class OgObject(TypedDict):
    engagement: Engagement
    id: str


class Facebook(TypedDict):
    og_object: Optional[OgObject]
    id: str


class Bookmark(TypedDict):
    comment: str
    user: str
    tags: List[str]
    timestamp: str


class Hatena(TypedDict):
    eid: str
    count: str
    screenshot: str
    url: str
    title: str
    entry_url: str
    bookmarks: List[Bookmark]
    requested_url: str


class Star(TypedDict):
    name: str
    quote: str


class Entry(TypedDict):
    uri: str
    can_comment: int
    stars: List[Star]
    colored_stars: List[Star]


class HatenaStar(TypedDict):
    can_comment: int
    entries: List[Entry]


class Twitter(TypedDict):
    url: str
    count: int
    likes: int


class MetricHeaderEntry(TypedDict):
    name: str
    type: str


class MetricHeader(TypedDict):
    metricHeaderEntries: List[MetricHeaderEntry]


class ColumnHeader(TypedDict):
    dimensions: List[str]
    metricHeader: MetricHeader


class Metric(TypedDict):
    values: List[str]


class Row(TypedDict):
    dimensions: List[str]
    metrics: List[Metric]


class Data(TypedDict):
    rows: List[Row]
    totals: List[Metric]
    rowCount: int
    minimums: List[Metric]
    maximums: List[Metric]


class Report(TypedDict):
    columnHeader: ColumnHeader
    data: Data


class AnalyticsResponse(TypedDict):
    reports: List[Report]


class Analytics(TypedDict):
    last7days: AnalyticsResponse
    last30days: AnalyticsResponse
    total: AnalyticsResponse


AnalyticsTempRow = TypedDict('AnalyticsTempRow', {'hier_part': str, 'value': int})
