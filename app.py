from flask import Flask, render_template
from database import initialize_database

app = Flask(__name__)

if __name__ == "__main__":
    app.run(debug=True)
