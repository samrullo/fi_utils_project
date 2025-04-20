import datetime
from scipy.optimize import fsolve
import logging
import calendar


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
    this_year_coupon_date = datetime.date(adate.year, maturity.month, maturity.day)
    possible_coupon_dates_in_the_year = [this_year_coupon_date]

    # keep on subtracting days_per_year/freq days to find list of previous coupon dates in the year
    possible_coupon_date = this_year_coupon_date
    while possible_coupon_date.year == adate.year:
        possible_coupon_date = set_the_day_of_the_date(
            possible_coupon_date - datetime.timedelta(days=days_per_year / freq),
            maturity.day,
        )
        if possible_coupon_date.year == adate.year:
            possible_coupon_dates_in_the_year.append(possible_coupon_date)

    # keep on adding days_per_year/freq days to find list of upcoming coupon dates in the year
    possible_coupon_date = this_year_coupon_date
    while possible_coupon_date.year == adate.year:
        possible_coupon_date = set_the_day_of_the_date(
            possible_coupon_date + datetime.timedelta(days=days_per_year / freq),
            maturity.day,
        )
        if possible_coupon_date.year == adate.year:
            possible_coupon_dates_in_the_year.append(possible_coupon_date)

    # sort coupon dates in the year in ascending order
    possible_coupon_dates_in_the_year = sorted(possible_coupon_dates_in_the_year)
    possible_coupon_dates_adate_diff_list = [
        (thedate - adate).days for thedate in possible_coupon_dates_in_the_year
    ]

    # next coupon dates from as of date are those where possible coupon date minus adate is non-negative
    next_coupon_dates_in_the_year = [
        thedate
        for idx, thedate in enumerate(possible_coupon_dates_in_the_year)
        if possible_coupon_dates_adate_diff_list[idx] >= 0
    ]

    # next coupon date is the first item in the next coupon dates list
    return next_coupon_dates_in_the_year[0]


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


from scipy.optimize import fsolve
import numpy as np


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
        return (
            price
            - calculate_pv_from_ytm(
                ytm, coupon_rate, adate, maturity, days_per_year, freq, principal_amount
            )
        ) ** 2

    solved_ytm = fsolve(objective_func, np.array(1))
    return float(solved_ytm[0])
