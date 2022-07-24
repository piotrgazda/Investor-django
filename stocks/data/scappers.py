from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import re
import requests

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'close',
    'DNT': '1',
    'Pragma': 'no-cache',
    'Referrer': 'https://google.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
}


def rename_unnamed_columns_to_empty(df):
    if 'Unnamed: 0' in df.columns:
        return df.rename(columns={'Unnamed: 0': ''})
    else:
        return df


class StatementScrapperFactory():

    def get_scrapper(self, source):
        if source == 'zacks':
            return ZacksStatementScrapper()
        return None


class StatementScrapper(ABC):

    STATEMENT_CATEGORIES = ('income', 'balance', 'cash')
    STATEMENT_PERIODS = ('annual', 'quaterly')

    @abstractmethod
    def get_statements(self, company, category, period):
        pass


class ZacksStatementScrapper(StatementScrapper):
    __URL = 'https://www.zacks.com/stock/quote/{company}/{sheet_category}/'

    SECTION_SELECTORS = ('#income_statements_tabs',
                         '#income_statements_tabs', '.quote_body_full')

    SHEET_TYPES = ('income-statement',
                   'balance-sheet',
                   'cash-flow-statements')
    CUTOFF = 3

    def __init__(self) -> None:
        self.sheet_mapping = {key: value for key, value in zip(
            self.STATEMENT_CATEGORIES, self.SHEET_TYPES)}
        self.section_selectors_mapping = {key: value for key, value in zip(
            self.STATEMENT_CATEGORIES, self.SECTION_SELECTORS)}

    def get_statements(self, company, category, period):
        if category == 'cash' and period == 'quaterly':
            raise NotImplementedError(
                'Quaterly cash statement is not available for zacks!')
        sheet_category = self.sheet_mapping[category]
        section_selector = self.section_selectors_mapping[category]
        url = self.__URL.format(company=company, sheet_category=sheet_category)
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, features='lxml')
        scrapped = soup.select(section_selector + ' table')
        all_tables = [rename_unnamed_columns_to_empty(
            pd.read_html(str(scrap))[0]).dropna() for scrap in scrapped]
        if period == 'annual':
            return all_tables[:self.CUTOFF]
        elif period == 'quaterly':
            return all_tables[self.CUTOFF:]
        else:
            raise ValueError(period + ' not one of [annual, quaterly]')


class ZacksEarningsSummaryScrapper():
    __URL = 'https://www.zacks.com/stock/quote/{company}/detailed-earning-estimates'

    def get_summary(self, company):
        url = self.__URL.format(company=company)
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, features='lxml')
        scrapped = soup.find(id='detailed_estimate').findAll('table')

        dfs = [pd.read_html(str(table))[0] for table in scrapped]
        for df in dfs:
            df.iloc[:, 0] = df.iloc[:, 0].str.split('More Info').str[0]
        self.reformat_date(dfs[0])
        return dfs

    def reformat_date(self, df):
        read_date = re.findall('\d+/\d+/\d+', df.iloc[0, 1])[0]
        date_format = '%M/%d/%y'
        date = datetime.strptime(
            read_date, date_format)
        reformatted = date.strftime('%Y-%M-%d')
        df.iloc[0, 1] = reformatted
