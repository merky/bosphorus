"""empty message

Revision ID: 2eb74d81b686
Revises: 10af3f929eb8
Create Date: 2014-08-01 14:02:55.701450

"""

# revision identifiers, used by Alembic.
revision = '2eb74d81b686'
down_revision = '10af3f929eb8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('person', sa.Column('notes', sa.String(length=1024), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('person', 'notes')
    ### end Alembic commands ###
