import datetime


def compute_linear_amortization_schedule(
    initial_book_price: float,
    maturity: datetime.date,
    purchase_date: datetime.date,
    period_length_years: float,
    par: float = 100.0,
):
    """
    Calculate total number of periods till maturity and linear change per period in book price.

    :param initial_book_price: Book price at purchase time.
    :param maturity: Maturity date of the bond.
    :param purchase_date: Purchase date or stress test starting date.
    :param period_length_years: Length of one period (e.g., 0.5 for semiannual).
    :param par: Par value of the bond (default 100).
    :return: (total_periods: int, change_per_period: float)
    """
    total_years = (maturity - purchase_date).days / 365.0
    total_periods = int(total_years / period_length_years)

    if total_periods <= 0:
        raise ValueError(
            "Bond is at or past maturity or period_length_years is too large."
        )

    change_per_period = (par - initial_book_price) / total_periods

    return total_periods, change_per_period
