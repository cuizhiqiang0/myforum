from flask import Blueprint
brother = Blueprint('brother', __name__)
from . import views