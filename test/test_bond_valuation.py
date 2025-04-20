import unittest
import datetime
import logging
from sampytools.logging_utils import init_logging

init_logging(level=logging.INFO)


class MyTestCase(unittest.TestCase):
    def test_find_next_coupon_date(self):
        from fi_utils.bond_valuation import find_next_coupon_date

        maturity = datetime.date(2048, 2, 28)
        adate = datetime.date(2025, 3, 17)
        freq = 2
        next_cpn_date = find_next_coupon_date(
            adate, maturity, freq=freq, days_per_year=365
        )
        print(
            f"next coupon date when adate is {adate}, maturity is {maturity}, freq is {freq} : {next_cpn_date}"
        )
        self.assertGreater(next_cpn_date, adate)
        maturity = datetime.date(2048, 9, 28)
        adate = datetime.date(2025, 3, 17)
        freq = 4
        next_cpn_date = find_next_coupon_date(
            adate, maturity, freq=freq, days_per_year=365
        )
        print(
            f"next coupon date when adate is {adate}, maturity is {maturity}, freq is {freq} : {next_cpn_date}"
        )
        self.assertGreater(next_cpn_date, adate)

    def test_set_the_day_of_the_date(self):
        from fi_utils.bond_valuation import set_the_day_of_the_date

        thedate = datetime.date(2025, 4, 29)
        fixed_date = set_the_day_of_the_date(thedate, 31)
        print(f"fixed date : {fixed_date}")
        self.assertEqual(fixed_date.day, 30)

    def test_calculate_pv_from_ytm(self):
        from fi_utils.bond_valuation import calculate_pv_from_ytm

        ytm = 4.0
        coupon_rate = 5.0
        pv = calculate_pv_from_ytm(
            ytm, coupon_rate, datetime.date(2025, 4, 17), datetime.date(2048, 9, 25)
        )
        print(f"PV with yield to maturity of {ytm} and coupon of {coupon_rate} : {pv}")
        self.assertTrue(pv > 100)
        ytm = 4.0
        coupon_rate = 3.0
        pv = calculate_pv_from_ytm(
            ytm, coupon_rate, datetime.date(2025, 4, 17), datetime.date(2048, 9, 25)
        )
        print(f"PV with yield to maturity of {ytm} and coupon of {coupon_rate} : {pv}")
        self.assertTrue(pv < 100)

    def test_calc_ytm_of_bond(self):
        from fi_utils.bond_valuation import calc_ytm_of_bond

        price = 89.0
        coupon = 4.0
        adate = datetime.date(2025, 4, 17)
        maturity = datetime.date(2048, 9, 25)
        ytm = calc_ytm_of_bond(price, coupon, adate, maturity)
        print(f"price {price}, coupon {coupon}, maturity {maturity}, ytm : {ytm}")
        self.assertTrue(ytm > 0)


if __name__ == "__main__":
    unittest.main()
