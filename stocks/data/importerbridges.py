from abc import ABC, abstractmethod


class DownloadDbBridge(ABC):
    @abstractmethod
    def bridge(self, data):
        pass


class YahooPriceBridge(DownloadDbBridge):
    FIELD_MAPPING = {'Open': 'opening',
                     'Close': 'closing', 'Date': 'date'}

    def bridge(self, data):
        return data.reset_index().rename(columns=self.FIELD_MAPPING)[list(self.FIELD_MAPPING.values())]
