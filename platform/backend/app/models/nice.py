"""NICE Framework reference data and lab mappings.

The NICE tables are global reference data. They carry no learner or tenant
identity. Lab mappings point at a lab and a component; the component code is
stable across framework refreshes, while the statement text may be updated.
"""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)


from app.database import Base


class NiceComponent(Base):
    """One work role, task, knowledge, or skill statement."""

    __tablename__ = "nice_components"

    id = Column(Integer, primary_key=True)
    component_type = Column(String(20), nullable=False, index=True)
    code = Column(String(32), nullable=False, index=True)
    name = Column(String(200), nullable=True)
    statement = Column(Text, nullable=True)
    category_code = Column(String(16), nullable=True)
    category_name = Column(String(120), nullable=True)
    version = Column(String(16), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("component_type", "code", name="uq_nice_component_type_code"),
        Index("ix_nice_components_type_code", "component_type", "code"),
    )


class NiceLink(Base):
    """A work-role to task/knowledge/skill relationship."""

    __tablename__ = "nice_links"

    id = Column(Integer, primary_key=True)
    source_id = Column(
        Integer,
        ForeignKey("nice_components.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_id = Column(
        Integer,
        ForeignKey("nice_components.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    link_type = Column(String(24), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("source_id", "target_id", "link_type", name="uq_nice_link"),
        Index("ix_nice_links_source_type", "source_id", "link_type"),
    )


class NiceFrameworkMeta(Base):
    """The installed framework version and ingestion provenance."""

    __tablename__ = "nice_framework_meta"

    id = Column(Integer, primary_key=True)
    version = Column(String(16), nullable=False)
    source = Column(String(24), nullable=False)
    source_url = Column(String(500), nullable=True)
    fetched_at = Column(DateTime, server_default=func.now(), nullable=False)
    counts = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class LabNiceComponent(Base):
    """A selected NICE component for one lab."""

    __tablename__ = "lab_nice_components"

    id = Column(Integer, primary_key=True)
    lab_id = Column(
        Integer,
        ForeignKey("labs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    component_id = Column(
        Integer,
        ForeignKey("nice_components.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_by_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("lab_id", "component_id", name="uq_lab_nice_component"),
    )


class LabNiceMetadata(Base):
    """Review status and provenance for one lab's NICE mapping."""

    __tablename__ = "lab_nice_metadata"

    lab_id = Column(
        Integer,
        ForeignKey("labs.id", ondelete="CASCADE"),
        primary_key=True,
    )
    review_status = Column(String(24), nullable=False, default="provisional")
    source = Column(String(40), nullable=False)
    confidence = Column(String(16), nullable=True)
    policy_version = Column(Integer, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
