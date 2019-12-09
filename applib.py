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
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name
        self.desc = None
    

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
                parties = NomenclatureAccReg.get_balance(selection={'nomenclature':nomenclature})
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
        '''setection = {'nomenclature': Nomenclature, 'part':{}}'''
        parties = []
        for row in __class__.rows:
            if row.period >= date and row.nomenclature == selection.get('nomenclature'):
                parties.append(row.part)
        parties = list(set(parties))
        res = []
        for part in parties:
            part_balance = {'part':part, 'count': 0, 'sum': 0, 'period':datetime(1,1,1)}
            for row in __class__.rows:
                if row.period >= date and row.nomenclature == selection.get('nomenclature') and row.part == part:
                    if row.action == 1:
                        part_balance['count'] += row.count
                        part_balance['sum'] += row.sum
                        part_balance['period'] = row.period
                    else:
                        part_balance['count'] -= row.count
                        part_balance['sum'] -= row.sum
            if part_balance['count']: res.append(part_balance)
        reverse = True if POLICY == 'LIFO' else False
        res = sorted(res, key=lambda elem:elem['period']-datetime(1,1,1), reverse=reverse)
        return res

if __name__ == '__main__':
    pen1 = Nomenclature()
    pen1.id = 0
    pen1.name = 'Pen Parker'

    pen2 = Nomenclature()
    pen2.id = 1
    pen2.name = 'Pen Senator'
    print(pen2)

    doc1 = PurcaseInvoice()
    doc1.id = 0
    doc1.num = '00001'
    doc1.date = datetime(2019,11,15,12,0,0)
    doc1.nomTabSec.add({'lineNum':1,'nomenclature':pen1,'count':5,'sum':500})  # pen1 costs $100
    doc1.nomTabSec.add({'lineNum':2,'nomenclature':pen2,'count':3,'sum':450})  # pen2 costs $150
    doc1.post()

    doc2 = PurcaseInvoice()
    doc2.id = 1
    doc2.num = '00002'
    doc2.date = datetime(2019,11,20,12,0,0)
    doc2.nomTabSec.add({'lineNum':1,'nomenclature':pen1,'count':2,'sum':400})  # pen1 costs $200
    doc2.nomTabSec.add({'lineNum':2,'nomenclature':pen2,'count':1,'sum':200})  # pen2 costs $200
    doc2.post()

    doc3 = PurcaseInvoice()
    doc3.id = 2
    doc3.num = '00003'
    doc3.date = datetime(2019,11,30,12,0,0)
    doc3.nomTabSec.add({'lineNum':1,'nomenclature':pen1,'count':10,'sum':500})  # pen1 costs $50
    doc3.nomTabSec.add({'lineNum':2,'nomenclature':pen2,'count':4,'sum':1000})  # pen2 costs $200
    doc3.post()
    

    doc4 = SalesInvoice()
    doc4.id = 0
    doc4.num = '00001'
    doc4.date = datetime(2019,12,1,12,0,0)
    doc4.nomTabSec.add({'lineNum':1,'nomenclature':pen1,'count':6,'sum':1500})  # FIFO costs $700, LIFO costs $300
    doc4.nomTabSec.add({'lineNum':2,'nomenclature':pen2,'count':5,'sum':2500})  # FIFO costs $900, LIFO costs $1200
    doc4.post()

    print('NomenclatureAccReg:')
    print(NomenclatureAccReg.rows)
    print('pen1 balance:')
    print(NomenclatureAccReg.get_balance(selection={'nomenclature':pen1}))
    print('doc4 register records:')
    print(doc4.registerRecords)