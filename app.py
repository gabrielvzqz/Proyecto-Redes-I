from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------- MODELOS ----------
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    tareas = db.relationship('Tarea', backref='usuario', lazy=True)

class Tarea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    completada = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

# ---------- RUTAS ----------
@app.route('/')
def index():
    if 'user_id' in session:
        usuario = Usuario.query.get(session['user_id'])
        return render_template('index.html', usuario=usuario.username, title="Inicio")
    return render_template('index.html', usuario=None, title="Login")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        usuario = Usuario.query.filter_by(username=username, password=password).first()
        
        if usuario:
            session['user_id'] = usuario.id
            return redirect(url_for('tasks'))
        else:
            return "Credenciales incorrectas", 401
    
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/tasks')
def tasks():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    usuario = Usuario.query.get(session['user_id'])
    lista_tareas = Tarea.query.filter_by(usuario_id=usuario.id).all()
    
    return render_template('tasks.html', 
                           usuario=usuario.username,
                           tareas=lista_tareas,
                           title="Mis Tareas")

@app.route('/add_task', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    texto_tarea = request.form['task_text']
    
    if texto_tarea.strip():
        nueva_tarea = Tarea(
            usuario_id=session['user_id'],
            texto=texto_tarea,
            completada=False
        )
        db.session.add(nueva_tarea)
        db.session.commit()
    
    return redirect(url_for('tasks'))

@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    tarea = Tarea.query.filter_by(id=task_id, usuario_id=session['user_id']).first()
    if tarea:
        db.session.delete(tarea)
        db.session.commit()
    
    return redirect(url_for('tasks'))

@app.route('/toggle_task/<int:task_id>')
def toggle_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    tarea = Tarea.query.filter_by(id=task_id, usuario_id=session['user_id']).first()
    if tarea:
        tarea.completada = not tarea.completada
        db.session.commit()
    
    return redirect(url_for('tasks'))

@app.route('/about')
def about():
    return "<h1>Acerca de</h1><p>Esta es mi aplicación Flask para la práctica de Redes.</p>"

# ---------- INICIALIZAR BD ----------
with app.app_context():
    db.create_all()
    print("Tablas creadas/verificadas")
    
    # Crear usuario por defecto si no existe
    if not Usuario.query.first():
        usuario_admin = Usuario(
            username='admin',
            password='1234'
        )
        db.session.add(usuario_admin)
        db.session.commit()
        print("Usuario admin creado")

# CAMBIA ESTO:
if __name__ == '__main__':
    app.run(debug=True)

# POR ESTO:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)