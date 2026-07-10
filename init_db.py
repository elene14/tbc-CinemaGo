from ext import db, app
import models

with app.app_context():
    db.drop_all()
    db.create_all()
    print("base has been created")

# db.init_app(app)
