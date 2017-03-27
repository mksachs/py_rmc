import py_rmc.data.models
from py_rmc import rmc

import flask
import sqlalchemy.inspection

import json
import pprint


def add_data(data, model, session):
    compatible_data = {}
    column_names = list(model.__table__.columns.keys())
    for key in data.keys():
        if key in column_names:
            compatible_data[key] = data[key]

    session.add(
        model(**compatible_data)
    )
    session.commit()

    return compatible_data


def list_data(model, session, filters=None):
    return [x.as_dict() for x in session.query(model).all()]


def update_data(object_id, data, model, session):
    compatible_data = {}
    column_names = list(model.__table__.columns.keys())
    for key in data.keys():
        if key in column_names:
            compatible_data[key] = data[key]

    data_object = session.query(model).get(object_id)

    for column_name in compatible_data:
        setattr(data_object, column_name, compatible_data[column_name])

    session.commit()

    return data_object.as_dict()


def delete_data(object_id, model, session):
    data_object = session.query(model).get(object_id)
    data_values = data_object.as_dict()
    session.delete(data_object)
    session.commit()

    return data_values


def get_data(object_id, model, session):
    data_object = session.query(model).get(object_id)

    relationships = sqlalchemy.inspection.inspect(model).relationships

    for r in relationships:

        print(r, type(r), r.mapper)

    return {'obj': data_object.as_dict(), 'rel': relationships}


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

    return {'parent': parent_obj.as_dict(), 'child': child_obj.as_dict()}


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

    return {'parent': parent_obj.as_dict(), 'child': child_obj.as_dict()}


def execute_action(action_name, model, session, in_data=None, object_id=None, parent_id=None, parent_name=None):
    if action_name == 'POST':
        added_data = add_data(in_data, model, session)
        return flask.jsonify(
            {'added_data': added_data}
        )
    elif action_name == 'PATCH':
        updated_data = update_data(
            object_id, in_data, model, flask.g.database
        )
        return flask.jsonify(
            {'updated_data': updated_data}
        )
    elif action_name == 'DELETE':
        deleted_data = delete_data(object_id, model, session)
        return flask.jsonify(
            {'deleted_data': deleted_data}
        )
    elif action_name == 'LINK':
        linked_data = link_data(
            object_id, model, parent_id, parent_name, session
        )
        return flask.jsonify(
            {'linked_data': linked_data}
        )
    elif action_name == 'UNLINK':
        unlinked_data = unlink_data(
            object_id, model, parent_id, parent_name, session
        )
        return flask.jsonify(
            {'unlinked_data': unlinked_data}
        )
    else:
        if object_id is None:
            data_list = list_data(model, session)
            return flask.jsonify(data_list)
        else:
            print(action_name, model, session, in_data, object_id)
            data = get_data(object_id, model, session)
            return flask.jsonify(data)


@rmc.route('/api/v1.0/combatants', methods=['GET', 'POST'])
def combatants():
    return execute_action(
        flask.request.method, py_rmc.data.models.Combatant, flask.g.database, in_data=flask.request.get_json()
    )


@rmc.route('/api/v1.0/combatants/<combatant_id>', methods=['GET', 'PATCH', 'DELETE', 'LINK', 'UNLINK'])
def combatant(combatant_id):
    return execute_action(
        flask.request.method, py_rmc.data.models.Combatant, flask.g.database,
        in_data=flask.request.get_json(),
        object_id=combatant_id,
        parent_id=flask.request.args.get('parent_id'),
        parent_name=flask.request.args.get('parent')
    )


@rmc.route('/api/v1.0/encounters', methods=['GET', 'POST'])
def encounters():
    return execute_action(
        flask.request.method, py_rmc.data.models.Encounter, flask.g.database, in_data=flask.request.get_json()
    )


@rmc.route('/api/v1.0/encounters/<encounter_id>', methods=['GET', 'PATCH', 'DELETE'])
def encounter(encounter_id):
    return execute_action(
        flask.request.method, py_rmc.data.models.Encounter, flask.g.database,
        in_data=flask.request.get_json(),
        object_id=encounter_id
    )


@rmc.route('/api/v1.0/actions', methods=['GET', 'POST'])
def actions():
    if flask.request.method == 'POST':
        # add an action
        pass
    else:
        # list all actions
        pass


@rmc.route('/api/v1.0/actions/<action_id>', methods=['GET', 'PUT', 'DELETE'])
def action(action_id):
    if flask.request.method == 'PUT':
        # update action
        pass
    elif flask.request.method == 'DELETE':
        # delete action
        pass
    else:
        # return action
        pass


@rmc.route('/api/v1.0/attack_types', methods=['GET', 'POST'])
def attack_types():
    if flask.request.method == 'POST':
        # add an attack_type
        pass
    else:
        # list all attack_types
        pass


@rmc.route('/api/v1.0/attack_types/<attack_type_id>', methods=['GET', 'PUT', 'DELETE'])
def attack_type(attack_type_id):
    if flask.request.method == 'PUT':
        # update attack type
        pass
    elif flask.request.method == 'DELETE':
        # delete attack type
        pass
    else:
        # return attack type
        pass


@rmc.route('/api/v1.0/statuses', methods=['GET', 'POST'])
def statuses():
    if flask.request.method == 'POST':
        # add an attack type
        pass
    else:
        # list all attack types
        pass


@rmc.route('/api/v1.0/statuses/<status_id>', methods=['GET', 'PUT', 'DELETE'])
def status(status_id):
    if flask.request.method == 'PUT':
        # update status
        pass
    elif flask.request.method == 'DELETE':
        # delete status
        pass
    else:
        # return status
        pass



