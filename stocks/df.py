from stocks import models
import pandas as pd
import stocks.indicators as indicators
import numpy as np
from stocks.models import UserFollowedCompanies


def companys_indicators_table(user):
    abbreviation_column = 'company__abbreviation'
    companys = UserFollowedCompanies.objects.user_followed_companies(
        user).values(abbreviation_column)
    prices = models.Price.objects.far_days_first_by_companies(
        companys).values(abbreviation_column, 'closing')
    df = pd.DataFrame(prices)
    if not df.empty:
        df['Weekly %'] = df.groupby(abbreviation_column)[
            'closing'].transform(lambda x: indicators.change_in_time_percentage(x, 5).round(2))
        df['SMA50'] = df.groupby(abbreviation_column)['closing'].transform(
            lambda x: indicators.sma(x, length=50).round(2))
        df['EMA50'] = df.groupby(abbreviation_column)['closing'].transform(
            lambda x: indicators.ema(x, length=50).round(2))
        df['RSI14'] = df.groupby(abbreviation_column)['closing'].transform(
            lambda x: indicators.rsi(x, length=14).round(2))
        df['MACD'] = df.groupby(abbreviation_column)[
            'closing'].transform(lambda x: indicators.macd(x).round(2).iloc[:, 0])

        df = df.drop_duplicates(subset=[abbreviation_column], keep='last')
        df = df.sort_values(by='RSI14')
        df.rename(inplace=True, columns={
            'closing': 'Price', abbreviation_column: 'Company'})
    return df


def weighted_average(df, group, value, weight, name='weighted_avg'):
    return df.groupby(group).apply(
        lambda x: np.average(x[value], weights=x[weight])).rename(name)


def get_money_from_sells(user):
    company_column = 'company__abbreviation'
    user_investments = models.UserStockTransactions.objects.filter(
        user=user).values(company_column, 'quantity', 'price', 'buy')
    df = pd.DataFrame(user_investments)
    if df.empty:
        return df
    df = df.merge(weighted_average(
        df, [company_column, 'buy'], 'price', 'quantity').reset_index(), on=[company_column, 'buy'])
    df.loc[~df['buy'], 'quantity'] = -1*df['quantity']
    has_sell = df[df['quantity'] < 0][company_column]
    sells_df = df[df[company_column].isin(has_sell)].groupby(
        [company_column, 'buy']).apply(lambda x: x.quantity*x['weighted_avg'])
    sells_df = sells_df.reset_index()
    sells_df['summed'] = sells_df.groupby(company_column)[
        0].transform('sum')
    earned_on_sells_dollars = -1 * sells_df['summed'].sum()/2
    return earned_on_sells_dollars


def user_portfolio_df(user, exchange_rate=None):
    company_column = 'company__abbreviation'
    user_investments = models.UserStockTransactions.objects.filter(
        user=user).order_by('date')
    df = pd.DataFrame(indicators.summarize_price(
        user_investments)).transpose().reset_index()
    if not df.empty:
        df = df[df['quantity'] > 0]
        df = df.rename(
            columns={'index': company_column, 'price': 'weighted_avg'})
        df = df.astype({'quantity': 'int64'})
        df = df[[company_column, 'quantity', 'weighted_avg', 'avg_days_owned']]
        if df.empty:
            return pd.DataFrame()
        current_company_prices = models.Price.objects.recent_days_first_by_companies(
            df[company_column]).values(company_column, 'closing')
        current_prices = pd.DataFrame(current_company_prices).drop_duplicates(
            subset=[company_column])
        df = df.merge(current_prices, on=company_column)
        df['Earned'] = (df['closing']-df['weighted_avg'])*df['quantity']
        df['Earned %'] = 100*df['Earned']/(df['weighted_avg']*df['quantity'])
        output_columns = ['Company', 'Quantity', 'Avg price', 'Days owned',
                          'Current price', 'Earned', 'Earned %']
        if exchange_rate:
            df['Main currency'] = df['Earned']*exchange_rate
            output_columns.append('User currency')
        df.columns = output_columns
        df = df.sort_values(by='Earned', ascending=False)
    return df


def add_delete_button(df, column, function_name='deleteItem'):
    df[column] = r'<button class="btn btn-danger center" style="width: 100%" onclick="' + \
        function_name+r'(event)"><b>X</b></button>'
    return df


class PortfolioDataFrame(pd.DataFrame):
    def __init__(self, user, exchange_rate=None) -> None:
        super().__init__(user_portfolio_df(user, exchange_rate))

    def footer(self, exchange_rate):
        total_value = sum(self['Quantity']*self['Current price'])
        total_earned = sum(self['Earned'])
        total_earned_local = total_earned * exchange_rate
        return f'Total value: {total_value:.2f}$ , total earned in: {total_earned:.2f}$, in local {total_earned_local:.2f}'

    def worth(self):
        return sum(self['Quantity']*self['Current price'])
