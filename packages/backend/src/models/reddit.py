"""SQLAlchemy ORM models for Reddit scraper and analysis tables."""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class RedditJob(Base):
    """A user-initiated scrape + analysis job."""

    __tablename__ = "reddit_jobs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Comma-separated list of subreddits e.g. "learnprogramming,Python"
    subreddits: Mapped[str] = mapped_column(Text, nullable=False)
    scrape_limit: Mapped[int] = mapped_column(
        Integer, default=25, nullable=False
    )
    # pending | scraping | analyzing | done | failed
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False, index=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    post_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    comment_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    pain_point_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    posts: Mapped[List["RedditPost"]] = relationship(
        "RedditPost", back_populates="job", cascade="all, delete-orphan"
    )
    pain_points: Mapped[List["RedditPainPoint"]] = relationship(
        "RedditPainPoint", back_populates="job", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<RedditJob(id={self.id}, status={self.status}, subreddits={self.subreddits})>"


class RedditPost(Base):
    """A scraped Reddit post belonging to a job."""

    __tablename__ = "reddit_posts"
    __table_args__ = (
        UniqueConstraint("job_id", "post_id", name="uq_reddit_posts_job_post"),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    job_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("reddit_jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    post_id: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    subreddit: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    author: Mapped[str] = mapped_column(
        String(100), nullable=False, default="[deleted]"
    )
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    num_comments: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Relationships
    job: Mapped["RedditJob"] = relationship("RedditJob", back_populates="posts")
    comments: Mapped[List["RedditComment"]] = relationship(
        "RedditComment", back_populates="post", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<RedditPost(id={self.id}, post_id={self.post_id}, subreddit={self.subreddit})>"


class RedditComment(Base):
    """A scraped Reddit comment belonging to a post."""

    __tablename__ = "reddit_comments"
    __table_args__ = (
        UniqueConstraint(
            "post_id", "comment_id", name="uq_reddit_comments_post_comment"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    post_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("reddit_posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    comment_id: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )
    subreddit: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    author: Mapped[str] = mapped_column(
        String(100), nullable=False, default="[deleted]"
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    parent_comment_id: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Relationships
    post: Mapped["RedditPost"] = relationship(
        "RedditPost", back_populates="comments"
    )

    def __repr__(self) -> str:
        return f"<RedditComment(id={self.id}, comment_id={self.comment_id})>"


class RedditPainPoint(Base):
    """A pain point identified by LLM analysis of a subreddit's comments."""

    __tablename__ = "reddit_pain_points"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    job_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("reddit_jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    subreddits: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[int] = mapped_column(Integer, nullable=False)  # 0–100
    target_audience: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    job: Mapped["RedditJob"] = relationship(
        "RedditJob", back_populates="pain_points"
    )
    evidence: Mapped[List["RedditEvidence"]] = relationship(
        "RedditEvidence",
        back_populates="pain_point",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<RedditPainPoint(id={self.id}, title={self.title[:40]}, severity={self.severity})>"


class RedditEvidence(Base):
    """Supporting comment evidence for a pain point."""

    __tablename__ = "reddit_evidence"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    pain_point_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("reddit_pain_points.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    comment_id: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    link: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    pain_point: Mapped["RedditPainPoint"] = relationship(
        "RedditPainPoint", back_populates="evidence"
    )

    def __repr__(self) -> str:
        return f"<RedditEvidence(id={self.id}, pain_point_id={self.pain_point_id})>"
