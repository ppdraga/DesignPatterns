import abc

class TabularSection():
    def __init__(self):
        self.lines = []

    def insert(self, number, line):
        self.lines.insert(number, line)

    def add(self, line):
        self.lines.append(number, line)

    def clear(self):
        self.lines.clear()

    def delete(self, line):
        self.lines.pop(line)


class PurchaseInvoiceTabSec(TabularSection):
    pass

class SalesInvoiceTabSec(TabularSection):
    pass

class TabularSectionFabric:
    DOC_TYPE_1 = 'Purchase'
    DOC_TYPE_2 = 'Sales'

    @staticmethod
    def create_tabsec(name):
        if name == __class__.DOC_TYPE_1:
            return PurchaseTabSecFactory()
        elif name == __class__.DOC_TYPE_2:
            return SalesTabSecFactory()
        else:
            return None

class PurchaseTabSecFactory:
    def create(self):
        return PurchaseInvoiceTabSec()

class SalesTabSecFactory:
    def create(self):
        return SalesInvoiceTabSec()

