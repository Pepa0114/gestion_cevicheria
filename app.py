from flask import Flask, render_template, redirect, url_for, flash
from models import db, Saldo, Venta, Gasto, Transferencia
from forms import VentaForm, GastoForm, TransferForm, InicialForm
from datetime import datetime
import os
from flask_migrate import Migrate
from sqlalchemy.pool import NullPool

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'app.db')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-solo-para-desarrollo')

# Aquí viene la magia: usa la URL de Postgres si la hay, sino SQLite (modo local mode ON)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or f'sqlite:///{db_path}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ajuste especial para evitar que Render nos tire con conexiones persistentes
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgresql'):
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'poolclass': NullPool,
        'connect_args': {
            'options': '-c timezone=utc'
        }
    }

db.init_app(app)
migrate = Migrate(app, db)

def init_db():
    with app.app_context():
        db.create_all()
        for metodo in ['Efectivo', 'Yape', 'Izipay']:
            if not Saldo.query.filter_by(metodo_pago=metodo).first():
                db.session.add(Saldo(
                    metodo_pago=metodo,
                    monto_inicial=0.0,
                    saldo=0.0
                ))
        db.session.commit()

def obtener_saldos():
    return Saldo.query.all()

def obtener_ventas():
    return Venta.query.order_by(Venta.fecha.desc()).all()

def obtener_gastos():
    return Gasto.query.order_by(Gasto.fecha.desc()).all()

@app.route('/init', methods=['GET','POST'])
def inicial():
    form = InicialForm()
    if form.validate_on_submit():
        saldo = Saldo.query.filter_by(metodo_pago=form.metodo.data).first()
        if saldo and saldo.monto_inicial > 0:
            flash(f"Ya existe un monto inicial para {form.metodo.data}.", 'warning')
        else:
            if not saldo:
                saldo = Saldo(metodo_pago=form.metodo.data,
                              monto_inicial=form.monto.data,
                              saldo=form.monto.data)
                db.session.add(saldo)
            else:
                saldo.monto_inicial = form.monto.data
                saldo.saldo = form.monto.data
            db.session.commit()
            flash(f"Monto inicial de S/.{form.monto.data:.2f} para {form.metodo.data} registrado.", 'success')
            return redirect(url_for('dashboard'))
    return render_template('initial_form.html', form=form)

@app.route('/')
def dashboard():
    saldos = obtener_saldos()
    ventas = obtener_ventas()
    gastos = obtener_gastos()
    total_dinero = sum(s.saldo for s in saldos) if saldos else 0

    return render_template('dashboard.html',
                           saldos=saldos,
                           ventas=ventas,
                           gastos=gastos,
                           total_dinero=total_dinero)

