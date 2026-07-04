from __future__ import annotations

from datetime import datetime
from typing import Any
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class WatchFolder(Base):
    __tablename__ = "watch_folders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    root_path: Mapped[str] = mapped_column(Text, nullable=False)
    inbox_path: Mapped[str] = mapped_column(Text, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    dry_run: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    auto_processing: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    auto_confidence_threshold: Mapped[float] = mapped_column(Float, default=0.95, nullable=False)
    max_file_size_mb: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    allowed_extensions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    exclude_patterns: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    scan_interval_seconds: Mapped[int] = mapped_column(Integer, default=300, nullable=False)
    realtime_watch: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    files: Mapped[list["FileRecord"]] = relationship(back_populates="watch_folder")


class FileRecord(Base):
    __tablename__ = "file_records"
    __table_args__ = (UniqueConstraint("watch_folder_id", "absolute_path", name="uq_file_watch_path"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    watch_folder_id: Mapped[int] = mapped_column(ForeignKey("watch_folders.id", ondelete="CASCADE"), nullable=False)
    absolute_path: Mapped[str] = mapped_column(Text, nullable=False)
    relative_path: Mapped[str] = mapped_column(Text, nullable=False)
    filename: Mapped[str] = mapped_column(Text, nullable=False)
    extension: Mapped[str] = mapped_column(String(32), default="", nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(255))
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    sha256: Mapped[str | None] = mapped_column(String(64), index=True)
    created_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    modified_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(50), default="discovered", index=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    watch_folder: Mapped[WatchFolder] = relationship(back_populates="files")
    analyses: Mapped[list["AnalysisResult"]] = relationship(back_populates="file_record")
    operations: Mapped[list["FileOperation"]] = relationship(back_populates="file_record")
    approvals: Mapped[list["Approval"]] = relationship(back_populates="file_record")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_record_id: Mapped[int] = mapped_column(ForeignKey("file_records.id", ondelete="CASCADE"), nullable=False)
    category_id: Mapped[str] = mapped_column(String(100), nullable=False)
    subcategory_id: Mapped[str | None] = mapped_column(String(100))
    customer_name: Mapped[str | None] = mapped_column(String(255))
    document_date: Mapped[str | None] = mapped_column(String(32))
    suggested_filename: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(Text, default="", nullable=False)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(50), default="v1", nullable=False)
    raw_response: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    file_record: Mapped[FileRecord] = relationship(back_populates="analyses")


class Approval(Base):
    __tablename__ = "approvals"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_record_id: Mapped[int] = mapped_column(ForeignKey("file_records.id", ondelete="CASCADE"), nullable=False)
    analysis_result_id: Mapped[int] = mapped_column(ForeignKey("analysis_results.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False, index=True)
    approved_by: Mapped[str | None] = mapped_column(String(255))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    file_record: Mapped[FileRecord] = relationship(back_populates="approvals")


class FileOperation(Base):
    __tablename__ = "file_operations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_record_id: Mapped[int] = mapped_column(ForeignKey("file_records.id", ondelete="CASCADE"), nullable=False)
    operation_type: Mapped[str] = mapped_column(String(50), default="move", nullable=False)
    source_path: Mapped[str] = mapped_column(Text, nullable=False)
    destination_path: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    dry_run: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    source_sha256: Mapped[str | None] = mapped_column(String(64))
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    undone_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)
    file_record: Mapped[FileRecord] = relationship(back_populates="operations")


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    destination_template: Mapped[str] = mapped_column(Text, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(100))
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
