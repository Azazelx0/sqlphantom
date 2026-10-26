"""
SQLPhantom domain enumerations.
"""

from enum import Enum


class JobStatus(str, Enum):
    """Lifecycle status of an assessment job."""
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AssessmentStage(str, Enum):
    """Phases executed during an assessment run."""
    INITIALIZATION = "INITIALIZATION"
    TARGET_PROBE = "TARGET_PROBE"
    FINGERPRINTING = "FINGERPRINTING"
    DETECTION = "DETECTION"
    EXPLOITATION = "EXPLOITATION"
    DATA_EXTRACTION = "DATA_EXTRACTION"
    CLEANUP = "CLEANUP"
    FINISHED = "FINISHED"


class Severity(str, Enum):
    """Severity classification for assessment findings."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFORMATIONAL = "INFORMATIONAL"


class Confidence(str, Enum):
    """Confidence level in a finding verification."""
    CONFIRMED = "CONFIRMED"
    FIRM = "FIRM"
    TENTATIVE = "TENTATIVE"


class FindingType(str, Enum):
    """Types of vulnerabilities identified."""
    SQL_INJECTION = "SQL_INJECTION"
    BLIND_SQL_INJECTION = "BLIND_SQL_INJECTION"
    BOOLEAN_BASED_BLIND = "BOOLEAN_BASED_BLIND"
    TIME_BASED_BLIND = "TIME_BASED_BLIND"
    ERROR_BASED = "ERROR_BASED"
    UNION_BASED = "UNION_BASED"
    STACKED_QUERIES = "STACKED_QUERIES"
    OUT_OF_BAND = "OUT_OF_BAND"
    INLINE_QUERY = "INLINE_QUERY"


class ReportFormat(str, Enum):
    """Supported export formats for reporting."""
    JSON = "JSON"
    MARKDOWN = "MARKDOWN"
    HTML = "HTML"


class HttpMethod(str, Enum):
    """Standard HTTP methods supported in target definitions."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
