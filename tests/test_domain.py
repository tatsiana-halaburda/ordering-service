"""Unit tests for services.ordering.domain (no database)."""

from decimal import Decimal

import pytest
from services.ordering.domain import (
    InvalidTransition,
    LineItem,
    OrderStatus,
    compute_totals,
    validate_item_quantity,
    validate_transition,
)


def test_compute_totals_zero_items() -> None:
    t = compute_totals([], tax_rate=0.0)
    assert t.subtotal == Decimal("0.00")
    assert t.tax == Decimal("0.00")
    assert t.total == Decimal("0.00")


def test_compute_totals_two_items_no_tax() -> None:
    items = [LineItem(2.0, 4.5), LineItem(5.0, 6.5)]
    t = compute_totals(items, tax_rate=0.0)
    assert t.subtotal == Decimal("41.50")
    assert t.total == Decimal("41.50")


def test_compute_totals_decimal_float_precision() -> None:
    """0.1 + 0.2 as floats → exact Decimal line totals."""
    items = [LineItem(0.1, 1.0), LineItem(0.2, 1.0)]
    t = compute_totals(items, tax_rate=0.0)
    assert t.subtotal == Decimal("0.30")


def test_compute_totals_with_tax_rounding() -> None:
    items = [LineItem(1.0, 10.0)]
    t = compute_totals(items, tax_rate=0.05)
    assert t.subtotal == Decimal("10.00")
    assert t.tax == Decimal("0.50")
    assert t.total == Decimal("10.50")


def test_validate_item_quantity_rejects_zero_and_negative() -> None:
    with pytest.raises(ValueError, match="quantity"):
        validate_item_quantity(0.0)
    with pytest.raises(ValueError, match="quantity"):
        validate_item_quantity(-1.0)


def test_transition_draft_to_submitted_ok() -> None:
    assert validate_transition("Draft", "Submitted") == OrderStatus.SUBMITTED


def test_transition_draft_to_cancelled_ok() -> None:
    assert validate_transition("Draft", "Cancelled") == OrderStatus.CANCELLED


def test_transition_confirmed_to_submitted_rejected() -> None:
    with pytest.raises(InvalidTransition, match="Cannot transition"):
        validate_transition("Confirmed", "Submitted")


def test_transition_unknown_status_rejected() -> None:
    with pytest.raises(InvalidTransition, match="Unknown"):
        validate_transition("Unknown", "Draft")
