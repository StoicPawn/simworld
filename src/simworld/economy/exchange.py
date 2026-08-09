from __future__ import annotations

from dataclasses import dataclass

from .production import Inventory


@dataclass(frozen=True, slots=True)
class ExchangeProposal:
    proposer_id: str
    receiver_id: str
    offered_good: str
    offered_quantity: float
    requested_good: str
    requested_quantity: float


@dataclass(frozen=True, slots=True)
class ExchangeResult:
    accepted: bool
    reason: str


def execute_exchange(proposal: ExchangeProposal, inventories: dict[str, Inventory], acceptance_score: float) -> ExchangeResult:
    proposer = inventories[proposal.proposer_id]
    receiver = inventories[proposal.receiver_id]
    if proposer.amount(proposal.offered_good) + 1e-9 < proposal.offered_quantity:
        return ExchangeResult(False, "proposer_insufficient_stock")
    if receiver.amount(proposal.requested_good) + 1e-9 < proposal.requested_quantity:
        return ExchangeResult(False, "receiver_insufficient_stock")
    if acceptance_score < 0.5:
        return ExchangeResult(False, "rejected")

    proposer.remove(proposal.offered_good, proposal.offered_quantity)
    receiver.add(proposal.offered_good, proposal.offered_quantity)
    receiver.remove(proposal.requested_good, proposal.requested_quantity)
    proposer.add(proposal.requested_good, proposal.requested_quantity)
    return ExchangeResult(True, "accepted")
