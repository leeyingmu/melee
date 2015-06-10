# -*- coding: utf-8 -*-

from flask import Flask, Blueprint, request, g, json, jsonify, after_this_request
from ..core import config

class MeleeApp(object):

    def __init__(self, import_name):
        self.import_name = import_name
        self.app = Flask(import_name)
