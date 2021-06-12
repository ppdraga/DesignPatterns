from datetime import datetime
from flask import Flask, render_template, jsonify, request

from applib import Nomenclature, PurcaseInvoice, SalesInvoice, NomenclatureAccReg

app = Flask(__name__)

# Data initialization:

pen1 = Nomenclature()
pen1.id = 0
pen1.name = 'Pen Parker'

pen2 = Nomenclature()
pen2.id = 1
pen2.name = 'Pen Senator'
# print(pen2)

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

# print('NomenclatureAccReg:')
# print(NomenclatureAccReg.rows)

print('pen1 balance:')
print(NomenclatureAccReg.get_balance(selection={'nomenclature_id':pen1.id}))

# print('doc4 register records:')
# print(doc4.registerRecords)

import sqlite3
from dbmapper import NomenclatureMapper

connection = sqlite3.connect('db.sqlite3')
nomenclature_mapper = NomenclatureMapper(connection)
# nomenclature_mapper.insert(pen1)
# nomenclature_mapper.insert(pen2)
# pen = nomenclature_mapper.find_by_id(5)
# pen.description = 'test'
# nomenclature_mapper.update(pen)
# pen = nomenclature_mapper.find_by_id(7)
# nomenclature_mapper.delete(pen)
pens = nomenclature_mapper.fetchall()
# print(pens)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/api")
def api():
    data_args = {}
    data = {}
    for key in request.args.keys():
        data_args[key] = request.args.get(key)
    product_id = data_args.get('product_id', None)
    if product_id is None or not product_id.isdigit():
        return jsonify({'message': 'Failed'}), 404
    detal_data = NomenclatureAccReg.get_balance(selection={'nomenclature_id':int(product_id)})
    if data_args.get('detal', '0') == '1':
        data = detal_data
    else:
        data['product_id'] = product_id
        count = 0
        for elem in detal_data:
            count += elem.get('count', 0)
        data['count'] = count
    return jsonify({'message': 'Success', 'data': data}), 200

@app.route("/api/products", methods=['GET', 'POST'])
def products_handler():
    if request.method == 'GET':
        data = []
        connection = sqlite3.connect('db.sqlite3')
        nomenclature_mapper = NomenclatureMapper(connection)
        products = nomenclature_mapper.fetchall()
        for product_obj in products:
            product = {}
            product['id'] = product_obj.id
            product['name'] = product_obj.name
            product['description'] = product_obj.description
            data.append(product)
        return jsonify({'message': 'Success', 'data': data}), 200
    if request.method == 'POST':
        data = request.get_json()
        connection = sqlite3.connect('db.sqlite3')
        nomenclature_mapper = NomenclatureMapper(connection)
        product = nomenclature_mapper.find_by_id(data.get('id'))
        if product:
            product.name = data.get('name')
            product.description = data.get('description')
            nomenclature_mapper.update(product)
        else:
            nomenclature_mapper.insert(Nomenclature(**product))
        return jsonify({'message': 'Success', 'data': data}), 200

if __name__ == '__main__':
    app.run(debug=True)