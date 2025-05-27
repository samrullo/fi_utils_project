import datetime
from scipy.optimize import fsolve
import logging
import calendar
from typing import List
import numpy as np


def fix_february_date(thedate: datetime.date):
    if thedate.month == 2 and thedate.day > 28:
        thedate = datetime.date(thedate.year, thedate.month, 28)
    return thedate


def set_the_day_of_the_date(adate: datetime.date, day: int):
    try:
        return datetime.date(adate.year, adate.month, day)
    except ValueError as e:
        logging.info(
            f"breached month days range for the month {adate} with days {day}: {e}"
        )
        _, max_day = calendar.monthrange(adate.year, adate.month)
        return datetime.date(adate.year, adate.month, max_day)


def get_possible_coupon_dates_in_specified_years(
        maturity: datetime.date,
        specified_years: List[int],
        freq: int = 2,
        days_per_year: int = 365,
) -> List[datetime.date]:
    """
    Get possible coupon dates in the year
    :param maturity:
    :param specified_years:
    :param freq:
    :param days_per_year:
    :return:
    """
    specified_years = sorted(specified_years)
    this_year_coupon_date = datetime.date(
        specified_years[-1], maturity.month, maturity.day
    )
    possible_coupon_dates_in_specified_years = [this_year_coupon_date]

    # keep on subtracting days_per_year/freq days to find list of previous coupon dates in the year
    possible_coupon_date = this_year_coupon_date
    while possible_coupon_date.year in specified_years:
        possible_coupon_date = set_the_day_of_the_date(
            possible_coupon_date - datetime.timedelta(days=days_per_year / freq),
            maturity.day,
        )
        if possible_coupon_date.year in specified_years:
            possible_coupon_dates_in_specified_years.append(possible_coupon_date)

    # keep on adding days_per_year/freq days to find list of upcoming coupon dates in the year
    possible_coupon_date = this_year_coupon_date
    while possible_coupon_date.year in specified_years:
        possible_coupon_date = set_the_day_of_the_date(
            possible_coupon_date + datetime.timedelta(days=days_per_year / freq),
            maturity.day,
        )
        if possible_coupon_date.year in specified_years:
            possible_coupon_dates_in_specified_years.append(possible_coupon_date)

    # sort coupon dates in the year in ascending order
    possible_coupon_dates_in_specified_years = sorted(
        possible_coupon_dates_in_specified_years
    )
    return possible_coupon_dates_in_specified_years


def get_possible_coupon_dates_in_the_year(
        maturity: datetime.date, year: int, freq: int = 2, days_per_year: int = 365
) -> List[datetime.date]:
    """
    Get possible coupon dates in the year
    :param maturity:
    :param year:
    :param freq:
    :param days_per_year:
    :return:
    """
    return get_possible_coupon_dates_in_specified_years(
        maturity, [year], freq, days_per_year
    )


def get_next_coupon_dates_in_the_year(
        adate: datetime.date,
        maturity: datetime.date,
        freq: int = 2,
        days_per_year: int = 365,
) -> List[datetime.date]:
    """
    Get the list of next coupon dates that falls in the year of adate
    :param adate:
    :param maturity:
    :param freq:
    :param days_per_year:
    :return:
    """
    possible_coupon_dates_in_the_year = get_possible_coupon_dates_in_the_year(
        maturity, adate.year, freq=freq, days_per_year=days_per_year
    )
    possible_coupon_dates_adate_diff_list = [
        (thedate - adate).days for thedate in possible_coupon_dates_in_the_year
    ]

    # next coupon dates from as of date are those where possible coupon date minus adate is non-negative
    return [
        thedate
        for idx, thedate in enumerate(possible_coupon_dates_in_the_year)
        if possible_coupon_dates_adate_diff_list[idx] >= 0
    ]


def find_next_coupon_date(
        adate: datetime.date,
        maturity: datetime.date,
        freq: int = 2,
        days_per_year: int = 365,
) -> datetime.date:
    """
    Find next coupon date given as of date, maturity date
    :param adate:
    :param maturity:
    :param freq:
    :param days_per_year:
    :return:
    """
    next_coupon_dates_in_the_year = get_next_coupon_dates_in_the_year(
        adate, maturity, freq, days_per_year
    )
    # next coupon date is the first item in the next coupon dates list
    if len(next_coupon_dates_in_the_year) == 0:
        # this means all coupon dates of this year has already passed
        # adate comes after all coupon dates within this year
        # so we need to search next coupon date within next year
        next_coupon_dates_in_the_year = get_next_coupon_dates_in_the_year(
            datetime.date(adate.year + 1, 1, 1), maturity, freq, days_per_year
        )
    return next_coupon_dates_in_the_year[0]