# def get_hfd_observations(boa_table, source_ids):
#     """Returns HFD data from the Book of Azathoth.
#
#     Input:
#     boa_table: the name of the Book Of Azathoth table to query
#     source_ids: A list of source ids to query
#
#     Output:
#     Tuple containing the results in the first position and any ids that failed to return results in the second.
#
#     :param boa_table: string
#     :param source_ids: list
#     :return: tuple (dict, dict)
#     """
#     select_event = flask.g.book_of_azathoth.prepare(
#         'select * from {} where source_id = ? order by event_time desc limit 1;'.format(boa_table)
#     )
#
#     ret = {}
#     fail = {}
#     for source_id in source_ids:
#         hfd_obs = flask.g.book_of_azathoth.execute(select_event, [source_id])
#
#         failed = True
#         if hfd_obs is not None:
#             if len(hfd_obs.current_rows) != 0:
#                 obs_res = hfd_obs[0]._asdict()
#                 obs_res['source'] = boa_table.split('_')[0]
#                 ret[source_id] = obs_res
#                 failed = False
#
#         if failed:
#             fail[source_id] = {'source': boa_table.split('_')[0]}
#
#     return ret, fail
#
#
# @ddn_ep.route('/hfd/<input_type>/<hfd_input>')
# def hfd(input_type, hfd_input):
#     """For a given input type and set of source ids returns the HFD observatins from the Book of Azathoth.
#
#     URL form: <server>/hfd/<input_type>/<hfd_input>
#
#     <input_type> is one of: 'yt_id', 'fbv_id', 'video_id'
#     <hfd_input> is either a comma-separated list of source ids for the given input_type, or 'list' or info. 'list'
#     returns a list of all available ids from the Book of Azathoth for input_types 'yt_id' and 'fbv_id' and an error
#     for 'video_id'
#
#     :param input_type: string
#     :param hfd_input: string
#     :return: json
#     """
#     if input_type not in ddn_config.ddn_endpoints['hfd_input_types']:
#         raise ddn_endpoints.exceptions.HFDError(
#             'The input type must be one of {}'.format(
#                 ', '.join(ddn_config.ddn_endpoints['hfd_input_types'])
#             )
#         )
#
#     boa_table = None
#     if input_type == 'yt_id':
#         boa_table = 'yt_data'
#     elif input_type == 'fbv_id':
#         boa_table = 'fbv_data'
#
#     if hfd_input == 'list':
#         if boa_table is not None:
#             statement = cassandra.query.SimpleStatement(
#                 'select distinct source_id from {}'.format(boa_table), fetch_size=100
#             )
#             ret = []
#             for row in flask.g.book_of_azathoth.execute(statement):
#                 ret.append(row.source_id)
#
#             return json.dumps(
#                 {'result_list': ret, 'result_length': len(ret), 'failed': [], 'failed_length': 0},
#                 cls=ddn_endpoints.utilities.DateTimeEncoder
#             )
#         else:
#             raise ddn_endpoints.exceptions.HFDError(
#                 '/list is not a valid path for {}'.format(input_type)
#             )
#     elif hfd_input == 'info':
#         return json.dumps({'info': input_type}, cls=ddn_endpoints.utilities.DateTimeEncoder)
#     else:
#         input_source_ids = hfd_input.split(',')
#         if boa_table is not None:
#             ret, failed = get_hfd_observations(boa_table, input_source_ids)
#             return json.dumps(
#                 {'result_object': ret, 'result_length': len(ret), 'failed': failed, 'failed_length': len(failed)},
#                 cls=ddn_endpoints.utilities.DateTimeEncoder
#             )
#         else:
#             a = flask.g.necronomicon.a_sess
#             video_types = (
#                 a.query(dm.VideoType.id).filter(dm.VideoType.name == 'YT').one()[0],
#                 a.query(dm.VideoType.id).filter(dm.VideoType.name == 'FBV').one()[0]
#             )
#
#             hfd_source_ids = {}
#             found_input_ids = []
#             for source, source_id, video_id in a.query(
#                     dm.VideoType.name, dm.VideoMetaData.value, dm.VideoMetaData.video_id
#             )\
#                     .join(dm.Video, dm.VideoType.id == dm.Video.video_type_id)\
#                     .join(dm.VideoMetaData, dm.Video.id == dm.VideoMetaData.video_id)\
#                     .filter(dm.VideoType.id.in_(video_types))\
#                     .filter(dm.Video.id.in_(input_source_ids))\
#                     .filter(dm.VideoMetaData.name == u'source_id'):
#                 found_input_ids.append(str(video_id))
#                 source_tag = '{}_data'.format(source.lower())
#                 if source_tag not in hfd_source_ids:
#                     hfd_source_ids[source_tag] = [source_id]
#                 else:
#                     hfd_source_ids[source_tag].append(source_id)
#
#             failed = {x: {'source': 'misk'} for x in list(set(input_source_ids) - set(found_input_ids))}
#
#             ret = {}
#             for source_tag in hfd_source_ids:
#                 result, fail = get_hfd_observations(source_tag, hfd_source_ids[source_tag])
#                 failed.update(fail)
#                 ret.update(result)
#
#             return json.dumps(
#                 {
#                     'result_object': ret, 'result_length': len(ret),
#                     'failed': failed, 'failed_length': len(failed)
#                 },
#                 cls=ddn_endpoints.utilities.DateTimeEncoder
#             )
