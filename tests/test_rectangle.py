from __future__ import annotations

from scikit_poles_zeros._domain import Rectangle


class TestRectangle:
    def test_init(self):
        bl, tr = 0, 10 + 10j
        r = Rectangle(bl, tr)
        assert r.bottom_left == bl
        assert r.top_right == tr
