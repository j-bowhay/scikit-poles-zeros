import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_equal

from scikit_poles_zeros._domain import Rectangle


class TestRectangle:
    @pytest.mark.parametrize(("bl", "tr"), [(0, 0), (0, 1), (0, 1j), (1 + 1j, 0)])
    def test_iv(self, bl, tr):
        with pytest.raises(ValueError, match="right and above bottom left"):
            Rectangle(bl, tr)

    def test_attributes(self):
        bl, tr = 1 + 2j, 12 + 10j
        r = Rectangle(bl, tr)
        assert r.bottom_left == bl
        assert r.top_right == tr
        assert r.corners == (bl, 12 + 2j, tr, 1 + 10j)

    @pytest.mark.parametrize(
        "attr", ["top_right", "bottom_left", "children", "corners"]
    )
    def test_read_only(self, attr):
        d = Rectangle(0, complex(1, 1))
        with pytest.raises(AttributeError):
            setattr(d, attr, 1)

    @pytest.mark.parametrize(
        ("f", "bl", "tr", "expected"),
        [
            (lambda z: 1 / z, complex(-1, -1), complex(1, 1), 2j * np.pi),
            (lambda z: 1 / (z**2 + 1) ** 2, -1, complex(10, 10), np.pi / 2),
            (lambda z: np.sin(z), complex(-10, -10), complex(12, 3), 0),
        ],
    )
    def test_contour_integral(self, f, bl, tr, expected):
        d = Rectangle(bl, tr)
        res = d.contour_integral(f)
        assert np.all(res.success)
        assert_equal(res.status, 0)
        assert_allclose(res.integral, expected, atol=1e-10)
