from abc import ABC, abstractmethod
from collections import deque
from math import pi
from typing import Literal

import numpy as np
from matplotlib import patches
from scipy.integrate import tanhsinh

from scikit_poles_zeros._integrate import _quadvec


class Domain(ABC):
    """Abstract Domain"""

    __slots__ = ()

    @property
    @abstractmethod
    def children(self): ...

    @abstractmethod
    def contour_integral(
        self, f, *, method: Literal["gk21", "tanhsinh"] = "gk21", quadrature_args=None
    ): ...

    @abstractmethod
    def subdivide(self): ...

    @abstractmethod
    def plot(self, ax): ...

    def argument_principle(
        self,
        f,
        f_z,
        *,
        method: Literal["gk21", "tanhsinh"] = "gk21",
        quadrature_args=None,
    ):
        res = self.contour_integral(
            lambda z: f_z(z) / f(z), method=method, quadrature_args=quadrature_args
        )
        res.integral /= complex(0, 2 * pi)
        return res


class Rectangle(Domain):
    """Rectangle region in the complex plane."""

    __slots__ = "_bottom_left", "_children", "_corners", "_top_right"

    def __init__(self, bottom_left, top_right, /):
        # check that top_right is to the right and above bottom left in the complex
        # plane
        if bottom_left.real >= top_right.real or bottom_left.imag >= top_right.imag:
            msg = (
                "`top_right` must be to the right and above bottom left in the complex "
                "plane"
            )
            raise ValueError(msg)
        self._bottom_left = bottom_left
        self._top_right = top_right
        self._corners = (
            bottom_left,
            complex(top_right.real, bottom_left.imag),
            top_right,
            complex(bottom_left.real, top_right.imag),
        )

        # children created if region is subdivided
        # 0th entry left/top, 1st entry right/bottom
        self._children = []

    @property
    def bottom_left(self):
        return self._bottom_left

    @property
    def top_right(self):
        return self._top_right

    @property
    def children(self):
        return self._children

    @property
    def corners(self):
        """Returns the corners of the rectangle in a counter clockwise order
        starting from the bottom left."""
        return self._corners

    def contour_integral(
        self, f, *, method: Literal["gk21", "tanhsinh"] = "gk21", quadrature_args=None
    ):
        """Compute the contour integral of `f` around the region."""
        quadrature_args = {} if quadrature_args is None else quadrature_args

        def f_wrapped(t, _a, _b):
            return f(_a * (1 - t) + _b * t)

        a, b = np.asarray(self.corners), np.roll(self.corners, -1)
        if method == "tanhsinh":
            res = tanhsinh(f_wrapped, 0, 1, args=(a, b), **quadrature_args)
        elif method == "gk21":
            res = _quadvec(f_wrapped, 0, 1, args=(a, b), **quadrature_args)
        else:
            msg = "Invalid `method`"
            raise ValueError(msg)

        # multiply by the Jacobian
        res.integral *= b - a
        res.integral = np.sum(res.integral)
        return res

    def subdivide(self):
        diag = self.top_right - self.bottom_left

        if diag.real > diag.imag:
            ...
        else:
            ...

    def plot(self, ax):
        diff = self.top_right - self.bottom_left
        ax.add_patch(
            patches.Rectangle(
                (self.bottom_left.real, self.bottom_left.imag),
                diff.real,
                diff.imag,
                fc="none",
                edgecolor="r",
                lw=2,
            )
        )
        for child in self.children:
            child.plot(ax)


def _subdivide_domain(domain, f, f_z, max_arg_principle):
    queue = deque(domain)
    while len(queue) > 0:
        current_domain = queue.popleft()

        # 1. Compute the combined number of poles and zeros in the domain

        arg_principle = current_domain.argument_principle(f, f_z)
        # 2. Subdivide and repeat if this number is too high
        if arg_principle > max_arg_principle:
            current_domain.subdivide()
            queue.append(current_domain.children)
