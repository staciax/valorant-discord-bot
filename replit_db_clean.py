from replit import db

for _ in db.keys():
    del db[_]
