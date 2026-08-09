from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4


def new_obligation_id() -> str:
    return f"obl_{uuid4().hex}"


@dataclass(slots=True)
class Obligation:
    debtor_id: str
    creditor_id: str
    kind: str
    resource: str
    amount: float
    created_at: int
    due_at: int
    id: str = field(default_factory=new_obligation_id)
    fulfilled: float = 0.0
    debtor_acceptance: float = 0.5
    external_recognition: float = 0.0
    enforceability: float = 0.0
    origin_event_id: str | None = None

    @property
    def outstanding(self) -> float:
        return max(0.0, self.amount - self.fulfilled)

    @property
    def settled(self) -> bool:
        return self.outstanding <= 1e-9


@dataclass(frozen=True, slots=True)
class ObligationPayment:
    obligation_id: str
    time: int
    amount: float
    completed: bool


@dataclass(slots=True)
class ObligationRegistry:
    obligations: dict[str, Obligation] = field(default_factory=dict)
    payments: list[ObligationPayment] = field(default_factory=list)

    def add(self, obligation: Obligation) -> None:
        if obligation.amount <= 0:
            raise ValueError("obligation amount must be positive")
        if obligation.id in self.obligations:
            raise ValueError(f"duplicate obligation: {obligation.id}")
        self.obligations[obligation.id] = obligation

    def due(self, time: int) -> tuple[Obligation, ...]:
        return tuple(
            obligation
            for obligation in self.obligations.values()
            if not obligation.settled and obligation.due_at <= time
        )

    def between(self, debtor_id: str, creditor_id: str, *, unsettled_only: bool = False) -> tuple[Obligation, ...]:
        return tuple(
            obligation
            for obligation in self.obligations.values()
            if obligation.debtor_id == debtor_id
            and obligation.creditor_id == creditor_id
            and (not unsettled_only or not obligation.settled)
        )

    def pay(self, obligation_id: str, amount: float, time: int) -> ObligationPayment:
        if amount < 0:
            raise ValueError("payment cannot be negative")
        obligation = self.obligations[obligation_id]
        paid = min(amount, obligation.outstanding)
        obligation.fulfilled += paid
        payment = ObligationPayment(obligation_id, time, paid, obligation.settled)
        self.payments.append(payment)
        return payment

    def dependency(self, debtor_id: str, creditor_id: str) -> float:
        active = self.between(debtor_id, creditor_id, unsettled_only=True)
        burden = sum(obligation.outstanding for obligation in active)
        recognition = sum(
            obligation.external_recognition + obligation.debtor_acceptance
            for obligation in active
        )
        return min(1.0, 0.12 * burden + 0.08 * recognition)
