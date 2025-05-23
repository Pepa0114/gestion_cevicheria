"""Migración inicial

Revision ID: cc7d82daa43e
Revises: 
Create Date: 2025-05-19 23:45:00.153058

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc7d82daa43e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('gastos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fecha', sa.DateTime(), nullable=False),
    sa.Column('categoria', sa.String(length=50), nullable=False),
    sa.Column('monto', sa.Float(), nullable=False),
    sa.Column('metodo_pago', sa.String(length=20), nullable=False),
    sa.CheckConstraint('monto > 0', name=op.f('ck_gastos_check_monto_positivo_gasto')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_gastos'))
    )
    op.create_table('roa_analytics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tipo', sa.String(length=10), nullable=False),
    sa.Column('periodo', sa.String(length=20), nullable=False),
    sa.Column('total_ventas', sa.Float(), nullable=True),
    sa.Column('activo_total', sa.Float(), nullable=True),
    sa.Column('roa', sa.Float(), nullable=True),
    sa.Column('fecha_calculo', sa.DateTime(), nullable=True),
    sa.CheckConstraint('activo_total >= 0', name=op.f('ck_roa_analytics_check_activo_positivo')),
    sa.CheckConstraint('total_ventas >= 0', name=op.f('ck_roa_analytics_check_ventas_positivas')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_roa_analytics')),
    sa.UniqueConstraint('periodo', name=op.f('uq_roa_analytics_periodo'))
    )
    with op.batch_alter_table('roa_analytics', schema=None) as batch_op:
        batch_op.create_index('idx_roa_periodo', ['tipo', 'periodo'], unique=True)

    op.create_table('saldos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('metodo_pago', sa.String(length=20), nullable=False),
    sa.Column('saldo', sa.Float(), nullable=False),
    sa.Column('monto_inicial', sa.Float(), nullable=False),
    sa.CheckConstraint('saldo >= 0', name=op.f('ck_saldos_check_saldo_positivo')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_saldos')),
    sa.UniqueConstraint('metodo_pago', name=op.f('uq_saldos_metodo_pago'))
    )
    op.create_table('transferencias',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fecha', sa.DateTime(), nullable=False),
    sa.Column('metodo_origen', sa.String(length=20), nullable=False),
    sa.Column('metodo_destino', sa.String(length=20), nullable=False),
    sa.Column('monto', sa.Float(), nullable=False),
    sa.CheckConstraint('metodo_origen != metodo_destino', name=op.f('ck_transferencias_check_origen_destino_diferentes')),
    sa.CheckConstraint('monto > 0', name=op.f('ck_transferencias_check_monto_positivo_transferencia')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_transferencias'))
    )
    op.create_table('ventas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fecha', sa.DateTime(), nullable=False),
    sa.Column('monto', sa.Float(), nullable=False),
    sa.Column('metodo_pago', sa.String(length=20), nullable=False),
    sa.CheckConstraint('monto > 0', name=op.f('ck_ventas_check_monto_positivo_venta')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_ventas'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ventas')
    op.drop_table('transferencias')
    op.drop_table('saldos')
    with op.batch_alter_table('roa_analytics', schema=None) as batch_op:
        batch_op.drop_index('idx_roa_periodo')

    op.drop_table('roa_analytics')
    op.drop_table('gastos')
    # ### end Alembic commands ###
