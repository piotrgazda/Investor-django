from django.utils.safestring import mark_safe
import pandas as pd
from django.template.loader import render_to_string

from authentication.models import UserProfile
from stocks import indicators
from stocks.data.currency import get_or_set_cached_exchange_rate
from stocks.models import Price


def money_balance(portfolio_value, spent, earned, template_name='stocks/money-balance.html'):
    return render_to_string(template_name, context={'portfolio_value': portfolio_value,
                                                    'spent': spent,
                                                    'earned': earned,
                                                    'balance': portfolio_value-spent+earned})


def render_currencies_rates(user):
    currency_summary_template = 'stocks/currency-summary.html'
    main_currency = UserProfile.objects.filter(
        user=user.pk).first().currency
    to_convert = ['USD', 'EUR']
    currencies = []
    for currency in to_convert:
        currencies.append(
            (currency, get_or_set_cached_exchange_rate(currency, main_currency)))
    return render_to_string(currency_summary_template, context={'currencies': currencies})


def render_company_card(abbreviation):
    ordered = Price.objects.far_days_first(
        abbreviation=abbreviation).values('closing')
    df = pd.DataFrame(ordered)
    simple_average = indicators.sma(df['closing'], length=50).round(2).iloc[-1]
    exp_average = indicators.ema(df['closing'], 50).round(2).iloc[-1]
    rsi = indicators.rsi(df['closing'], 14).round(2).iloc[-1]
    return render_to_string('stocks/company-card.html', context={'company_abbreviation': abbreviation, 'sma': simple_average,
                                                                 'ema': exp_average, 'rsi': rsi})


def render_chart(datasets, labels):
    return render_to_string('stocks/company-chart.html', context={'datasets': datasets, 'labels': labels})


def render_table(df, template_name='table.html', title=None, include_headers=True, footer=None):
    pd.options.display.float_format = '{:,.2f}'.format
    return render_to_string(template_name=template_name, context={'dataframe': df.to_html(index=False, header=include_headers, escape=False, border=0, justify='left', classes=['darktable']),
                                                                  'title': title, 'footer': footer})


def style_based_on_condition(df, condition, if_true, if_false):
    return df.applymap(
        lambda x: if_true(x) if condition(x) else if_false(x))


def style_positive_negative(df):
    df = df.astype(str)
    positive_prefix = '<div class="positive">'
    negative_prefix = '<div class="negative">'
    postfix = '</div>'
    return style_based_on_condition(df, lambda x: x[0] != '-', lambda x: mark_safe(positive_prefix+x+postfix), lambda x: mark_safe(negative_prefix+x+postfix))
