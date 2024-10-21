from tinydb import TinyDB, Query


db = TinyDB('db.json')


db.insert({'a': 3, 'b': 4})
print(db.get())