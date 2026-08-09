from simworld.core.randomness import RandomStreams, derive_seed


def test_seed_derivation_is_stable_and_semantic() -> None:
    assert derive_seed(42, "demography", "A") == derive_seed(42, "demography", "A")
    assert derive_seed(42, "demography", "A") != derive_seed(42, "demography", "B")
    assert derive_seed(42, "demography", "A") != derive_seed(43, "demography", "A")


def test_unrelated_stream_consumption_does_not_perturb_existing_stream() -> None:
    baseline = RandomStreams(104729)
    expected = [baseline.stream("encounters").random() for _ in range(5)]

    with_extra_feature = RandomStreams(104729)
    extra = with_extra_feature.stream("future_religion")
    _ = [extra.random() for _ in range(100)]
    observed = [with_extra_feature.stream("encounters").random() for _ in range(5)]

    assert observed == expected


def test_ephemeral_stream_is_repeatable_without_shared_mutable_state() -> None:
    streams = RandomStreams(9)
    first = streams.ephemeral("actor", "A", "year", 12).random()
    second = streams.ephemeral("actor", "A", "year", 12).random()
    other_year = streams.ephemeral("actor", "A", "year", 13).random()

    assert first == second
    assert first != other_year
