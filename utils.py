from models import db, Venta, Gasto, ROA, Saldo
from datetime import datetime

def calcula_y_guarda_roa():
    # Fecha actual y primer día del mes
    ahora = datetime.utcnow()
    primer_dia_mes = datetime(ahora.year, ahora.month, 1)
    
    # Total ventas del mes (suma monto)
    total_ventas = db.session.query(db.func.coalesce(db.func.sum(Venta.monto), 0))\
        .filter(Venta.fecha >= primer_dia_mes).scalar()
    
    # Total gastos del mes (suma monto)
    total_gastos = db.session.query(db.func.coalesce(db.func.sum(Gasto.monto), 0))\
        .filter(Gasto.fecha >= primer_dia_mes).scalar()
    
    # Utilidad neta = ventas - gastos
    utilidad_neta = total_ventas - total_gastos
    
    # Activo total = suma de montos iniciales (no el saldo, porque el saldo puede variar)
    activo_total = db.session.query(db.func.coalesce(db.func.sum(Saldo.monto_inicial), 0)).scalar()
    
    # Evitamos división por cero
    if activo_total == 0:
        roa = 0.0
    else:
        roa = utilidad_neta / activo_total
    
    # Guardamos el ROA para el mes actual en formato 'YYYY-MM'
    mes_str = primer_dia_mes.strftime('%Y-%m')
    registro_roa = ROA.query.filter_by(mes=mes_str).first()
    
    if registro_roa:
        registro_roa.valor = roa
    else:
        registro_roa = ROA(mes=mes_str, valor=roa)
        db.session.add(registro_roa)
    
    db.session.commit()
