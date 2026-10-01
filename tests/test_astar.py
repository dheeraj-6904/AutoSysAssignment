from src.grid import GridMap
from src.reservation_table import ReservationTable
from src.spacetime_astar import space_time_astar


def test_space_time_astar_finds_path():
    grid = GridMap(8, 8, 0.0, 0.0, seed=1)
    rt = ReservationTable()
    path = space_time_astar(grid, (0, 0), (3, 0), 0, rt, max_time=40)
    assert path is not None
    assert path[0] == (0, 0)
    assert path[-1] == (3, 0)


def test_respects_reservations():
    grid = GridMap(6, 6, 0.0, 0.0, seed=1)
    rt = ReservationTable()
    rt.reserve_path([(1, 0), (1, 1), (1, 2)], start_time=1)
    path = space_time_astar(grid, (0, 0), (2, 2), 0, rt, max_time=50)
    assert path is not None
