import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm


RMCBase = sqlalchemy.ext.declarative.declarative_base()

combatants_attack_types = sqlalchemy.Table(
    'combatants_attack_types',
    RMCBase.metadata,
    sqlalchemy.Column(
        'combatant_id',
        sqlalchemy.INTEGER,
        sqlalchemy.ForeignKey('combatants.id')
    ),
    sqlalchemy.Column(
        'attack_type_id',
        sqlalchemy.INTEGER,
        sqlalchemy.ForeignKey('attack_types.id')
    )
)

combatants_encounters = sqlalchemy.Table(
    'combatants_encounters',
    RMCBase.metadata,
    sqlalchemy.Column(
        'combatant_id',
        sqlalchemy.INTEGER,
        sqlalchemy.ForeignKey('combatants.id')
    ),
    sqlalchemy.Column(
        'encounter_id',
        sqlalchemy.INTEGER,
        sqlalchemy.ForeignKey('encounters.id')
    )
)


class Encounter(RMCBase):
    __tablename__ = 'encounters'

    id = sqlalchemy.Column(sqlalchemy.INTEGER, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.Unicode(1024))

    # M - N Parent
    combatants = sqlalchemy.orm.relationship(
        'Combatant',
        secondary=combatants_encounters,
        backref='encounters'
    )

    # 1 - N Parent
    actions = sqlalchemy.orm.relationship(
        'Action',
        backref='encounter',
        cascade='all, delete, delete-orphan',
    )

    updated = sqlalchemy.Column(
        sqlalchemy.DateTime, server_default=sqlalchemy.func.now(), onupdate=sqlalchemy.func.current_timestamp()
    )

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Action(RMCBase):
    __tablename__ = 'actions'

    id = sqlalchemy.Column(sqlalchemy.INTEGER, primary_key=True)

    results = sqlalchemy.Column(sqlalchemy.Unicode(1024))

    # 1 - N Child
    attacker_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        # sqlalchemy.ForeignKey('combatants.id')
    )

    # 1 - N Child
    defender_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        # sqlalchemy.ForeignKey('combatants.id')
    )

    # 1 - N Child
    encounter_id = sqlalchemy.Column(
        sqlalchemy.INTEGER,
        sqlalchemy.ForeignKey('encounters.id')
    )

    updated = sqlalchemy.Column(
        sqlalchemy.DateTime, server_default=sqlalchemy.func.now(), onupdate=sqlalchemy.func.current_timestamp()
    )

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Combatant(RMCBase):
    __tablename__ = 'combatants'

    types = ['pc', 'monster', 'npc']

    id = sqlalchemy.Column(sqlalchemy.INTEGER, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.Unicode(1024))
    type = sqlalchemy.Column(sqlalchemy.Enum(*types))

    level = sqlalchemy.Column(sqlalchemy.INTEGER)
    hit_points = sqlalchemy.Column(sqlalchemy.INTEGER)
    db = sqlalchemy.Column(sqlalchemy.INTEGER)
    qb = sqlalchemy.Column(sqlalchemy.INTEGER)

    # 1 - N Parent
    statuses = sqlalchemy.orm.relationship(
        'Status',
        backref='combatant',
        cascade='all, delete, delete-orphan',
    )

    # # 1 - N Parent
    # attacks_made = sqlalchemy.orm.relationship(
    #     'Action',
    #     backref='attacker',
    #     # cascade='all, delete, delete-orphan',
    # )
    #
    # # 1 - N Parent
    # attacks_defended = sqlalchemy.orm.relationship(
    #     'Action',
    #     backref='defender',
    #     # cascade='all, delete, delete-orphan',
    # )

    # M - N Parent
    attack_types = sqlalchemy.orm.relationship(
        'AttackType',
        secondary=combatants_attack_types,
        backref='combatants'
    )

    updated = sqlalchemy.Column(
        sqlalchemy.DateTime, server_default=sqlalchemy.func.now(), onupdate=sqlalchemy.func.current_timestamp()
    )

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return 'combatant'


class AttackType(RMCBase):
    __tablename__ = 'attack_types'

    id = sqlalchemy.Column(sqlalchemy.INTEGER, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.Unicode(1024))
    ob = sqlalchemy.Column(sqlalchemy.INTEGER)

    updated = sqlalchemy.Column(
        sqlalchemy.DateTime, server_default=sqlalchemy.func.now(), onupdate=sqlalchemy.func.current_timestamp()
    )

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Status(RMCBase):
    __tablename__ = 'statuses'

    id = sqlalchemy.Column(sqlalchemy.INTEGER, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.Enum(
        *[
            'bleeding',
            'at',
            'must parry',
            'stunned',
            'stunned no parry',
            'down',
            'out'
        ]
    ))
    ob_mod = sqlalchemy.Column(sqlalchemy.INTEGER)
    db_mod = sqlalchemy.Column(sqlalchemy.INTEGER)
    duration = sqlalchemy.Column(sqlalchemy.INTEGER)
    precedence = sqlalchemy.Column(sqlalchemy.Enum(
        *[
            'None',
            '0',
            '1',
            '2',
            '3',
            '4'
        ]
    ))

    # 1 - N Child
    combatant_id = sqlalchemy.Column(
        sqlalchemy.INTEGER,
        sqlalchemy.ForeignKey('combatants.id')
    )

    updated = sqlalchemy.Column(
        sqlalchemy.DateTime, server_default=sqlalchemy.func.now(), onupdate=sqlalchemy.func.current_timestamp()
    )

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}