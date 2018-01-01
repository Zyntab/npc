from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
character = Table('character', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('id_users', Integer),
    Column('timestamp', DateTime),
    Column('start_values', String(length=200)),
    Column('weights', String(length=300)),
    Column('traits', String(length=420)),
    Column('points_left', Integer),
    Column('skills', String(length=700)),
    Column('hitpoints', String(length=350)),
    Column('move_carry', String(length=200)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['character'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['character'].drop()
