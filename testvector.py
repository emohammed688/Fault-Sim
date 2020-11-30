import csv
from typing import List, List, Set, Union, Tuple
from nodes import Value
import unittest
import copy


class TestVector(object):
    def __init__(self, values: str):
        self.values: List[Value] = [
            Value(char) for char in values
        ]

    def __repr__(self):
        return ''.join([str(value) for value in self.values])

    def __iter__(self) -> Value:
        for value in self.values:
            yield value

    def __len__(self) -> int:
        return len(self.values)

    def __eq__(self, other: Union['TestVector', str, int]):
        if type(other) == int:
            other = format(other, f"0{len(self)}b")
        elif len(other) != len(self):
            return False
        for val1, val2 in zip(self, other):
            if val1 != val2:
                return False
        return True

    def __ne__(self, other: 'TestVector'):
        return ~self.__eq__(other)

    def __hash__(self):
        return hash(('string', str(self)))

    def __getitem__(self, item) -> 'TestVector':
        return TestVector.from_values(self.values[item])

    @classmethod
    def from_values(cls, values: List[Value]):
        cls_obj = TestVector('')
        cls_obj.values = values
        return cls_obj


class LFSR(object):
    # _h = [0]

    def __init__(self, q: Union[str, int]):
        q_type = type(q)
        if q_type == int:
            self._q = q
        elif q_type == str:
            self._q = int(q, 2)
        else:
            raise TypeError

    @property
    def h(self) -> List[int]:  # example:
        return [1, ] + list(1 if n in self._h else 0 for n in range(1, 8))

    # @h.setter
    # def h(self, value: List[int]):
    #     self._h = set(value)

    @property
    def q(self) -> List[int]:  # example: 18
        q = [int(b) for b in format(self._q, "08b")]
        q.reverse()
        return list(q)

    @q.setter
    def q(self, q: Union[int, str]):
        if type(q) == str:
            self._q = int(q, 2)
        elif type(q) == int:
            self._q = q
        else:
            raise TypeError

    @classmethod
    def taps(cls, h: List[int]):
        cls._h = list(h)

    def lfsr_algorithm(self):
        q = self.q
        qprime = copy.copy(q)
        h = self.h
        qprime[0] = q[7] * h[0]
        for n in range(1, 8):
            qprime[n] = (q[7] * h[n]) ^ q[n - 1]
        qprime.reverse()
        qprime = ''.join([str(bit) for bit in qprime])
        self.q = qprime
        return qprime

    def __call__(self, *args, **kwargs) -> TestVector:
        return TestVector(self.lfsr_algorithm())