def find_prev_coupon_date(
        adate: datetime.date,
        maturity: datetime.date,
        freq: int = 2,
        days_per_year: int = 365,
) -> datetime.date:
    """
    Find previous coupon date given as of date and maturity
    :param adate:
    :param maturity:
    :param freq:
    :param days_per_year:
    :return:
    """
    years_in_scope = [adate.year, adate.year - 1]
    possible_coupon_dates_in_the_year = get_possible_coupon_dates_in_specified_years(
        maturity, years_in_scope, freq=freq, days_per_year=days_per_year
    )
    possible_coupon_dates_adate_diff_list = [
        (thedate - adate).days for thedate in possible_coupon_dates_in_the_year
    ]

    # previous coupon dates from as of date are those where possible coupon date minus adate is non-positive
    prev_coupon_dates_in_the_year = [
        thedate
        for idx, thedate in enumerate(possible_coupon_dates_in_the_year)
        if possible_coupon_dates_adate_diff_list[idx] <= 0
    ]
    return prev_coupon_dates_in_the_year[-1]


def get_no_of_cf_periods(
        beginning_date: datetime.date,
        ending_date: datetime.date,
        freq: int = 2,
        days_per_year: int = 365,
) -> int:
    return int((ending_date - beginning_date).days / days_per_year * freq) + 1


def get_vanilla_bond_cf_and_time_to_cf(
        adate: datetime.date,
        maturity: datetime.date,
        coupon: float,
        freq: int = 2,
        days_per_year: int = 365,
        principal: float = 100.0,
):
    """
    Get mapping between time to cashflows and cashflows for vanilla bond.
    Vanilla bond usually pays coupons semiannually till maturity and pays down the whole principal on maturity
    :param adate: as of date
    :param maturity: maturity
    :param coupon:
    :param freq:
    :param days_per_year:
    :param principal:
    :return:
    """
    next_cpn_date = find_next_coupon_date(adate, maturity, freq, days_per_year)
    no_of_periods = get_no_of_cf_periods(next_cpn_date, maturity, freq, days_per_year)
    time_to_next_cpn = (next_cpn_date - adate).days / days_per_year
    time_to_cashflows = {
        time_to_next_cpn + p / freq: coupon / freq for p in range(no_of_periods)
    }
    time_to_cashflows[max(time_to_cashflows)] += principal
    return time_to_cashflows


def calculate_pv_from_ytm(
        ytm: float,
        coupon_rate: float,
        adate: datetime.date,
        maturity: datetime.date,
        days_per_year: int = 365,
        freq: int = 2,
        principal_amount: float = 100.0,
) -> float:
    """
    Calculate present value given yield to maturity, coupon rate, as of date, maturity and coupon frequency
    :param ytm: yield to maturity in percentages
    :param coupon_rate: coupon rate in percentages
    :param adate: as of date
    :param maturity:
    :param days_per_year:
    :param freq: coupon frequency
    :param principal_amount:
    :return:
    """
    next_cpn_date = find_next_coupon_date(adate, maturity, freq, days_per_year)
    no_of_periods = int((maturity - next_cpn_date).days / days_per_year * freq)
    time_to_next_cpn_date = (next_cpn_date - adate).days / days_per_year
    pv = (coupon_rate / freq) / (1 + ytm / 100) ** time_to_next_cpn_date
    for period in range(1, no_of_periods + 1):
        pv += (coupon_rate / 2) / (1 + ytm / 100) ** (
                time_to_next_cpn_date + period / freq
        )
    pv += principal_amount / (1 + ytm / 100) ** (
            time_to_next_cpn_date + no_of_periods / freq
    )
    return pv


