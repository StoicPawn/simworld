"""Generic cultural/knowledge substrate.

High-level categories such as language, religion, ethnicity and technological eras are
intended to be derived from lower-level transmitted knowledge, conventions, beliefs,
skills and capabilities rather than created as primitive historical objects.
"""

from simworld.culture.knowledge import KnowledgeLedger, KnowledgeState, KnowledgeUnit, transmit_knowledge
from simworld.culture.technology import Affordance, InnovationContext, innovation_probability, innovation_occurs

__all__ = [
    "Affordance",
    "InnovationContext",
    "KnowledgeLedger",
    "KnowledgeState",
    "KnowledgeUnit",
    "innovation_occurs",
    "innovation_probability",
    "transmit_knowledge",
]
