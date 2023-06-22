from flask_restx import Namespace, Resource, reqparse, fields
from flask import request, url_for, redirect
import datetime
import json
from common.entities.person import PersonEntity

from common.google_credentials import get_credentials
from common.entity_store import EntityStore
pns = Namespace('Persons', description='services manage Person Entity metadata')
pmodel = pns.model('Person', {})

@pns.route('/')
class Persons(Resource):
    ''' '''
    @pns.doc('get person entities')
    def get(self):
        # storage will return a list of PersonEntity objects
        person_storage = EntityStore(PersonEntity)
        # get_list() returns a list of PersonEntity instances, which are just Dicts
        # these will automatically be serialized to JSON by the flask framework
        return person_storage.list_items()
    
    @pns.doc('create or update a person entity')
    @pns.expect(pmodel)
    def post(self):
        person_storage = EntityStore(PersonEntity)        
        pe = PersonEntity(request.get_json())
        person_storage.upsert_item(pe)
        return { 'id': pe[pe.key_field] }, 201

@pns.route('/<ids>')
@pns.param('ids', 'comma-separated list of person ids')
class Person(Resource):
    def get(self, ids):
        person_storage = EntityStore(PersonEntity)
        return [ person_storage.get_item(id) for id in ids.split(',') ]

    @pns.doc('delete a person')
    def delete(self, ids):
        person_storage = EntityStore(PersonEntity)        
        id_list = ids.split(',')
        person_storage.delete(id_list)
        return { 'result': id_list }, 204
    