def calc_ytm_of_bond(
        price: float,
        coupon_rate: float,
        adate: datetime.date,
        maturity: datetime.date,
        days_per_year: int = 365,
        freq: int = 2,
        principal_amount: float = 100,
):
    def objective_func(ytm: np.ndarray):
        ytm = float(ytm)
        pv = calculate_pv_from_ytm(
            ytm, coupon_rate, adate, maturity, days_per_year, freq, principal_amount
        )
        if isinstance(pv, complex):
            raise ValueError(
                f"calc_pv_from_ytm returned complex number for ytm : {ytm}, adate {adate},coupon_rate {coupon_rate}, maturity {maturity} -> {pv}")
        return (price - pv) ** 2

    solved_ytm = fsolve(objective_func, np.array(1))
    return float(solved_ytm[0])


def calc_accrued_interest(
        adate: datetime.date,
        maturity: datetime.date,
        coupon: float,
        freq: int = 2,
        days_per_year: int = 365,
):
    """
    Calculate accrued interest given as of date, maturity, coupon and coupon frequency
    :param adate:
    :param maturity:
    :param coupon:
    :param freq:
    :param days_per_year:
    :return:
    """
    prev_coupon_date = find_prev_coupon_date(adate, maturity, freq, days_per_year)
    days_since_prev_coupon_date = (adate - prev_coupon_date).days
    time_since_prev_coupon_date = days_since_prev_coupon_date / days_per_year
    return coupon * time_since_prev_coupon_date


from typing import Dict


def find_matching_interval_in_curve(time_to_cf: float, curve: Dict[float, float]):
    """
    Given time to the cashflow in years find the matching interval within the curve. Curve is the dictionary
    that maps years to their corresponding interest rates.
    :param time_to_cf:
    :param curve:
    :return:
    """
    years = sorted(curve)
    time_to_cf_years_diff = [y - time_to_cf for y in years]
    negative_time_to_cf_years = [i for i in time_to_cf_years_diff if i < 0]
    nonnegative_time_to_cf_years = [i for i in time_to_cf_years_diff if i >= 0]
    if len(negative_time_to_cf_years) == 0:
        negative_time_to_cf_years = [time_to_cf_years_diff[0]]
    if len(nonnegative_time_to_cf_years) == 0:
        nonnegative_time_to_cf_years = [time_to_cf_years_diff[-1]]
    right_year_idx = time_to_cf_years_diff.index(nonnegative_time_to_cf_years[0])
    right_year = years[right_year_idx]
    left_year_idx = time_to_cf_years_diff.index(negative_time_to_cf_years[-1])
    left_year = years[left_year_idx]
    return {left_year: curve[left_year], right_year: curve[right_year]}


def calc_interpolated_rate_from_interval_curve(
        interval_curve: Dict[float, float], time_to_cf: float
) -> float:
    if len(interval_curve) == 1:
        ir = interval_curve[list(interval_curve)[0]]
    else:
        (left_year, left_ir), (right_year, right_ir) = interval_curve.items()
        slope = (right_ir - left_ir) / (right_year - left_year)

        # right_ir=slope*right_year+b
        b = right_ir - slope * right_year
        ir = time_to_cf * slope + b
    return ir


def calc_discount_factor_given_ir_and_time_to_cf(ir: float, time_to_cf: float) -> float:
    """
    Calculate discount factor given annual interest rate and time to cashflow in years
    :param ir: annual interest rate
    :param time_to_cf: time to cashflow in years
    :return:
    """
    return 1 / (1 + ir / 100) ** time_to_cf


def calc_pv_of_vanilla_bond(
        adate: datetime.date,
        maturity: datetime.date,
        coupon: float,
        curve: Dict[float, float],
        freq: int = 2,
        days_per_year: int = 365,
) -> float:
    """
    Calculate PV of vanilla bond
    :param adate: analysis date
    :param maturity: bond maturity
    :param coupon: vanilla bond annual coupon rate
    :param curve: interest rate curve, this is a dictionary that maps interest rates to time
    :param freq: coupon frequency
    :param days_per_year: days per year
    :return:
    """
    bond_cf = get_vanilla_bond_cf_and_time_to_cf(
        adate, maturity, coupon, freq, days_per_year
    )
    pv = 0
    for time_to_cf, cf in bond_cf.items():
        matching_interval = find_matching_interval_in_curve(time_to_cf, curve)
        ir = calc_interpolated_rate_from_interval_curve(matching_interval, time_to_cf)
        dfactor = calc_discount_factor_given_ir_and_time_to_cf(ir, time_to_cf)
        pv += cf * dfactor
    return pv
