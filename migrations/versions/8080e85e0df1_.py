"""empty message

Revision ID: 8080e85e0df1
Revises: 
Create Date: 2023-01-29 20:10:26.233708

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8080e85e0df1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.add_column(sa.Column('banned', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.drop_column('banned')

    # ### end Alembic commands ###