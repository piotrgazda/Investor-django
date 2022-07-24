from abc import ABC, abstractmethod
import pandas_datareader as pdr


class PriceDownloader(ABC):
    @abstractmethod
    def get_price(company_abbreviation):
        pass


class YahooPriceDownloader(PriceDownloader):
    def get_price(self,company_abbreviation):
        return pdr.get_data_yahoo(company_abbreviation)

