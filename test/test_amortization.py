import unittest
from datetime import date
from fi_utils.abor_utils import compute_linear_amortization_schedule


class TestLinearAmortizationSchedule(unittest.TestCase):
    def test_basic_accretion(self):
        initial_book_price = 95.0
        maturity = date(2030, 4, 30)
        purchase_date = date(2025, 4, 30)
        period_length_years = 1.0

        periods, delta = compute_linear_amortization_schedule(
            initial_book_price, maturity, purchase_date, period_length_years
        )

        self.assertEqual(periods, 5)
        self.assertAlmostEqual(delta, 1.0)

    def test_basic_amortization(self):
        initial_book_price = 105.0
        maturity = date(2030, 4, 30)
        purchase_date = date(2025, 4, 30)
        period_length_years = 1.0

        periods, delta = compute_linear_amortization_schedule(
            initial_book_price, maturity, purchase_date, period_length_years
        )

        self.assertEqual(periods, 5)
        self.assertAlmostEqual(delta, -1.0)

    def test_partial_years(self):
        initial_book_price = 95.0
        maturity = date(2027, 4, 30)
        purchase_date = date(2025, 4, 30)
        period_length_years = 0.5  # semiannual

        periods, delta = compute_linear_amortization_schedule(
            initial_book_price, maturity, purchase_date, period_length_years
        )

        self.assertEqual(periods, 4)  # 2 years / 0.5
        self.assertAlmostEqual(delta, 1.25)

    def test_maturity_before_purchase(self):
        with self.assertRaises(ValueError):
            compute_linear_amortization_schedule(
                initial_book_price=95.0,
                maturity=date(2024, 4, 30),
                purchase_date=date(2025, 4, 30),
                period_length_years=1.0,
            )

    def test_zero_period_length(self):
        with self.assertRaises(ZeroDivisionError):
            compute_linear_amortization_schedule(
                initial_book_price=95.0,
                maturity=date(2030, 4, 30),
                purchase_date=date(2025, 4, 30),
                period_length_years=0.0,
            )


if __name__ == "__main__":
    unittest.main()
