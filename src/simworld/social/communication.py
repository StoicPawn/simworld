from __future__ import annotations

from dataclasses import dataclass

from simworld.social.epistemics import EpistemicState


@dataclass(frozen=True, slots=True)
class Message:
    sender_id: str
    receiver_id: str
    proposition: str
    asserted_probability: float
    domain: str = "general"
    truthful_probability: float | None = None
    motive: str | None = None


def communicate(message: Message, receiver: EpistemicState, *, time: int) -> float:
    """Deliver a claim using receiver-side trust, not omniscient truth.

    ``truthful_probability`` is provenance available to the simulator/evaluator; the
    receiver does not use it while updating the belief.
    """
    trust = receiver.trust.get(message.sender_id, message.domain)
    receiver.observe(
        message.proposition,
        message.asserted_probability,
        reliability=trust,
        time=time,
        source_id=message.sender_id,
        salience=0.55,
    )
    return trust


def evaluate_message_accuracy(message: Message, realized_probability: float) -> float:
    """Score hindsight accuracy after evidence becomes available."""
    claimed = max(0.0, min(1.0, message.asserted_probability))
    realized = max(0.0, min(1.0, realized_probability))
    return 1.0 - abs(claimed - realized)
