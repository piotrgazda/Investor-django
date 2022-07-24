from django.http import Http404, HttpResponse
from django.shortcuts import render
from stocks.data import importerbridges, downloaders, importers
from stocks.data.scappers import StatementScrapperFactory, ZacksEarningsSummaryScrapper, ZacksStatementScrapper
from utils import fading_sections
from stocks.renders import render_table
from stocks.data.currency import get_or_set_cached_exchange_rate
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from stocks.df import PortfolioDataFrame, companys_indicators_table, add_delete_button
from django.http import HttpResponse
from stocks.models import UserStockTransactions, Company, Price
from stocks.renders import render_currencies_rates, render_chart, money_balance, render_company_card


@login_required
def homepage(request):
    render_context = {}
    render_context['currencies'] = render_currencies_rates(request.user)
    spent = UserStockTransactions.objects.money_spent_on_buys(request.user)
    earned = UserStockTransactions.objects.money_earned_on_sells(request.user)
    df = companys_indicators_table(request.user)
    df = add_delete_button(df, 'Unfollow')
    exchange_rate = get_or_set_cached_exchange_rate('USD', 'PLN')
    portfolio = PortfolioDataFrame(request.user, exchange_rate)
    if portfolio.empty:
        return render(request=request, template_name='stocks/summary.html', context=render_context)
    render_context['balance'] = money_balance(
        portfolio.worth(), spent, earned)
    footer = portfolio.footer(exchange_rate)
    render_context['portfolio'] = render_table(
        portfolio, title='Portfolio', footer=footer)
    render_context['companys'] = render_table(
        df, title='Followed companys')
    return render(request=request, template_name='stocks/summary.html', context=render_context)


@login_required
def refresh_data(request):
    downloader = downloaders.YahooPriceDownloader()
    bridge = importerbridges.YahooPriceBridge()
    for company in Company.objects.active():
        importer = importers.ImporterStocks(Price)
        importer.import_data(
            downloader=downloader, bridge=bridge, company=company)
    return HttpResponse('Success!')


@login_required
def financials(request, company):
    PERIOD = 'annual'
    STATEMENT_CATEGORIES = ('income', 'balance', 'cash')
    scrapper = StatementScrapperFactory().get_scrapper('zacks')
    statements = [scrapper.get_statements(
        company, statement_type, PERIOD) for statement_type in STATEMENT_CATEGORIES]
    rendered_statements = [
        ''.join([render_table(table) for table in tables]) for tables in statements]
    return HttpResponse(fading_sections(rendered_statements, STATEMENT_CATEGORIES))


@login_required
def company_stock_summary(request, company):
    abbreviation = company.upper()
    company = Company.objects.filter(abbreviation=abbreviation).first()
    if not company:
        raise Company.DoesNotExist(abbreviation + ' does not exist in db')
    data, labels = company.rsi_price_datasets()
    chart = render_chart(data, labels)
    card = render_company_card(company.abbreviation)
    earnings_info = []
    if not '.' in abbreviation:
        scrapper = ZacksEarningsSummaryScrapper()
        scrapped = scrapper.get_summary(abbreviation)
        earnings_info.append(render_table(scrapped[0], include_headers=False))
        earnings_info.append(render_table(scrapped[1], include_headers=False))
        earnings_info.append(render_table(scrapped[2], include_headers=True))
    return render(request, template_name='stocks/company-summary.html', context={'card': card,
                                                                                 'chart': chart, 'earnings_info': earnings_info})
