from simworld.spatial import CellCoord, GridSpec, SpatialMap


def main() -> None:
    spec = GridSpec(width=12, height=9, cell_size_m=1_000.0, chunk_size=4)
    world_map = SpatialMap.create(spec)

    # A mountain wall is not labelled "strategic". The pass becomes strategic
    # because it is the only traversable connection between east and west.
    for y in range(spec.height):
        world_map.layers.set("passable", CellCoord(6, y), False)
        world_map.layers.set("elevation_m", CellCoord(6, y), 3_200.0)

    pass_cell = CellCoord(6, 6)
    world_map.layers.set("passable", pass_cell, True)
    world_map.layers.set("elevation_m", pass_cell, 420.0)

    route = world_map.path(CellCoord(1, 2), CellCoord(10, 2))
    if route is None:
        raise RuntimeError("expected a route through the pass")

    print(f"route cells: {route.cells}")
    print(f"route cost: {route.cost:.0f}")
    print(f"emergent pass used: {pass_cell in route.cells}")


if __name__ == "__main__":
    main()
