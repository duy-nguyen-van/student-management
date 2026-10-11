import unittest
from decimal import Decimal

from student_tracker.grading import average, classify


class GradingTests(unittest.TestCase):
    def test_average_of_equal_weights(self) -> None:
        self.assertEqual(average(Decimal("8"), Decimal("7"), Decimal("9")), Decimal("8.00"))

    def test_average_rounds_half_up_across_gioi_boundary(self) -> None:
        score = average(Decimal("8"), Decimal("8"), Decimal("7.99"))
        self.assertEqual(score, Decimal("8.00"))
        self.assertEqual(classify(score), "Giỏi")

    def test_rank_boundaries(self) -> None:
        self.assertEqual(classify(Decimal("8.00")), "Giỏi")
        self.assertEqual(classify(Decimal("7.99")), "Khá")
        self.assertEqual(classify(Decimal("7.96")), "Khá")
        self.assertEqual(classify(Decimal("6.50")), "Khá")
        self.assertEqual(classify(Decimal("6.49")), "Trung bình")
        self.assertEqual(classify(Decimal("5.00")), "Trung bình")
        self.assertEqual(classify(Decimal("4.99")), "Yếu")


if __name__ == "__main__":
    unittest.main()
