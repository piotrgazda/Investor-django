from collections import defaultdict
import pandas as pd
import pandas_ta as ta

import numpy as np
from django.utils import timezone


def rma(x, n, y0):
    a = (n-1) / n
    ak = a**np.arange(len(x)-1, -1, -1)
    return np.r_[np.full(n, np.nan), y0, np.cumsum(ak * x) / ak / n + y0 * a**np.arange(1, len(x)+1)]


def rsi70(series, n):
    RSI70_CONS = 7/3
    df = pd.DataFrame()
    df['change'] = series.diff()
    df['gain'] = df.change.mask(df.change < 0, 0.0)
    df['loss'] = -df.change.mask(df.change > 0, -0.0)
    df['avg_gain'] = rma(df.gain[n+1:].to_numpy(), n,
                         np.nansum(df.gain.to_numpy()[:n+1])/n)
    df['avg_loss'] = rma(df.loss[n+1:].to_numpy(), n,
                         np.nansum(df.loss.to_numpy()[:n+1])/n)
    df['rsi'] = 100 - (100 / (1 + df['avg_gain']/df['avg_loss']))

    df['gain_to_70'] = (RSI70_CONS*df['avg_loss'] - df['avg_gain'])*n
    return df['gain_to_70']


def rsi30(series, n):
    RSI70_CONS = 7/3
    df = pd.DataFrame()
    df['change'] = series.diff()
    df['gain'] = df.change.mask(df.change < 0, 0.0)
    df['loss'] = -df.change.mask(df.change > 0, -0.0)
    df['avg_gain'] = rma(df.gain[n+1:].to_numpy(), n,
                         np.nansum(df.gain.to_numpy()[:n+1])/n)
    df['avg_loss'] = rma(df.loss[n+1:].to_numpy(), n,
                         np.nansum(df.loss.to_numpy()[:n+1])/n)
    df['loss_to_30'] = (RSI70_CONS*df['avg_gain'] - df['avg_loss'])*n
    return df['loss_to_30']


def sma(series, length):
    return ta.sma(series, length)


def ema(series, length):
    return ta.ema(series, length)


def rsi(series, length):
    return ta.rsi(series, length=length)


def macd(series, fast=12, slow=26):
    return ta.macd(series, fast, slow)


def change_in_time(series, length):
    return series - series.shift(length)


def change_in_time_percentage(series, length):
    return 100*(series - series.shift(length))/series


def summarize_price(investments, add_sold=False):
    results = defaultdict(
        lambda: {'price': 0, 'quantity': 0, 'avg_days_owned': 0})
    for investment in investments:
        company_result = results[investment.company.abbreviation]
        if investment.buy:
            company_result['price'] = (company_result['price']*company_result['quantity']+investment.price *
                                       investment.quantity) / (company_result['quantity']+investment.quantity)

            avg_days = (timezone.now().date() - investment.date).days
            company_result['avg_days_owned'] = (company_result['avg_days_owned']*company_result['quantity'] + avg_days *
                                                investment.quantity) / (company_result['quantity']+investment.quantity)
            company_result['quantity'] += investment.quantity
        else:
            company_result['quantity'] -= investment.quantity

    return results




def returns_on_year_scale(df):
    sum_weights = sum(df['weighted_avg']*df['quantity']*df['avg_days_owned'])
    earned_yearly = df['Earned %'] * 365/df['avg_days_owned']
    yearly_return = (df['weighted_avg'] *
                     df['quantity']*df['avg_days_owned']*earned_yearly)
    total_yearly = sum(yearly_return)/sum_weights
    return total_yearly
