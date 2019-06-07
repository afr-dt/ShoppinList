import os
from flask import Flask
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from flask_graphql import GraphQLView
from flask_cors import CORS

from db import db
from dotenv import load_dotenv
from os.path import join, dirname
# Create .env file connection to PostgreSQL 🐘
dotenv_path = join(dirname(__file__), '.env')
# Load file from the path
load_dotenv(dotenv_path)

app = Flask(__name__)
CORS(app)
app.debug = True

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL_PSQL', '')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '715b5b41a2lfa2bd00003e67996912y8'

db.init_app(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@app.route('/')
def index():
    return '<h2> GraphQL Server ⚛️ 🌚 </h2>'


if __name__ == '__main__':
    from schema import schema
    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view(
            'graphql',
            schema=schema,
            graphiql=True
        )
    )
    manager.run()
