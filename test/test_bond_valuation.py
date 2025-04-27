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

    def test_get_possible_coupon_dates_in_the_year(self):
        from fi_utils.bond_valuation import get_possible_coupon_dates_in_the_year

        maturity = datetime.date(2048, 9, 25)
        freq = 2
        year = 2025
        coupon_dates = get_possible_coupon_dates_in_the_year(maturity, year, freq)
        print(f"maturity {maturity}, year {year}, freq {freq}, {coupon_dates}")
        self.assertTrue(len(coupon_dates) > 0)

        maturity = datetime.date(2048, 1, 25)
        freq = 2
        year = 2025
        coupon_dates = get_possible_coupon_dates_in_the_year(maturity, year, freq)
        print(f"maturity {maturity}, year {year}, freq {freq}, {coupon_dates}")
        self.assertTrue(len(coupon_dates) == 2)

        maturity = datetime.date(2048, 1, 25)
        freq = 4
        year = 2025
        coupon_dates = get_possible_coupon_dates_in_the_year(maturity, year, freq)
        print(f"maturity {maturity}, year {year}, freq {freq}, {coupon_dates}")
        self.assertTrue(len(coupon_dates) > 2)

    def test_get_possible_coupon_dates_in_specified_years(self):
        from fi_utils.bond_valuation import get_possible_coupon_dates_in_specified_years

        maturity = datetime.date(2048, 9, 25)
        years = [2024, 2025]
        freq = 2
        possible_coupon_dates = get_possible_coupon_dates_in_specified_years(
            maturity, years, freq
        )
        print(
            f"maturity {maturity}, years {years}, freq {freq}, possible coupon dates : {possible_coupon_dates}"
        )
        self.assertTrue(len(possible_coupon_dates) > 2)

    def test_find_prev_coupon_date(self):
        from fi_utils.bond_valuation import find_prev_coupon_date

        maturity = datetime.date(2048, 9, 25)
        adate = datetime.date(2025, 1, 20)
        freq = 2
        prev_cpn_date = find_prev_coupon_date(adate, maturity, freq=2)
        print(
            f"adate {adate}, maturity {maturity}, freq {freq}, prev coupon date : {prev_cpn_date}"
        )
        self.assertEqual(prev_cpn_date.year, adate.year - 1)

    def test_calc_accrued_interest(self):
        from fi_utils.bond_valuation import calc_accrued_interest

        adate = datetime.date(2025, 3, 24)
        maturity = datetime.date(2048, 9, 25)
        freq = 2
        coupon = 4.0
        accrued_interest = calc_accrued_interest(adate, maturity, coupon, freq)
        print(
            f"adate {adate}, maturity {maturity}, coupon {coupon}, freq {freq}, accrued interest : {accrued_interest}"
        )
        self.assertTrue(accrued_interest < coupon)

    def test_find_matching_interval_in_curve(self):
        from fi_utils.bond_valuation import find_matching_interval_in_curve

        curve = {y: 4.0 + y / 100 for y in range(1, 31)}
        interval = find_matching_interval_in_curve(3.4, curve)
        print(interval)
        self.assertTrue(len(interval) > 0)

        interval = find_matching_interval_in_curve(40, curve)
        print(interval)
        self.assertTrue(len(interval) > 0)

    def test_calc_interpolated_rate_from_interval_curve(self):
        from fi_utils.bond_valuation import (
            calc_interpolated_rate_from_interval_curve,
            find_matching_interval_in_curve,
        )

        curve = {y: 4.0 + y / 100 for y in range(1, 31)}
        time_to_cf = 3.4
        interval = find_matching_interval_in_curve(time_to_cf, curve)
        ir = calc_interpolated_rate_from_interval_curve(interval, time_to_cf)
        print(f"time_to_cf : {time_to_cf}, interval : {interval}, ir : {ir}")
        self.assertTrue(ir > 0)

    def test_calc_discount_factor_given_ir_and_time_to_cf(self):
        from fi_utils.bond_valuation import (
            calc_interpolated_rate_from_interval_curve,
            find_matching_interval_in_curve,
            calc_discount_factor_given_ir_and_time_to_cf,
        )

        curve = {y: 4.0 + y / 100 for y in range(1, 31)}
        time_to_cf = 3.4
        interval = find_matching_interval_in_curve(time_to_cf, curve)
        ir = calc_interpolated_rate_from_interval_curve(interval, time_to_cf)
        discount_factor = calc_discount_factor_given_ir_and_time_to_cf(ir, time_to_cf)
        print(
            f"time_to_cf : {time_to_cf}, interval : {interval}, ir : {ir}, discount factor : {discount_factor}"
        )
        self.assertTrue(discount_factor > 0)

    def test_calc_cf_of_vanilla_bond(self):
        from fi_utils.bond_valuation import get_vanilla_bond_cf_and_time_to_cf

        adate = datetime.date(2025, 4, 21)
        maturity = datetime.date(2048, 9, 25)
        coupon = 4.0
        bond_cf = get_vanilla_bond_cf_and_time_to_cf(adate, maturity, coupon)
        print(bond_cf)
        self.assertTrue(len(bond_cf) > 0)


if __name__ == "__main__":
    unittest.main()