class TestVectorGenerator(object):
    """
    Args:
        seed: The integer seed to be used for the LFSRs
        input_bits: The number of inputs in the circuit
        taps: The taps used for h in the PRPG algorithm
    """

    def __init__(self, seed: int, input_bits: int, taps: List[int] = ()):
        self.input_bits = input_bits
        LFSR.taps(taps)
        # lfsr_sum_length = self.bits_ceiling(input_bits)
        # binary_seed = format(seed, f"0{self.bits_ceiling(seed.bit_length())}b")
        # while len(binary_seed) < lfsr_sum_length:
        #     binary_seed += format(seed, "0b")
        # binary_seed = binary_seed[:lfsr_sum_length]

        # while(trimmed_seed.bit_length() < trim_length):
        #     trimmed_seed = int(
        #         str(trimmed_seed) + str(seed)
        #     )
        # trimmed_seed = format(trimmed_seed, "x")[:trim_length]

        seed_length = self.bits_ceiling(input_bits) if input_bits > seed.bit_length() else \
            self.bits_ceiling(seed.bit_length())
        # seed_length = TestVectorGenerator.bits_ceiling(input_bits) \
        #     if input_bits > seed.bit_length() else \
        #     TestVectorGenerator.bits_ceiling(seed.bit_length())
        binary_seed = format(seed, f"0{seed_length}b")
        self.lfsrs = [LFSR(
            binary_seed[n: n + 8])
            for n in range(0, seed_length, 8)
        ]

    def __call__(self) -> List[TestVector]:
        # def __call__(self, *args, **kwargs) -> List[TestVector]:
        """Returns: A list of TestVectors using the PRPG algorithm"""
        test_vector_count = 2 ** self.input_bits if 2 ** self.input_bits < 100 else 100
        lfsr_count = len(self.lfsrs)
        test_vectors: List[TestVector] = []
        # i = 0
        # while len(test_vectors) < test_vector_count:
        #     test_vector = self.lfsrs[i % lfsr_count]()[:self.input_bits]
        #     if test_vector not in test_vectors:
        #         test_vectors.append(test_vector)
        #     i += 1

        test_vectors = [TestVector.from_values(
            [value for values in [lfsr() for lfsr in self.lfsrs][:self.input_bits]
             for value in values]
        ) for _ in range(0, test_vector_count)]
        # i = 0
        # while len(result) < test_vector_count:
        #     test_vector = self.lfsrs[i % lfsr_count]()[:]

        with open(f"_testvectors_from_LFSR.txt", 'w') as f:
            f.writelines([str(testvector) + '\n' for testvector in test_vectors])
        return test_vectors

    @staticmethod
    def bits_ceiling(bits: int) -> int:
        """Return: Rounds the integer up to the nearest multiple of 8"""
        return bits // 8 * 8 + (8 if bits % 8 else 0)

    @staticmethod
    # @write_csv
    def from_counter(seed: int, input_bits: int) -> List[TestVector]:
        """

        Args:
            seed: The integer seed to be used for the LFSRs
            input_bits: The number of inputs in the circuit

        Returns:
            A list of test vectors generated by incrementing the seed at most 100 times
        """
        test_vector_count = 2 ** input_bits if 2 ** input_bits < 100 else 100
        seed_length = TestVectorGenerator.bits_ceiling(input_bits) \
            if input_bits > seed.bit_length() else \
            TestVectorGenerator.bits_ceiling(seed.bit_length())
        trimmed_seed = int(format(seed, f"0{seed_length}b")[:input_bits], 2)
        result = [TestVector(
            format((trimmed_seed + n) % test_vector_count, f"0{input_bits}b"))
            for n in range(0, test_vector_count)
        ]
        with open(f"_testvectors_from_counter.txt", 'w') as f:
            f.writelines([str(testvector) + '\n' for testvector in result])
        return result
        # with open(f"{__name__}")


class LFSRTest(unittest.TestCase):
    def setUp(self) -> None:
        super(LFSRTest, self).setUp()

    def test1(self):
        seed = 0x1234
        input_bits = 3
        taps = list([2, 3, 5])
        tvg = TestVectorGenerator(seed, input_bits, taps)
        test_vectors = tvg()
        self.assertEqual(len(test_vectors), 8, 'unexpected length')  # Check that we got 16 test vectors
        self.assertEqual(len(test_vectors), len(set(test_vectors)), 'non-unique elements')
        test_vectors = TestVectorGenerator.from_counter(seed, input_bits)
        self.assertEqual(len(test_vectors), 8, 'unexpected length')  # Check that we got 16 test vectors
        self.assertEqual(len(test_vectors), len(set(test_vectors)), 'non-unique elements')

    def test2(self):
        seed = 0x1
        input_bits = 4
        taps = list([2, 3, 5])
        tvg = TestVectorGenerator(seed, input_bits, taps)
        test_vectors = tvg()
        self.assertEqual(len(test_vectors), 16, 'unexpected length')  # Check that we got 16 test vectors
        self.assertEqual(len(test_vectors), len(set(test_vectors)), 'non-unique elements')
        test_vectors = TestVectorGenerator.from_counter(seed, input_bits)
        self.assertEqual(len(test_vectors), 16, 'unexpected length')  # Check that we got 16 test vectors
        self.assertEqual(len(test_vectors), len(set(test_vectors)), 'non-unique elements')

    def test3(self):
        seed = 0x12345689ABCDEF
        input_bits = 32
        taps = list([3])
        tvg = TestVectorGenerator(seed, input_bits, taps)
        test_vectors = tvg()
        self.assertEqual(len(test_vectors), 100, 'unexpected length')  # Check that we got 16 test vectors
        self.assertEqual(len(test_vectors), len(set(test_vectors)), 'non-unique elements')
        test_vectors = TestVectorGenerator.from_counter(seed, input_bits)
        self.assertEqual(len(test_vectors), 100, 'unexpected length')  # Check that we got 16 test vectors
        self.assertEqual(len(test_vectors), len(set(test_vectors)), 'non-unique elements')


if __name__ == '__main__':
    unittest.main()
