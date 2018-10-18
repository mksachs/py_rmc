import sys
import os
import os.path
import pprint

import sqlalchemy
import sqlalchemy.orm

sys.path.append('./')

import py_rmc.data.models
import py_rmc.views.api


def create_database():
    engine = sqlalchemy.create_engine('sqlite:///database.sqlite3', echo=True)
    py_rmc.data.models.RMCBase.metadata.create_all(engine)


def reset_database():
    if os.path.isfile('database.sqlite3'):
        os.remove('database.sqlite3')
    create_database()


def add_characters():

    engine = sqlalchemy.create_engine('sqlite:///database.sqlite3', echo=True)
    Session = sqlalchemy.orm.sessionmaker(bind=engine)

    session = Session()

    characters = {
        'Alexis': {
            'args': [
                'POST',
                py_rmc.data.models.Combatant,
                session
            ],
            'kwargs': {
                'in_data': {
                    'name': 'Alexis',
                    'type': 'pc',
                    'level': 1,
                    'hit_points': 14,
                    'power_points': 1,
                    'db': 20,
                    'shield_db': 0,
                    'qb': 20,
                    'at': 9,
                }
            }
        },
        'Kirill': {
            'args': [
                'POST',
                py_rmc.data.models.Combatant,
                session
            ],
            'kwargs': {
                'in_data': {
                    'name': 'Kirill',
                    'type': 'pc',
                    'level': 1,
                    'hit_points': 21,
                    'power_points': 3,
                    'db': -5,
                    'shield_db': 20,
                    'qb': 5,
                    'at': 17
                }
            }
        },
        'Grundle': {
            'args': [
                'POST',
                py_rmc.data.models.Combatant,
                session
            ],
            'kwargs': {
                'in_data': {
                    'name': 'Grundle',
                    'type': 'pc',
                    'level': 1,
                    'hit_points': 13,
                    'power_points': 2,
                    'db': 25,
                    'shield_db': 0,
                    'qb': 25,
                    'at': 5,
                }
            }
        },
        'Talion': {
            'args': [
                'POST',
                py_rmc.data.models.Combatant,
                session
            ],
            'kwargs': {
                'in_data': {
                    'name': 'Talion',
                    'type': 'pc',
                    'level': 1,
                    'hit_points': 33,
                    'power_points': 1,
                    'db': 25,
                    'shield_db': 10,
                    'qb': 15,
                    'at': 5
                }
            }
        },
        'Zuuad': {
            'args': [
                'POST',
                py_rmc.data.models.Combatant,
                session
            ],
            'kwargs': {
                'in_data': {
                    'name': 'Zuuad',
                    'type': 'pc',
                    'level': 1,
                    'hit_points': 62,
                    'power_points': 1,
                    'db': 5,
                    'shield_db': 20,
                    'qb': 5,
                    'at': 14,
                }
            }
        },
        'Aravae': {
            'args': [
                'POST',
                py_rmc.data.models.Combatant,
                session
            ],
            'kwargs': {
                'in_data': {
                    'name': 'Aravae',
                    'type': 'pc',
                    'level': 1,
                    'hit_points': 16,
                    'power_points': 2,
                    'db': 25,
                    'shield_db': 0,
                    'qb': 25,
                    'at': 2
                }
            }
        }
    }
    weapons = {
        'Alexis': [
            {
                'args': [
                    'POST',
                    py_rmc.data.models.AttackType,
                    session
                ],
                'kwargs': {
                    'in_data': {
                        'name': 'Ranseur',
                        'ob': 40,
                        'current': True,
                        'hands': 2
                    }
                }
            },
            {
                'args': [
                    'POST',
                    py_rmc.data.models.AttackType,
                    session
                ],
                'kwargs': {
                    'in_data': {
                        'name': 'Dagger (thrown)',
                        'ob': 47,
                        'current': False,
                        'hands': 1
                    }
                }
            }
        ],
        'Kirill': [
            {
                'args': [
                    'POST',
                    py_rmc.data.models.AttackType,
                    session
                ],
                'kwargs': {
                    'in_data': {
                        'name': 'War Hammer',
                        'ob': 41,
                        'current': True,
                        'hands': 1
                    }
                }
            },
            {
                'args': [
                    'POST',
                    py_rmc.data.models.AttackType,
                    session
                ],
                'kwargs': {
                    'in_data': {
                        'name': 'Flail',
                        'ob': 36,
                        'current': False,
                        'hands': 2
                    }
                }
            },
        ],
        'Grundle': [
            {
                'args': [
                    'POST',
                    py_rmc.data.models.AttackType,
                    session
                ],
                'kwargs': {
                    'in_data': {
                        'name': 'Hand Axe (THC)',
                        'ob': 31,
                        'current': True,
                        'hands': 2
                    }
                }
            },
            {
                'args': [
                    'POST',
                    py_rmc.data.models.AttackType,
                    session
                ],
                'kwargs': {
                    'in_data': {
                        'name': 'Light Crossbow',
                        'ob': 26,
                        'current': False,
                        'hands': 2
                    }
                }
            }
        ],
        'Talion': [
            {
                'args': [
                    'POST',
                    py_rmc.data.models.AttackType,
                    session
                ],
                'kwargs': {
                    'in_data': {
                        'name': 'Broadsword (Magic +10)',
                        'ob': 51,
                        'current': True,
                        'hands': 1
                    }
                }
            },
            {
                'args': [
                    'POST',
                    py_rmc.data.models.AttackType,
                    session
                ],
                'kwargs': {
                    'in_data': {
                        'name': 'Composite Bow',
                        'ob': 41,
                        'current': False,
                        'hands': 2
                    }
                }
            },
            {
                'args': [
                    'POST',
                    py_rmc.data.models.AttackType,
                    session
                ],
                'kwargs': {
                    'in_data': {
                        'name': 'Dagger',
                        'ob': 16,
                        'current': False,
                        'hands': 1
                    }
                }
            }
        ],
        'Zuuad': [
            {
                'args': [
                    'POST',
                    py_rmc.data.models.AttackType,
                    session
                ],
                'kwargs': {
                    'in_data': {
                        'name': 'Mace',
                        'ob': 66,
                        'current': True,
                        'hands': 1
                    }
                }
            },
            {
                'args': [
                    'POST',
                    py_rmc.data.models.AttackType,
                    session
                ],
                'kwargs': {
                    'in_data': {
                        'name': 'Light Crossbow',
                        'ob': 40,
                        'current': False,
                        'hands': 2
                    }
                }
            }
        ],
        'Aravae': [
            {
                'args': [
                    'POST',
                    py_rmc.data.models.AttackType,
                    session
                ],
                'kwargs': {
                    'in_data': {
                        'name': 'Dagger (Thrown)',
                        'ob': 55,
                        'current': True,
                        'hands': 1
                    }
                }
            }
        ]
    }

    for character_name in characters:
        print('Adding {}'.format(character_name))
        result = py_rmc.views.api.execute_action(
            *characters[character_name]['args'], **characters[character_name]['kwargs']
        )
        characters[character_name]['id'] = result['obj']['id']

    for character_name in weapons:
        print('Adding {}\'s weapons'.format(character_name))
        for weapon in weapons[character_name]:
            result = py_rmc.views.api.execute_action(
                *weapon['args'], **weapon['kwargs']
            )
            weapon['id'] = result['obj']['id']

    for character_name in weapons:
        print('Linking {}\'s weapons'.format(character_name))
        for weapon in weapons[character_name]:
            result = py_rmc.views.api.execute_action(
                'LINK',
                py_rmc.data.models.AttackType,
                session,
                object_id=weapon['id'],
                parent_id=characters[character_name]['id'],
                parent_name='combatant'
            )


if __name__ == "__main__":

    reset_database()
    add_characters()


