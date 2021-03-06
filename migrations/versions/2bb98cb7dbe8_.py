"""empty message

Revision ID: 2bb98cb7dbe8
Revises: 1729e25c1270
Create Date: 2014-08-08 19:23:34.577741

"""

# revision identifiers, used by Alembic.
revision = '2bb98cb7dbe8'
down_revision = '1729e25c1270'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('research_protocols',
    sa.Column('person_id', sa.Integer(), nullable=True),
    sa.Column('protocol_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['person_id'], ['person.id'], ),
    sa.ForeignKeyConstraint(['protocol_id'], ['research_protocol.id'], )
    )
    op.drop_column(u'person', u'protocol_id')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column(u'person', sa.Column(u'protocol_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_table('research_protocols')
    ### end Alembic commands ###
