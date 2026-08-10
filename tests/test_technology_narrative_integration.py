from random import Random

from simworld.control_tower import WorldBlueprint, load_effective_affordance_catalog
from simworld.culture.knowledge import KnowledgeLedger, KnowledgeState
from simworld.culture.runtime import actor_effect_channels
from simworld.social.narrative import Narrative, NarrativeVersion, SocialMemory


def _writing_actor() -> tuple[object, KnowledgeLedger]:
    blueprint = WorldBlueprint.from_mapping({"simulation": {"root_seed": 9, "years": 1}})
    catalog = load_effective_affordance_catalog(blueprint)
    ledger = KnowledgeLedger()
    ledger.set(
        "scribe",
        KnowledgeState(
            unit_id="durable_symbolic_recording",
            mastery=0.9,
            confidence=0.8,
            acquired_at=0,
        ),
    )
    return catalog, ledger


def test_writing_capability_can_materialize_a_story_record_but_not_make_it_true() -> None:
    catalog, knowledge = _writing_actor()
    memory = SocialMemory()
    story = Narrative(
        id="story-1",
        origin_event_ids=("event-unknown",),
        versions=[
            NarrativeVersion(
                time=1,
                teller_id="scribe",
                claims=("the ruler hid all grain",),
                confidence=0.6,
            )
        ],
    )
    memory.add(story, "scribe")

    creation = actor_effect_channels(
        catalog,
        knowledge,
        "scribe",
        base_channels={"record_creation": 0.0},
        context={"marking_material_available": 1.0},
        rng=Random(1),
    )
    record = memory.create_record(
        "story-1",
        holder_id="scribe",
        record_id="record-1",
        time=2,
        record_creation=creation.get("record_creation", 0.0),
        durability=0.7,
        credibility_signal=0.8,
    )
    assert record is not None
    assert memory.narratives["story-1"].versions[record.version_index].claims == (
        "the ruler hid all grain",
    )


def test_record_can_reduce_mutation_and_sometimes_raise_acceptance_without_certifying_truth() -> None:
    catalog, knowledge = _writing_actor()
    memory = SocialMemory()
    story = Narrative(
        id="story-2",
        origin_event_ids=("event-2",),
        versions=[NarrativeVersion(time=1, teller_id="scribe", claims=("claim-x",), confidence=0.5)],
    )
    memory.add(story, "scribe")

    creation = actor_effect_channels(
        catalog,
        knowledge,
        "scribe",
        base_channels={"record_creation": 0.0},
        context={"marking_material_available": 1.0},
        rng=Random(2),
    )
    record = memory.create_record(
        "story-2",
        holder_id="scribe",
        record_id="record-2",
        time=2,
        record_creation=creation["record_creation"],
        durability=1.0,
        credibility_signal=0.9,
    )
    assert record is not None

    channels = actor_effect_channels(
        catalog,
        knowledge,
        "scribe",
        base_channels={"transmission_fidelity": 1.0, "claim_credibility": 1.0},
        context={
            "record_created": 1.0,
            "record_used": 1.0,
            "record_available": 1.0,
            "reader_accepts_medium": 1.0,
        },
        rng=Random(3),
    )
    received = memory.transmit(
        "story-2",
        teller_id="scribe",
        receiver_id="reader",
        trust=0.6,
        time=3,
        rng=Random(4),
        mutation_rate=0.5,
        record_id="record-2",
        transmission_fidelity=channels.get("transmission_fidelity", 1.0),
        credibility_multiplier=channels.get("claim_credibility", 1.0),
    )
    assert received is not None
    assert received.claims == ("claim-x",)
