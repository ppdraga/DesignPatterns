import abc
from datetime import datetime
from settings import POLICY

class TabularSection():
    def __init__(self):
        self.lines = []

    def insert(self, number, line):
        self.lines.insert(number, line)

    def add(self, line):
        self.lines.append(line)

    def clear(self):
        self.lines.clear()

    def delete(self, line):
        self.lines.pop(line)


class PurchaseInvoiceTabSec(TabularSection):
    pass

class SalesInvoiceTabSec(TabularSection):
    pass

class TabularSectionFabric:
    DOC_TYPE_1 = 'PurchaseInvoice'
    DOC_TYPE_2 = 'SalesInvoice'

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

class Catalog:
    def __init__(self, id=None, name=None, description=None):
        self.id = id
        self.name = name
        self.description = description
    

class Nomenclature(Catalog):
    def __str__(self):
        return f'{self.name} (id {self.id})'
    def __repr__(self):
        return f'{self.name} (id {self.id})'


class Document(metaclass=abc.ABCMeta):
    id = None
    date = None
    nomTabSec = None
    registerRecords = []
    
    @abc.abstractmethod
    def post(self):
        pass

    def unpost(self):
        for record in self.registerRecords:
            NomenclatureAccReg.rows.remove(record)
        self.registerRecords = []
        self.posted = False

    def save(self, posting=True):
        if posting:
            self.unpost()
            self.post()

    def __str__(self):
        lines = ''
        for line in self.nomTabSec.lines:
            lines += str(line) + '\n'
        return f'Doc # {self.id} date {self.date}\n{lines}'

class PurcaseInvoice(Document):
    def __init__(self, id=None, num=None):
        self.id = id
        self.num = num
        self.date = datetime.now()
        self.posted = False
        self.nomTabSec = PurchaseInvoiceTabSec()
        self.registerRecords = []

    def post(self):
        for line in self.nomTabSec.lines:
            record = NomenclatureAccReg()
            record.period = self.date
            record.reg_type = self.__class__.__name__
            record.reg_id = self.id
            record.part = self.id
            record.action = 1 # income
            record.lineNum = line.get('lineNum')
            record.nomenclature = line.get('nomenclature')
            record.count = line.get('count')
            record.sum = line.get('sum')
            self.registerRecords.append(record)
        self.posted = True      

class SalesInvoice(Document):
    def __init__(self, id=None, num=None):
        self.id = id
        self.num = num
        self.date = datetime.now()
        self.posted = False
        self.nomTabSec = SalesInvoiceTabSec()
        self.registerRecords = []

    def post(self):
        line_counter = 0
        cancel = False
        recordSet = []
        for line in self.nomTabSec.lines:
            remain = line.get('count')
            if remain:
                nomenclature = line.get('nomenclature')
                parties = NomenclatureAccReg.get_balance(selection={'nomenclature_id':nomenclature.id})
                for part in parties:
                    if part.get('count') < remain:
                        _sum = part.get('sum')
                        count = part.get('count')
                        remain -= count
                    else:
                        count = remain
                        _sum = part.get('sum')*count/part.get('count')
                        remain = 0
                    
                    record = NomenclatureAccReg()
                    line_counter+=1
                    record.period = self.date
                    record.reg_type = self.__class__.__name__
                    record.reg_id = self.id
                    record.part = part.get('part')
                    record.action = 0 # expense
                    record.lineNum = line_counter
                    record.nomenclature = nomenclature
                    record.count = count
                    record.sum = _sum
                    recordSet.append(record)
                    if not remain: break
            if remain:
                print(f'Not enough {remain} of {nomenclature}')
                cancel = True
        if not cancel:
            self.registerRecords.extend(recordSet)
            self.posted = True
        else:
            for record in recordSet:
                NomenclatureAccReg.rows.remove(record)

class AccumulationRegister:
    pass

class NomenclatureAccReg(AccumulationRegister):
    rows = []
    def __init__(self):
        __class__.rows.append(self)
    def __repr__(self):
        action = 'income' if self.action else 'expese'
        return f'\nPeriod: {self.period}, Registrator: {self.reg_type},{self.reg_id}, Part: {self.part}, Action: {action}, line: {self.lineNum}, nomecluture: {self.nomenclature}, count: {self.count}, sum: {self.sum}'
    
    @staticmethod
    def get_balance(date=datetime(1,1,1),selection={}):
        '''setection = {'nomenclature_id': Nomenclature.id, 'part':{}}'''
        parties = []
        for row in __class__.rows:
            if row.period >= date and row.nomenclature.id == selection.get('nomenclature_id'):
                parties.append(row.part)
        parties = list(set(parties))
        res = []
        for part in parties:
            part_balance = {'part':part, 'count': 0, 'sum': 0, 'period':datetime(1,1,1)}
            for row in __class__.rows:
                if row.period >= date and row.nomenclature.id == selection.get('nomenclature_id') and row.part == part:
                    if row.action == 1:
                        part_balance['count'] += row.count
                        part_balance['sum'] += row.sum
                        part_balance['period'] = row.period
                    else:
                        part_balance['count'] -= row.count
                        part_balance['sum'] -= row.sum
            if part_balance['count']: res.append(part_balance)
        reverse = POLICY == 'LIFO'
        res = sorted(res, key=lambda elem:elem['period']-datetime(1,1,1), reverse=reverse)
        return res

