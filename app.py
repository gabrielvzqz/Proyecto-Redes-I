from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import config
import os
import re

def validar_password(password):
    """Mecanismo inteligente: Valida fortaleza de contraseña"""
    if len(password) < 8:
        return "❌ La contraseña debe tener al menos 8 caracteres"
    if not re.search(r'[A-Z]', password):
        return "❌ Debe contener al menos una mayúscula (A-Z)"
    if not re.search(r'\d', password):
        return "❌ Debe contener al menos un número (0-9)"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_]', password):
        return "❌ Debe contener al menos un carácter especial (!@#$% etc.)"
    return None

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
        # VERIFICAR si usuario existe antes de usar .username
        if usuario:
            return render_template('index.html', usuario=usuario.username, title="Inicio")
        else:
            # Si el usuario no existe en BD, limpiar sesión
            session.pop('user_id', None)
            return render_template('index.html', usuario=None, title="Login")
    return render_template('index.html', usuario=None, title="Login")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Mecanismo inteligente: Validar contraseña
        error_password = validar_password(password)
        if error_password:
            return f"""
            <h2>Error en contraseña</h2>
            <p>{error_password}</p>
            <p><a href="{url_for('index')}">← Volver a intentar</a></p>
            <hr>
            <small>Requisitos: 8+ caracteres, mayúscula, número, carácter especial</small>
            """, 400
        
        usuario = Usuario.query.filter_by(username=username, password=password).first()
        
        if usuario:
            session['user_id'] = usuario.id
            return redirect(url_for('tasks'))
        else:
            return """
            <h2>Credenciales incorrectas</h2>
            <p>Usuario o contraseña no válidos.</p>
            <p><a href="{}">← Volver a intentar</a></p>
            """.format(url_for('index')), 401
    
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

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """Ruta para registro de nuevos usuarios"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirmar = request.form.get('confirmar_password', '')
        
        # Validaciones
        if password != confirmar:
            return "❌ Las contraseñas no coinciden. <a href='/registro'>Volver</a>", 400
        
        error_password = validar_password(password)
        if error_password:
            return f"""
            <h2>Error en contraseña</h2>
            <p>{error_password}</p>
            <p><a href="/registro">← Volver a intentar</a></p>
            """, 400
        
        # Verificar si usuario ya existe
        if Usuario.query.filter_by(username=username).first():
            return "❌ El usuario ya existe. <a href='/registro'>Volver</a>", 400
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(username=username, password=password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        # Auto-login
        session['user_id'] = nuevo_usuario.id
        return redirect(url_for('tasks'))
    
    # GET: Mostrar formulario de registro
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Registro</title></head>
    <body>
        <h1>📝 Registro de nuevo usuario</h1>
        <form method="POST">
            Usuario: <input type="text" name="username" required><br><br>
            Contraseña: <input type="password" name="password" required><br><br>
            Confirmar contraseña: <input type="password" name="confirmar_password" required><br><br>
            <input type="submit" value="Registrarse">
        </form>
        <hr>
        <p><strong>Requisitos contraseña:</strong></p>
        <ul>
            <li>Mínimo 8 caracteres</li>
            <li>Al menos una mayúscula (A-Z)</li>
            <li>Al menos un número (0-9)</li>
            <li>Al menos un carácter especial (!@#$%^&* etc.)</li>
        </ul>
        <p><a href="/">← Volver al login</a></p>
    </body>
    </html>
    """
# ---------- INICIALIZAR BD ----------
with app.app_context():
    db.create_all()
    # Crear usuario admin si no existe (para Render)
    if not Usuario.query.filter_by(username='admin').first():
        usuario_admin = Usuario(username='admin', password='1234')
        db.session.add(usuario_admin)
        db.session.commit()
        print("Usuario admin creado automáticamente")
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render usa PORT=10000
    app.run(host='0.0.0.0', port=port, debug=False)  # debug=False en producción