import numpy as np
from abc import ABC, abstractmethod

class Qubit:
    # Define in terms of complex composition of |0> and |1> and global phase factor e^ix
    def __init__(self, *args):
        self._ket = np.array([args[0], args[1]])

    @classmethod
    def from_numpy(cls, ndarray):
        qubit = cls(None, None)
        qubit._ket = ndarray
        return qubit

    @staticmethod
    def complex_round(c, ndigits):
        if c.imag:
            return complex(round(c.real, ndigits), round(c.imag, ndigits))
        return round(c.real, ndigits)

# region Properties

    # Vectors

    @property
    def ket(self):
        return self._ket.copy()

    # Values

    @property
    def global_phase_factor(self):
        return self._ket[0]

    @property
    def relative_phase_factor(self):
        if self._ket[0] == 0:
            return 1
        return self._ket[1] / self._ket[0]

    # String representations

    @property
    def phase_factored_str(self):
        return f"{Qubit.complex_round(self.global_phase_factor, 3)} * [UP + {Qubit.complex_round(self.relative_phase_factor, 3)} * DOWN]"

    @property
    def relative_phase_str(self):
        UP_coefficient = '1.0 * '
        if self.global_phase_factor == 0:
            UP_coefficient = '0.0 * '
            
        return f"[{UP_coefficient}UP + {Qubit.complex_round(self.relative_phase_factor, 3)} * DOWN]"

    @property
    def vectorized_str(self):
        return f"[{Qubit.complex_round(self._ket[0], 3)} * UP + {Qubit.complex_round(self._ket[1], 3)} * DOWN]"
    
# endregion

# region Setters

    # Vectors 
    @ket.setter
    def ket(self, value):
        self._ket = value

    # Values

    @global_phase_factor.setter
    def global_phase_factor(self, value):
        # To avoid a divide by 0 error
        self._ket = np.ndarray([value, value * self.relative_phase_factor])

    @relative_phase_factor.setter
    def relative_phase_factor(self, value):
        self._ket[1] = self.global_phase_factor * value

# endregion

# region Dunders

    def __add__(self, other):
        if isinstance(other, Qubit):
            return Qubit.from_numpy(self.ket + other.ket)
    
    def __radd__(self, other):
        if isinstance(other, Qubit):
            return Qubit.from_numpy(other.ket + self.ket)
    
    def __sub__(self, other):
        if isinstance(other, Qubit):
            return Qubit.from_numpy(self.ket - other.ket)
    
    def __rsub__(self, other):
        if isinstance(other, Qubit):
            return Qubit.from_numpy(other.ket - self.ket)

    def __mul__(self, other):
        if isinstance(other, (int, float, complex)):
            return Qubit.from_numpy(self.ket * other)
        
    def __rmul__(self, other):
        if isinstance(other, (int, float, complex)):
            return Qubit.from_numpy(other * self.ket)
        
    def __truediv__(self, other):
        if isinstance(other, (int, float, complex)):
            return Qubit.from_numpy(self.ket / other)

    def __rtruediv__(self, other):
        if isinstance(other, (int, float, complex)):
            return Qubit.from_numpy(other / self.ket)

    def __eq__(self, value):
        return self.get_relative_phase_factor() == value

    def __repr__(self):
        return self.relative_phase_str

# endregion

class QuantumGate:
    matrix = np.identity(2)

    @classmethod
    def pass_through(cls, qubit):
        return Qubit.from_numpy(qubit.ket @ cls.matrix)

class PauliX(QuantumGate):
    matrix = np.array([[0, 1], [1, 0]])
    
class PauliY(QuantumGate):
    matrix = np.array([[0, 1j], [-1j, 0]])
    
class PauliZ(QuantumGate):
    matrix = np.array([[1, 0], [0, -1]])

class H(QuantumGate):
    # - Rotates 180° around axis x = z
    # - Is its own inverse
    matrix = np.array([[2**-0.5, 2**-0.5], [2**-0.5, -2**-0.5]])

class S(QuantumGate):
    # - Rotated 90° around the z-axis clockwise looking down from +z
    # - S^2 = Z
    matrix = np.array([[1, 0], [0, 1j]])

class T(QuantumGate):
    # - Rotated 45° around the z-axis clockwise looking down from +z
    # - T^2 = S
    matrix = np.array([[1, 0], [0, 2**-0.5 + 1j * 2**-0.5]])

UP = Qubit(1, 0)
DOWN = Qubit(0, 1)

RIGHT = (UP + DOWN) * (1 / 2**0.5)
LEFT = (UP - DOWN) * (1 / 2**0.5)

OUT = (UP + 1j * DOWN) * (1 / 2**0.5)
IN = (UP - 1j * DOWN) * (1 / 2**0.5)

def example_gates(UP, RIGHT, OUT):

    print()

    print("-" * 50)
    print()

    print(f"UP: {UP}")
    print(f"PauliX(UP): {PauliX.pass_through(UP)}")
    print()

    print(f"RIGHT: {RIGHT}")
    print(f"PauliY(RIGHT): {PauliY.pass_through(RIGHT)}")
    print()

    print(f"OUT: {OUT}")
    print(f"PauliZ(OUT): {PauliZ.pass_through(OUT)}")
    print()

    print("-" * 50)
    print()

    print(f"UP: {UP}")
    print(f"H.pass_through(UP): {H.pass_through(UP)}")
    print()

    print(f"RIGHT: {RIGHT}")
    print(f"H.pass_through(RIGHT): {H.pass_through(RIGHT)}")
    print()

    print(f"OUT: {OUT}")
    print(f"H.pass_through(OUT): {H.pass_through(OUT)}")
    print()

    print("-" * 50)
    print()

    print(f"UP: {UP}")
    print(f"S.pass_through(UP): {S.pass_through(UP)}")
    print()

    print(f"RIGHT: {RIGHT}")
    print(f"S.pass_through(RIGHT): {S.pass_through(RIGHT)}")
    print()

    print(f"OUT: {OUT}")
    print(f"S.pass_through(OUT): {S.pass_through(OUT)}")
    print()

    print("-" * 50)
    print()

    print(f"UP: {UP}")
    print(f"T.pass_through(UP): {T.pass_through(UP)}")
    print()

    print(f"RIGHT: {RIGHT}")
    print(f"T.pass_through(RIGHT): {T.pass_through(RIGHT)}")
    print()

    print(f"OUT: {OUT}")
    print(f"T.pass_through(OUT): {T.pass_through(OUT)}")
    print()

    print("-" * 50)
    print()

example_gates(UP, RIGHT, OUT)
