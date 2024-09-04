import csv

from scrapy.exporters import CsvItemExporter


class QuoteNonNumericDialect(csv.excel):
    quoting = csv.QUOTE_NONNUMERIC


class CsvCustomSeperator(CsvItemExporter):
    def __init__(self, *args, **kwargs):
        kwargs['encoding'] = 'utf-8'
        kwargs['delimiter'] = ';'
        kwargs['quotechar'] = '"'
        kwargs['dialect'] = QuoteNonNumericDialect
        super(CsvCustomSeperator, self).__init__(*args, **kwargs)

# settings.py
# FEED_EXPORT_ENCODING = "utf-8"
# FEED_EXPORTERS = {
#     'csv': 'oliveyoung.exporters.CsvCustomSeperator'
# }
