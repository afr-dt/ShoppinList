import os
from flask import Flask
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from flask_graphql import GraphqQLView
from flask_cors import CORS

from db import db
