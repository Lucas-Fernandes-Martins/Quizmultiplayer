from app.app import app

from app.app import db

if(__name__ == "__main__"):
    db.drop_all()
    db.create_all()
    app.run()