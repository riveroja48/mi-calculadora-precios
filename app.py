from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configuración de Base de Datos SQLite
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
    margen_deseado = db.Column(db.Float, default=0.20)
    iva = db.Column(db.Float, default=0.19)
    comision_plataforma = db.Column(db.Float, default=0.05)
    tasa_devolucion = db.Column(db.Float, default=0.02)

    def calcular_precio_sugerido(self):
        costo_total_directo = self.insumos + self.mano_obra + self.fijos_por_unidad + self.envio
        tasas = self.margen_deseado + self.iva + self.comision_plataforma + self.tasa_devolucion
        if tasas >= 1: return 0.0
        return round(costo_total_directo / (1 - tasas), 2)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    productos = Producto.query.all()
    return render_template('index.html', productos=productos)

@app.route('/agregar', methods=['POST'])
def agregar():
    nuevo_p = Producto(
        nombre=request.form['nombre'],
        stock=int(request.form['stock']),
        insumos=float(request.form['insumos']),
        mano_obra=float(request.form['mano_obra']),
        fijos_por_unidad=float(request.form['fijos']),
        envio=float(request.form['envio']),
        margen_deseado=float(request.form['margen'])/100,
        iva=float(request.form['iva'])/100,
        comision_plataforma=float(request.form['comision'])/100,
        tasa_devolucion=float(request.form['devolucion'])/100
    )
    db.session.add(nuevo_p)
    db.session.commit()
    return redirect(url_for('index'))

# --- NUEVA FUNCIÓN PARA EDITAR ---
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    p = Producto.query.get_or_404(id)
    if request.method == 'POST':
        p.nombre = request.form['nombre']
        p.stock = int(request.form['stock'])
        p.insumos = float(request.form['insumos'])
        p.mano_obra = float(request.form['mano_obra'])
        p.fijos_por_unidad = float(request.form['fijos'])
        p.envio = float(request.form['envio'])
        p.margen_deseado = float(request.form['margen'])/100
        p.iva = float(request.form['iva'])/100
        p.comision_plataforma = float(request.form['comision'])/100
        p.tasa_devolucion = float(request.form['devolucion'])/100
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('editar.html', p=p)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
