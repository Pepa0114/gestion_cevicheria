from flask_wtf import FlaskForm
from wtforms import SelectField, FloatField, SubmitField, StringField,DateField
from wtforms.validators import DataRequired, NumberRange
from datetime import date 

METODOS = [('Efectivo','Efectivo'),
           ('Yape','Yape'),
           ('Izipay','Izipay')]

class InicialForm(FlaskForm):
    metodo = SelectField('Método de Pago', choices=METODOS, validators=[DataRequired()])
    monto = FloatField('Monto Inicial', validators=[DataRequired(), NumberRange(min=0.0)])
    submit = SubmitField('Guardar Monto Inicial')

class VentaForm(FlaskForm):
    fecha = DateField('Fecha', default=date.today, format='%Y-%m-%d', validators=[DataRequired()])
    monto = FloatField('Monto', validators=[DataRequired(), NumberRange(min=0.01)])
    metodo = SelectField('Método de Pago', choices=METODOS, validators=[DataRequired()])
    submit = SubmitField('Registrar Venta')

class GastoForm(FlaskForm):
    fecha = DateField('Fecha', default=date.today, format='%Y-%m-%d', validators=[DataRequired()])
    categoria = StringField('Categoría', validators=[DataRequired()])
    monto = FloatField('Monto', validators=[DataRequired(), NumberRange(min=0.01)])
    metodo = SelectField('Método de Pago', choices=METODOS, validators=[DataRequired()])
    submit = SubmitField('Registrar Gasto')
class TransferForm(FlaskForm):
    origen = SelectField('Origen', choices=METODOS, validators=[DataRequired()])
    destino = SelectField('Destino', choices=METODOS, validators=[DataRequired()])
    monto = FloatField('Monto', validators=[DataRequired(), NumberRange(min=0.01)])
    submit = SubmitField('Transferir')
