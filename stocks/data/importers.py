from abc import ABC, abstractmethod


class Importer(ABC):
    def __init__(self, model):
        self.model = model

    def import_to_db(self, models):
        self.model.objects.bulk_create(models, ignore_conflicts=True)

    @abstractmethod
    def import_data(self, downloader, bridge, company):
        pass


class ImporterStocks(Importer):

    def import_data(self, downloader, bridge, company):
        data = downloader.get_price(company.abbreviation)
        data = bridge.bridge(data)
        data['company_id'] = company.pk
        models = [self.model(**row) for row in data.to_dict(orient='records')]
        self.import_to_db(models)
