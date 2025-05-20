from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from sqlalchemy import CheckConstraint

db = SQLAlchemy()

# Configuración mejorada para PostgreSQL en Render
if os.environ.get('RENDER', '').lower() == 'true' or os.environ.get('DATABASE_URL'):
    metadata = db.MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s"
        }
    )
    db = SQLAlchemy(metadata=metadata)

class Saldo(db.Model):
    __tablename__ = 'saldos'
    id = db.Column(db.Integer, primary_key=True)
    metodo_pago = db.Column(db.String(20), unique=True, nullable=False)
    saldo = db.Column(db.Float, nullable=False, default=0.0)
    monto_inicial = db.Column(db.Float, nullable=False, default=0.0)
    
    __table_args__ = (
        CheckConstraint('saldo >= 0', name='check_saldo_positivo'),
    )

class Venta(db.Model):
    __tablename__ = 'ventas'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    monto = db.Column(db.Float, nullable=False)
    metodo_pago = db.Column(db.String(20), nullable=False)
    
    __table_args__ = (
        CheckConstraint('monto > 0', name='check_monto_positivo_venta'),
    )

class Gasto(db.Model):
    __tablename__ = 'gastos'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    metodo_pago = db.Column(db.String(20), nullable=False)
    
    __table_args__ = (
        CheckConstraint('monto > 0', name='check_monto_positivo_gasto'),
    )

class Transferencia(db.Model):
    __tablename__ = 'transferencias'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    metodo_origen = db.Column(db.String(20), nullable=False)
    metodo_destino = db.Column(db.String(20), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    
    __table_args__ = (
        CheckConstraint('monto > 0', name='check_monto_positivo_transferencia'),
        CheckConstraint('metodo_origen != metodo_destino', name='check_origen_destino_diferentes'),
    )

class ROA(db.Model):
    __tablename__ = 'roa_analytics'
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10), nullable=False)  # 'diario', 'semanal', 'mensual'
    periodo = db.Column(db.String(20), nullable=False, unique=True)
    total_ventas = db.Column(db.Float, default=0.0)
    activo_total = db.Column(db.Float, default=0.0)
    roa = db.Column(db.Float, default=0.0)
    fecha_calculo = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_roa_periodo', 'tipo', 'periodo', unique=True),
        CheckConstraint('total_ventas >= 0', name='check_ventas_positivas'),
        CheckConstraint('activo_total >= 0', name='check_activo_positivo'),
    )   