@app.route('/venta', methods=['GET','POST'])
def nueva_venta():
    form = VentaForm()
    if form.validate_on_submit():
        venta = Venta(
            fecha=form.fecha.data,
            monto=form.monto.data,
            metodo_pago=form.metodo.data
        )
        saldo = Saldo.query.filter_by(metodo_pago=form.metodo.data).first()
        saldo.saldo += form.monto.data
        db.session.add(venta)
        db.session.commit()
        flash('Venta registrada con éxito.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('sale_form.html', form=form)

@app.route('/gasto', methods=['GET','POST'])
def nuevo_gasto():
    form = GastoForm()
    if form.validate_on_submit():
        saldo = Saldo.query.filter_by(metodo_pago=form.metodo.data).first()
        if saldo.saldo < form.monto.data:
            flash('Saldo insuficiente para este gasto.', 'danger')
        else:
            gasto = Gasto(
                fecha=form.fecha.data,
                categoria=form.categoria.data,
                monto=form.monto.data,
                metodo_pago=form.metodo.data
            )
            saldo.saldo -= form.monto.data
            db.session.add(gasto)
            db.session.commit()
            flash('Gasto registrado con éxito.', 'warning')
            return redirect(url_for('dashboard'))
    return render_template('expense_form.html', form=form)

@app.route('/transfer', methods=['GET','POST'])
def nueva_transferencia():
    form = TransferForm()
    if form.validate_on_submit():
        origen = Saldo.query.filter_by(metodo_pago=form.origen.data).first()
        destino = Saldo.query.filter_by(metodo_pago=form.destino.data).first()
        if origen.saldo < form.monto.data:
            flash('Saldo insuficiente en el origen.', 'danger')
        else:
            origen.saldo -= form.monto.data
            destino.saldo += form.monto.data
            trans = Transferencia(
                metodo_origen=form.origen.data,
                metodo_destino=form.destino.data,
                monto=form.monto.data
            )
            db.session.add(trans)
            db.session.commit()
            flash('Transferencia exitosa.', 'info')
            return redirect(url_for('dashboard'))
    return render_template('transfer_form.html', form=form)

@app.route('/registro')
def registro():
    ventas = Venta.query.with_entities(
        Venta.id.label('id'),
        Venta.fecha.label('fecha'),
        Venta.monto.label('monto'),
        Venta.metodo_pago.label('metodo'),
        db.literal('Venta').label('tipo'),
        db.null().label('categoria')
    )
    gastos = Gasto.query.with_entities(
        Gasto.id.label('id'),
        Gasto.fecha.label('fecha'),
        Gasto.monto.label('monto'),
        Gasto.metodo_pago.label('metodo'),
        db.literal('Gasto').label('tipo'),
        Gasto.categoria.label('categoria')
    )
    registros = ventas.union_all(gastos).order_by(db.desc('fecha')).all()
    return render_template('registro.html', registros=registros)

@app.route('/ventas')
def listado_ventas():
    ventas = Venta.query.order_by(Venta.fecha.desc()).all()
    return render_template('listado_ventas.html', ventas=ventas)

@app.route('/venta/<int:venta_id>/editar', methods=['GET', 'POST'])
def editar_venta(venta_id):
    form = VentaForm()
    venta = Venta.query.get_or_404(venta_id)

    if form.validate_on_submit():
        saldo_old = Saldo.query.filter_by(metodo_pago=venta.metodo_pago).first()
        saldo_old.saldo -= venta.monto  # revertimos saldo anterior

        venta.fecha = form.fecha.data
        venta.monto = form.monto.data
        venta.metodo_pago = form.metodo.data

        saldo_new = Saldo.query.filter_by(metodo_pago=form.metodo.data).first()
        saldo_new.saldo += form.monto.data

        db.session.commit()
        flash('Venta actualizada correctamente.', 'info')
        return redirect(url_for('listado_ventas'))

    form.fecha.data = venta.fecha
    form.monto.data = venta.monto
    form.metodo.data = venta.metodo_pago

    return render_template('sale_form.html', form=form, editar=True)

@app.route('/venta/<int:venta_id>/eliminar', methods=['POST', 'GET'])
def eliminar_venta(venta_id):
    venta = Venta.query.get_or_404(venta_id)
    saldo = Saldo.query.filter_by(metodo_pago=venta.metodo_pago).first()
    saldo.saldo -= venta.monto  # revertimos saldo

    db.session.delete(venta)
    db.session.commit()
    flash('Venta eliminada y saldo ajustado.', 'danger')
    return redirect(url_for('listado_ventas'))

@app.route('/gastos')
def listado_gastos():
    gastos = Gasto.query.order_by(Gasto.fecha.desc()).all()
    return render_template('listado_gastos.html', gastos=gastos)

@app.route('/gasto/<int:gasto_id>/editar', methods=['GET', 'POST'])
def editar_gasto(gasto_id):
    form = GastoForm()
    gasto = Gasto.query.get_or_404(gasto_id)

    if form.validate_on_submit():
        saldo_old = Saldo.query.filter_by(metodo_pago=gasto.metodo_pago).first()
        saldo_old.saldo += gasto.monto  # revertimos saldo anterior

        gasto.fecha = form.fecha.data
        gasto.categoria = form.categoria.data
        gasto.monto = form.monto.data
        gasto.metodo_pago = form.metodo.data

        saldo_new = Saldo.query.filter_by(metodo_pago=form.metodo.data).first()
        saldo_new.saldo -= form.monto.data

        db.session.commit()
        flash('Gasto actualizado correctamente.', 'info')
        return redirect(url_for('listado_gastos'))

    form.fecha.data     = gasto.fecha
    form.categoria.data = gasto.categoria
    form.monto.data     = gasto.monto
    form.metodo.data    = gasto.metodo_pago

    return render_template('expense_form.html', form=form, editar=True)

@app.route('/gasto/<int:gasto_id>/eliminar', methods=['POST', 'GET'])
def eliminar_gasto(gasto_id):
    gasto = Gasto.query.get_or_404(gasto_id)
    saldo = Saldo.query.filter_by(metodo_pago=gasto.metodo_pago).first()
    saldo.saldo += gasto.monto  # revertimos saldo

    db.session.delete(gasto)
    db.session.commit()
    flash('Gasto eliminado y saldo ajustado.', 'danger')
    return redirect(url_for('listado_gastos'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

