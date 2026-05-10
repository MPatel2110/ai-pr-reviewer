

from enum import Enum
from pydantic import BaseModel, Field


class Severity(str, Enum):
    """How serious a review comment is, mirroring linter conventions."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Category(str, Enum):
    """The kind of issue the comment is flagging."""
    BUG = "bug"
    SECURITY = "security"
    PERFORMANCE = "performance"
    STYLE = "style"
    DOCUMENTATION = "documentation"


class ReviewComment(BaseModel):
    file: str = Field(description="Path of the file the comment applies to.")
    line: int = Field(description="Line number in the new version of the file.")
    severity: Severity = Field(description="How serious the issue is.")
    category: Category = Field(description="What kind of issue this is.")
    comment: str = Field(description="The review comment shown to the developer.")