#! usr/bin/python
from app import app, db
from app.models import User, Character
app.run(debug=True)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Character': Character}