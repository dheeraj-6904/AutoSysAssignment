from src.reservation_table import ReservationTable


def test_edge_collision_detection():
    rt = ReservationTable()
    rt.reserve_path([(0, 0), (0, 1)], 0)
    assert rt.is_edge_reserved((0, 1), (0, 0), 0)


def test_vertex_collision_detection():
    rt = ReservationTable()
    rt.reserve_path([(2, 2)], 3)
    assert rt.is_vertex_reserved((2, 2), 3)
