from pydantic import BaseModel, ConfigDict, Field


class WatchFolderBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    root_path: str = Field(min_length=1)
    inbox_path: str = Field(min_length=1)
    enabled: bool = True
    dry_run: bool = True
    auto_processing: bool = False
    auto_confidence_threshold: float = Field(default=0.95, ge=0.0, le=1.0)
    max_file_size_mb: int = Field(default=100, ge=1, le=102400)
    allowed_extensions: list[str] = Field(default_factory=list)
    exclude_patterns: list[str] = Field(default_factory=list)
    scan_interval_seconds: int = Field(default=300, ge=30)
    realtime_watch: bool = False


class WatchFolderCreate(WatchFolderBase):
    pass


class WatchFolderUpdate(WatchFolderBase):
    pass


class WatchFolderRead(WatchFolderBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
