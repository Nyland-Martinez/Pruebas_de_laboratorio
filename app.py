from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL

app = Flask(__name__)

# Sesión iniciar
app.secret_key = "a_secure_random_key"

# Configuración de la base de datos MySQL
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  
app.config['MYSQL_HOST'] = '127.0.0.1'  # localhost
app.config['MYSQL_DB'] = 'laboratorio_db'  

mysql = MySQL(app)

# Ruta de inicio que muestra los pacientes
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM Pacientes')
    pacientes = cur.fetchall()
    cur.close()
    return render_template('index.html', pacientes=pacientes)

# Leer tipo de prueba
@app.route('/tipo_prueba')
def tipo_prueba():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM TipoPrueba")
    tipo_pruebas = cursor.fetchall()
    cursor.close()
    return render_template('tipo_prueba.html', tipo_pruebas=tipo_pruebas)


# Ruta para agregar un nuevo paciente
@app.route('/agg_paciente', methods=['GET', 'POST'])
def agg_paciente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        fecha_nacimiento = request.form['fecha_nacimiento']
        direccion = request.form['direccion']
        telefono = request.form['telefono']

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO Pacientes (nombre, apellido, fecha_nacimiento, direccion, telefono)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, apellido, fecha_nacimiento, direccion, telefono))
        mysql.connection.commit()
        cursor.close()
    
        return redirect(url_for('index'))
    return render_template('agg_paciente.html')

# Ruta para Registrar una Nueva Prueba
@app.route('/agg_prueba/<int:id_paciente>', methods=['GET', 'POST'])
def agg_prueba(id_paciente):
    if request.method == 'POST':
        id_paciente = request.form['id_paciente']
        nombre_tipo_prueba = request.form['nombre_tipo_prueba']
        fecha = request.form['fecha']
        descripcion = request.form['descripcion']
        
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO Prueba (id_paciente, nombre_tipo_prueba, fecha, descripcion) VALUES (%s, %s, %s, %s)", 
                       (id_paciente, fecha, nombre_tipo_prueba, descripcion))
        mysql.connection.commit()

        # Obtener el último ID de prueba insertado
        id_prueba = cursor.lastrowid
        cursor.close()
        
        # Redirigir para agregar detalles a esta prueba específica
        return redirect(url_for('agg_detalles', id_prueba=id_prueba))

    return render_template('agg_prueba.html', id_paciente=id_paciente)

# Ruta para crear detalles de una prueba
@app.route('/agg_detalles/<int:id_prueba>', methods=['GET', 'POST'])
def agg_detalles(id_prueba):
    if request.method == 'POST':
        id_prueba = request.form['id_prueba']
        parametro = request.form['parametro']
        valor = request.form['valor']
        unidad = request.form['unidad']
        rango_min = request.form['rango_min']
        rango_max = request.form['rango_max']
        
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO Detalles (id_prueba, parametro, valor, unidad, rango_min, rango_max)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (id_prueba, parametro, valor, unidad, rango_min, rango_max))
        mysql.connection.commit()
        cursor.close()
        
        return redirect(url_for('agg_detalles', id_prueba=id_prueba))

    return render_template('agg_detalles.html', id_prueba=id_prueba)

# Ruta para actualizar un paciente
@app.route('/edit_paciente/<int:id>', methods=['GET', 'POST'])
def update_paciente(id):
    cur = mysql.connection.cursor()

# Obtener el paciente existente
    cur.execute('SELECT * FROM Pacientes WHERE ID = %s', (id,))
    paciente = cur.fetchone()
    cur.close()
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        fecha_nacimiento = request.form['fecha_nacimiento']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        #Actualizar el paciente de la base de datos
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE Pacientes SET nombre=%s, apellido=%s, fecha_nacimiento=%s, direccion=%s, telefono=%s
            WHERE id_paciente=%s
        """, (nombre, apellido, fecha_nacimiento, direccion, telefono, id))
        mysql.connection.commit()
        cur.close()

        flash('Paciente actualizado exitosamente!')
        return redirect(url_for('index')) 
    
    return render_template('edit_paciente.html', paciente=paciente)

# Eliminar paciente
@app.route('/delete_paciente/<int:id>', methods=['GET', 'POST'])
def delete_paciente(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM Pacientes WHERE id_paciente = %s', (id,))
        mysql.connection.commit()
        cur.close()
        flash('Paciente eliminado exitosamente', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al eliminar el paciente: {str(e)}', 'error')
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)