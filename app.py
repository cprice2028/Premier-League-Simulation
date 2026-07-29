from flask import Flask, render_template
from database import *

app = Flask(__name__)

def setup_database():
    initialize_database()
    add_all_teams()
    create_schedule()
    
if __name__ == "__main__":
    setup_database()
    app.run(debug=True)
