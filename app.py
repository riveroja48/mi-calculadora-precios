from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configuración de Base de Datos
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'inventario.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer, default=0)
    insumos = db.Column(db.Float, default=0.0)
    mano_obra = db.Column(db.Float, default=0.0)
    fijos_por_unidad = db.Column(db.Float, default=0.0)
    envio = db.Column(db.Float, default=0.0)
    margen_deseado = db.Column(db.Float, default=0.0)
    iva = db.Column(db.Float, default=0.0)
    comision_plataforma = db.Column(db.Float, default=0.0)
    tasa_devolucion = db.Column(db.Float, default=0.0)

    def calcular_precio_sugerido(self):
        costo_total_directo = self.insumos + self.mano_obra + self.fijos_por_unidad + self.envio
        # Sumatoria de tasas impositivas y de ganancia
        tasas = self.margen_deseado + self.iva + self.comision_plataforma + self.tasa_devolucion
        
        if tasas >= 1: return 0.0 # Evita división por cero o resultados negativos
        
        return round(costo_total_directo / (1 - tasas), 2)

with app.app_context():
    db.create_all()

# Función auxiliar para convertir texto de formulario a número de forma segura
def safe_float(value):
    try:
        return float(value) if value else 0.0
    except ValueError:
        return 0.0

@app.route('/')
def index():
    productos = Producto.query.all()
    return render_template('index.html', productos=productos)

@app.route('/agregar', methods=['POST'])
def agregar():
    nuevo_p = Producto(
        nombre=request.form.get('nombre', 'Sin nombre'),
        stock=int(request.form.get('stock') or 0),
        insumos=safe_float(request.form.get('insumos')),
        mano_obra=safe_float(request.form.get('mano_obra')),
        fijos_por_unidad=safe_float(request.form.get('fijos')),
        envio=safe_float(request.form.get('envio')),
        margen_deseado=safe_float(request.form.get('margen')) / 100,
        iva=safe_float(request.form.get('iva')) / 100,
        comision_plataforma=safe_float(request.form.get('comision')) / 100,
        tasa_devolucion=safe_float(request.form.get('devolucion')) / 100
    )
    db.session.add(nuevo_p)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    p = Producto.query.get_or_404(id)
    if request.method == 'POST':
        p.nombre = request.form.get('nombre', p.nombre)
        p.stock = int(request.form.get('stock') or 0)
        p.insumos = safe_float(request.form.get('insumos'))
        p.mano_obra = safe_float(request.form.get('mano_obra'))
        p.fijos_por_unidad = safe_float(request.form.get('fijos'))
        p.envio = safe_float(request.form.get('envio'))
        p.margen_deseado = safe_float(request.form.get('margen')) / 100
        p.iva = safe_float(request.form.get('iva')) / 100
        p.comision_plataforma = safe_float(request.form.get('comision')) / 100
        p.tasa_devolucion = safe_float(request.form.get('devolucion')) / 100
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('editar.html', p=p)

# --- NUEVA RUTA PARA ELIMINAR ---
@app.route('/eliminar/<int:id>')
def eliminar(id):
    p = Producto.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
