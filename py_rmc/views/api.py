import py_rmc.data.models
from py_rmc import rmc

import flask
import sqlalchemy.inspection

import json
import pprint


def add_data(data, model, session, children=False):
    compatible_data = {}
    column_names = list(model.__table__.columns.keys())
    for key in data.keys():
        if key in column_names:
            compatible_data[key] = data[key]

    data_object = model(**compatible_data)
    session.add(data_object)
    session.commit()

    relationships = None
    if children:
        relationships = get_children(data_object, model)

    return data_object.as_dict(), relationships


def list_data(model, session, filters=None, children=False):
    ret_list = []
    for object in session.query(model).all():
        object_dict = object.as_dict()
        if children:
            relationships = get_children(object, model)
            object_dict['children'] = relationships
        ret_list.append(object_dict)

    return ret_list


def update_data(object_id, data, model, session, children=False):
    compatible_data = {}
    column_names = list(model.__table__.columns.keys())
    for key in data.keys():
        if key in column_names:
            compatible_data[key] = data[key]

    data_object = session.query(model).get(object_id)

    for column_name in compatible_data:
        setattr(data_object, column_name, compatible_data[column_name])

    session.commit()

    relationships = None
    if children:
        relationships = get_children(data_object, model)

    return data_object.as_dict(), relationships


def delete_data(object_id, model, session):
    data_object = session.query(model).get(object_id)
    data_values = data_object.as_dict()
    session.delete(data_object)
    session.commit()

    return data_values


def get_children(obj, model):
    relationships = sqlalchemy.inspection.inspect(model).relationships

    ret_relationships = {}
    for r in relationships:
        r_name = str(r.class_attribute).split('.')[-1]
        ret_relationships[r_name] = []
        data_object_relationships = getattr(obj, r_name)
        for related_data in data_object_relationships:
            ret_relationships[r_name].append(related_data.as_dict())

    return ret_relationships


def get_data(object_id, model, session, children=True):
    data_object = session.query(model).get(object_id)

    relationships = None
    if children:
        relationships = get_children(data_object, model)

    return data_object.as_dict(), relationships


def link_data(child_id, child_model, parent_id, parent_name, session):
    child_obj = session.query(child_model).get(child_id)
    if parent_name == 'encounter':
        parent_model = py_rmc.data.models.Encounter
        if child_model is py_rmc.data.models.Combatant:
            link_prop = 'combatants'
        elif child_model is py_rmc.data.models.Action:
            link_prop = 'actions'
    elif parent_name == 'combatant':
        parent_model = py_rmc.data.models.Combatant
        if child_model is py_rmc.data.models.Status:
            link_prop = 'statuses'
        elif child_model is py_rmc.data.models.AttackType:
            link_prop = 'attack_types'

    parent_obj = session.query(parent_model).get(parent_id)

    link = getattr(parent_obj, link_prop)
    link.append(child_obj)
    session.commit()

    return parent_obj.as_dict(), child_obj.as_dict()


def unlink_data(child_id, child_model, parent_id, parent_name, session):
    child_obj = session.query(child_model).get(child_id)
    if parent_name == 'encounter':
        parent_model = py_rmc.data.models.Encounter
        if child_model is py_rmc.data.models.Combatant:
            link_prop = 'combatants'
        elif child_model is py_rmc.data.models.Action:
            link_prop = 'actions'
    elif parent_name == 'combatant':
        parent_model = py_rmc.data.models.Combatant
        if child_model is py_rmc.data.models.Status:
            link_prop = 'statuses'
        elif child_model is py_rmc.data.models.AttackType:
            link_prop = 'attack_types'

    parent_obj = session.query(parent_model).get(parent_id)

    link = getattr(parent_obj, link_prop)
    link.remove(child_obj)
    session.commit()

    return parent_obj.as_dict(), child_obj.as_dict()


