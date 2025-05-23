from collections.abc import Set
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Eis:
    a: int
    b: int = 0

    def components(self):
        return (self.a, self.b)

    def copy(self):
        return Eis(self.a, self.b)

    def __eq__(self, other):
        if isinstance(other, Eis):
            return (self.a, self.b) == (other.a, other.b)
        if isinstance(other, complex):
            return complex(self) == other

        if isinstance(other, Gau):
            return self.b == 0 and other.b == 0 and self.a == other.a

        # Assumes `other` is real
        return self.b == 0 and self.a == other

    def __hash__(self):
        return hash(complex(self))

    def __repr__(self):
        return f"{self.a}+{self.b}ω"

    def __add__(self, other):
        if not isinstance(other, Eis):
            return self + Eis(other)

        return Eis(self.a + other.a, self.b + other.b)

    def __mul__(self, other):
        if not isinstance(other, Eis):
            return self * Eis(other)

        a, b, c, d = self.a, self.b, other.a, other.b
        return Eis(a*c - b*d, a*d + b*c - b*d)

    def conjugate(self):
        return Eis(self.a - self.b, -self.b)

    def norm(self):
        return self.a*self.a - self.a*self.b + self.b*self.b

    def divides(self, other):
        numer = other * self.conjugate()
        denom = self.norm()
        return denom != 0 and numer.a % denom == 0 and numer.b % denom == 0
    def divby(self, other):
        if not isinstance(other, Eis):
            return Eis(other).divides(self)
        return other.divides(self)

    def congruent(self, other, modulus):
        if isinstance(other, Set):
            return any(self.congruent(item, modulus) for item in other)
        if not isinstance(modulus, Eis):
            return Eis(modulus).divides(other - self)
        return modulus.divides(other - self)

    def __truediv__(self, other):
        if not isinstance(other, Eis):
            return self / Eis(other)

        numer = self * other.conjugate()
        denom = other.norm()

        if numer.a % denom != 0 or numer.b % denom != 0:
            raise ValueError("Not divisible.")

        return Eis(numer.a // denom, numer.b // denom)

    def __pow__(self, exponent):
        if not isinstance(exponent, int):
            raise ValueError("Exponent must be integer.")

        if exponent == 0:
            return Eis(1)
        if exponent == 1:
            return self

        result = (self * self)**(exponent // 2)
        if exponent % 2 == 1:
            result *= self
        return result

    # Derived methods

    def __neg__(self):
        return -1 * self
    def __pos__(self):
        return self

    def __sub__(self, other):
        return self + -other

    def __radd__(self, other):
        return self + other
    def __rsub__(self, other):
        return -self + other
    def __rmul__(self, other):
        return self * other
    def __rtruediv__(self, other):
        if not isinstance(other, Eis):
            return Eis(other)/self
        return other/self
    def __rpow__(self, other):
        if not isinstance(other, Eis):
            return Eis(other)**self
        return other**self

    def __abs__(self):
        return math.sqrt(self.norm())
    def arg(self):
        return math.atan2(self.imag(), self.real())

    # Conversions

    def __int__(self):
        if self.b != 0:
            raise ValueError("Cannot convert to int; value is not an integer.")
        return self.a
    def __float__(self):
        if self.b != 0:
            raise ValueError("Cannot convert to float; value is not real.")
        return self.a

    def real(self):
        return self.a - 0.5*self.b
    def imag(self):
        return math.sqrt(0.75)*self.b
    def __iter__(self):
        return iter((self.real(), self.imag()))
    def __complex__(self):
        return self.real() + self.imag()*1j

    # Static functions

    @staticmethod
    def num_closest(z, tol=0.0):
        def eq(z1, z2):
            if tol == 0:
                return z1 == z2
            return abs(z2 - z1) <= tol

        to_grid = z.real + math.sqrt(1/3)*z.imag + 2j*math.sqrt(1/3)*z.imag
        a, b = math.floor(to_grid.real), math.floor(to_grid.imag)
        x, y = to_grid.real - a, to_grid.imag - b

        if (eq(x, 1/3) and eq(y, 2/3)) or (eq(x, 2/3) and eq(y, 1/3)):
            return 3

        if (eq(x + y, 1) and x - 2*y <= tol and y - 2*x <= tol) \
        or ((eq(y, 2*x) or eq(2*y, x)) and 1 - (x + y) <= tol) \
        or ((eq(y + 1, 2*x) or eq(2*y, x + 1)) and x + y - 1 <= tol):
            return 2

        return 1

    @staticmethod
    def closest(z):
        to_grid = z.real + math.sqrt(1/3)*z.imag + 2j*math.sqrt(1/3)*z.imag
        a, b = math.floor(to_grid.real), math.floor(to_grid.imag)
        x, y = to_grid.real - a, to_grid.imag - b

        if (x, y) == (1/3, 2/3):
            return Eis(a, b)
        if (x, y) == (2/3, 1/3):
            return Eis(a + 1, b + 1)

        if (x + y == 1 and 2*y >= x and y <= 2*x) \
        or ((y == 2*x or 2*y == x) and x + y >= 1) \
        or ((y + 1 == 2*x or 2*y == x + 1) and x + y <= 1):
            realigned = (z + 1/3)*1j*math.sqrt(3)
            closest1 = complex(Eis.closest(realigned))
            unaligned = closest1/(1j*math.sqrt(3)) - 1/3
            return Eis.closest(unaligned)

        if y + 1 < 2*x and 2*y < x:
            return Eis(a + 1, b)
        if 2*y > x + 1 and y > 2*x:
            return Eis(a, b + 1)
        if x + y > 1:
            return Eis(a + 1, b + 1)
        return Eis(a, b)

W = Eis(0, 1)
WC = Eis(-1, -1)

@dataclass(frozen=True)
class Gau:
    a: int
    b: int = 0

    def components(self):
        return (self.a, self.b)

    def copy(self):
        return Gau(self.a, self.b)

    def __eq__(self, other):
        if isinstance(other, Gau):
            return (self.a, self.b) == (other.a, other.b)
        if isinstance(other, complex):
            return complex(self) == other

        if isinstance(other, Eis):
            return self.b == 0 and other.b == 0 and self.a == other.a

        # Assumes `other` is real
        return self.b == 0 and self.a == other

    def __hash__(self):
        return hash(complex(self))

    def __repr__(self):
        if self.b == 0:
            return str(self.a)
        return f"{self.a} + {self.b}i"

    def __add__(self, other):
        if not isinstance(other, Gau):
            return self + Gau(other)

        return Gau(self.a + other.a, self.b + other.b)

    def __mul__(self, other):
        if not isinstance(other, Gau):
            return self * Gau(other)

        a, b, c, d = self.a, self.b, other.a, other.b
        return Gau(a*c - b*d, a*d + b*c)

    def conjugate(self):
        return Gau(self.a, -self.b)

    def norm(self):
        return self.a*self.a + self.b*self.b

    def divides(self, other):
        numer = other * self.conjugate()
        denom = self.norm()
        return denom != 0 and numer.a % denom == 0 and numer.b % denom == 0
    def divby(self, other):
        if not isinstance(other, Gau):
            return Gau(other).divides(self)
        return other.divides(self)

    def congruent(self, other, modulus):
        if isinstance(other, Set):
            return any(self.congruent(item, modulus) for item in other)
        if not isinstance(modulus, Gau):
            return Gau(modulus).divides(other - self)
        return modulus.divides(other - self)

    def __truediv__(self, other):
        if not isinstance(other, Gau):
            return self / Gau(other)

        numer = self * other.conjugate()
        denom = other.norm()

        if numer.a % denom != 0 or numer.b % denom != 0:
            raise ValueError("Not divisible.")

        return Gau(numer.a // denom, numer.b // denom)

    def __pow__(self, exponent):
        if not isinstance(exponent, int):
            raise ValueError("Exponent must be integer.")

        if exponent == 0:
            return Gau(1)
        if exponent == 1:
            return self

        result = (self * self)**(exponent // 2)
        if exponent % 2 == 1:
            result *= self
        return result

    # Derived methods

    def __neg__(self):
        return -1 * self
    def __pos__(self):
        return self

    def __sub__(self, other):
        return self + -other

    def __radd__(self, other):
        return self + other
    def __rsub__(self, other):
        return -self + other
    def __rmul__(self, other):
        return self * other
    def __rtruediv__(self, other):
        if not isinstance(other, Gau):
            return Gau(other)/self
        return other/self
    def __rpow__(self, other):
        if not isinstance(other, Gau):
            return Gau(other)**self
        return other**self

    def __abs__(self):
        return math.sqrt(self.norm())
    def arg(self):
        return math.atan2(self.imag(), self.real())

    # Conversions

    def __int__(self):
        if self.b != 0:
            raise ValueError("Cannot convert to int; value is not an integer.")
        return self.a
    def __float__(self):
        if self.b != 0:
            raise ValueError("Cannot convert to float; value is not real.")
        return self.a

    def real(self):
        return self.a
    def imag(self):
        return self.b
    def __iter__(self):
        return iter((self.real(), self.imag()))
    def __complex__(self):
        return self.real() + self.imag()*1j

I = Gau(0, 1)
