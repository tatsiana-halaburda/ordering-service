"""Pure business rules for ordering (no I/O)."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum


class OrderStatus(StrEnum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"


ALLOWED_TRANSITIONS: dict[OrderStatus, frozenset[OrderStatus]] = {
    OrderStatus.DRAFT: frozenset({OrderStatus.SUBMITTED, OrderStatus.CANCELLED}),
    OrderStatus.SUBMITTED: frozenset({OrderStatus.CONFIRMED, OrderStatus.CANCELLED}),
    OrderStatus.CONFIRMED: frozenset({OrderStatus.CANCELLED}),
    OrderStatus.CANCELLED: frozenset(),
}


class InvalidTransition(ValueError):
    """Raised when status change is not allowed."""


def validate_transition(current: str, target: str) -> OrderStatus:
    try:
        cur_e = OrderStatus(current)
    except ValueError as exc:
        raise InvalidTransition(f"Unknown order status: {current!r}") from exc
    try:
        tgt_e = OrderStatus(target)
    except ValueError as exc:
        raise InvalidTransition(f"Invalid target status: {target!r}") from exc
    if tgt_e not in ALLOWED_TRANSITIONS[cur_e]:
        raise InvalidTransition(f"Cannot transition from {current!r} to {target!r}")
    return tgt_e


@dataclass(frozen=True)
class LineItem:
    quantity: float
    unit_price: float


@dataclass(frozen=True)
class Totals:
    subtotal: Decimal
    tax: Decimal
    total: Decimal


def _money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def compute_totals(items: Iterable[LineItem], tax_rate: float = 0.0) -> Totals:
    sub = Decimal("0")
    for it in items:
        validate_item_quantity(it.quantity)
        line = Decimal(str(it.quantity)) * Decimal(str(it.unit_price))
        sub += line
    sub = _money(sub)
    tr = Decimal(str(tax_rate))
    tax = _money(sub * tr) if tr else Decimal("0.00")
    total = _money(sub + tax)
    return Totals(subtotal=sub, tax=tax, total=total)


def validate_item_quantity(quantity: float) -> float:
    if quantity <= 0:
        msg = "quantity must be > 0"
        raise ValueError(msg)
    return quantity