def execute_action(
        action_name, model, session, in_data=None, object_id=None, parent_id=None, parent_name=None, children=False
):
    results = {}
    if action_name == 'POST':
        obj, children = add_data(
            in_data, model, session, children=children
        )
        results['obj'] = obj
        results['children'] = children
    elif action_name == 'PATCH':
        obj, children = update_data(
            object_id, in_data, model, flask.g.database, children=children
        )
        results['obj'] = obj
        results['children'] = children
    elif action_name == 'DELETE':
        obj = delete_data(
            object_id, model, session
        )
        results['obj'] = obj
        results['children'] = None
    elif action_name == 'LINK':
        obj, child = link_data(
            object_id, model, parent_id, parent_name, session
        )
        results['obj'] = obj
        results['child'] = child
    elif action_name == 'UNLINK':
        obj, child = unlink_data(
            object_id, model, parent_id, parent_name, session
        )
        results['obj'] = obj
        results['child'] = child
    else:
        if object_id is None:
            objs = list_data(model, session, children=children)
            results['list'] = objs
        else:
            obj, children = get_data(object_id, model, session, children=children)
            results['obj'] = obj
            results['children'] = children

    results['action'] = action_name

    if flask.has_app_context():
        return flask.jsonify(results)
    else:
        return results


@rmc.route('/api/v1.0/combatants', methods=['GET', 'POST'])
def combatants():
    children = flask.request.args.get('children')
    if children is None:
        children = False
    return execute_action(
        flask.request.method, py_rmc.data.models.Combatant, flask.g.database,
        in_data=flask.request.get_json(), children=children
    )


@rmc.route('/api/v1.0/combatants/<combatant_id>', methods=['GET', 'PATCH', 'DELETE', 'LINK', 'UNLINK'])
def combatant(combatant_id):
    children = flask.request.args.get('children')
    if children is None:
        children = False
    return execute_action(
        flask.request.method, py_rmc.data.models.Combatant, flask.g.database,
        in_data=flask.request.get_json(),
        object_id=combatant_id,
        parent_id=flask.request.args.get('parent_id'),
        parent_name=flask.request.args.get('parent'),
        children=children
    )


@rmc.route('/api/v1.0/encounters', methods=['GET', 'POST'])
def encounters():
    children = flask.request.args.get('children')
    if children is None:
        children = False
    return execute_action(
        flask.request.method, py_rmc.data.models.Encounter, flask.g.database,
        in_data=flask.request.get_json(), children=children
    )


@rmc.route('/api/v1.0/encounters/<encounter_id>', methods=['GET', 'PATCH', 'DELETE'])
def encounter(encounter_id):
    children = flask.request.args.get('children')
    if children is None:
        children = False
    return execute_action(
        flask.request.method, py_rmc.data.models.Encounter, flask.g.database,
        in_data=flask.request.get_json(),
        object_id=encounter_id,
        children=children
    )


@rmc.route('/api/v1.0/actions', methods=['GET', 'POST'])
def actions():
    return execute_action(
        flask.request.method, py_rmc.data.models.Action, flask.g.database, in_data=flask.request.get_json()
    )


@rmc.route('/api/v1.0/actions/<action_id>', methods=['GET', 'PATCH', 'DELETE', 'LINK', 'UNLINK'])
def action(action_id):
    return execute_action(
        flask.request.method, py_rmc.data.models.Action, flask.g.database,
        in_data=flask.request.get_json(),
        object_id=action_id,
        parent_id=flask.request.args.get('parent_id'),
        parent_name=flask.request.args.get('parent')
    )


@rmc.route('/api/v1.0/attack_types', methods=['GET', 'POST'])
def attack_types():
    return execute_action(
        flask.request.method, py_rmc.data.models.AttackType, flask.g.database, in_data=flask.request.get_json()
    )


@rmc.route('/api/v1.0/attack_types/<attack_type_id>', methods=['GET', 'PATCH', 'DELETE', 'LINK', 'UNLINK'])
def attack_type(attack_type_id):
    return execute_action(
        flask.request.method, py_rmc.data.models.AttackType, flask.g.database,
        in_data=flask.request.get_json(),
        object_id=attack_type_id,
        parent_id=flask.request.args.get('parent_id'),
        parent_name=flask.request.args.get('parent')
    )


@rmc.route('/api/v1.0/statuses', methods=['GET', 'POST'])
def statuses():
    return execute_action(
        flask.request.method, py_rmc.data.models.AttackType, flask.g.database, in_data=flask.request.get_json()
    )


@rmc.route('/api/v1.0/statuses/<status_id>', methods=['GET', 'PATCH', 'DELETE', 'LINK', 'UNLINK'])
def status(status_id):
    return execute_action(
        flask.request.method, py_rmc.data.models.Status, flask.g.database,
        in_data=flask.request.get_json(),
        object_id=status_id,
        parent_id=flask.request.args.get('parent_id'),
        parent_name=flask.request.args.get('parent')
    )
