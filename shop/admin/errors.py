
from flask import jsonify
from . import *

@admin.app_errorhandler(500)
def server_error(_):
    return jsonify({"message": "Its not you it's us"}), 500


@admin.app_errorhandler(404)
def not_found(_):
    return jsonify({"message": "Not found"}), 404