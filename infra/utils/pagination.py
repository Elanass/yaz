"""Pagination utilities for the Surge platform."""

from math import ceil
from typing import Generic, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


class PageParams(BaseModel):
    """Parameters for pagination."""

    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Page size")

    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.size


class Page(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    items: list[T] = Field(description="Items in current page")
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    size: int = Field(description="Page size")
    total_pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page_params: PageParams,
    ) -> "Page[T]":
        """Create a paginated response."""
        total_pages = ceil(total / page_params.size) if total > 0 else 0

        return cls(
            items=items,
            total=total,
            page=page_params.page,
            size=page_params.size,
            total_pages=total_pages,
            has_next=page_params.page < total_pages,
            has_prev=page_params.page > 1,
        )
