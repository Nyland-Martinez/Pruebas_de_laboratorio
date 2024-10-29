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
@app.route('/', methods=['GET', 'POST'])
def index():
    cur = mysql.connection.cursor()
    
    if request.method == 'POST':
        # Obtener el valor de búsqueda ingresado
        search_query = request.form.get('search_query')
        query = """SELECT * FROM Pacientes WHERE nombre LIKE %s OR apellido LIKE %s"""
        like_query = f"%{search_query}%"
        cur.execute(query, (like_query, like_query))
    else:
        # Si no hay paciente de búsqueda, muestra todos los pacientes
        cur.execute('SELECT * FROM Pacientes')
    
    pacientes = cur.fetchall()
    cur.close()
    return render_template('index.html', pacientes=pacientes)

# Leer prueba
@app.route('/pruebas')
def pruebas():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Pruebas")
    pruebas = cursor.fetchall()
    cursor.close()
    return render_template('pruebas.html', pruebas=pruebas)

# Leer resultados de una prueba
@app.route('/resultados')
def resultados():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Resultados")
    resultados = cursor.fetchall()
    cursor.close()
    return render_template('resultados.html', resultados=resultados)

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
        cursor.execute("""
            INSERT INTO Pruebas (id_paciente, nombre_tipo_prueba, fecha, descripcion) 
            VALUES (%s, %s, %s, %s)
        """, (id_paciente, fecha, nombre_tipo_prueba, descripcion))
        mysql.connection.commit()

        # Obtener el último ID de prueba insertado
        id_prueba = cursor.lastrowid
        cursor.close()
        
        # Redirigir para agregar detalles a esta prueba específica
        return redirect(url_for('agg_detalles', id_prueba=id_prueba))

    return render_template('agg_prueba.html', id_paciente=id_paciente)

# Ruta para crear resultados de una prueba
@app.route('/agg_resultados/<int:id_prueba>', methods=['GET', 'POST'])
def agg_resultados(id_prueba):
    if request.method == 'POST':
        id_prueba = request.form['id_prueba']
        parametro = request.form['parametro']
        valor = request.form['valor']
        unidad = request.form['unidad']
        rango_min = request.form['rango_min']
        rango_max = request.form['rango_max']
        
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO Resultados (id_prueba, parametro, valor, unidad, rango_min, rango_max)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (id_prueba, parametro, valor, unidad, rango_min, rango_max))
        mysql.connection.commit()
        cursor.close()
        
        return redirect(url_for('agg_resultados', id_prueba=id_prueba))

    return render_template('agg_resultados.html', id_prueba=id_prueba)

# Ruta para actualizar un paciente
@app.route('/edit_paciente/<int:id_paciente>', methods=['GET', 'POST'])
def update_paciente(id_paciente):
    cur = mysql.connection.cursor()

# Obtener el paciente existente
    cur.execute('SELECT * FROM Pacientes WHERE id_paciente = %s', (id_paciente,))
    paciente = cur.fetchone()
    cur.close()
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        fecha_nacimiento = request.form['fecha_nacimiento']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        # Actualizar el paciente de la base de datos
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE Pacientes SET nombre=%s, apellido=%s, fecha_nacimiento=%s, direccion=%s, telefono=%s
            WHERE id_paciente=%s
        """, (nombre, apellido, fecha_nacimiento, direccion, telefono, id_paciente))
        mysql.connection.commit()
        cur.close()

        flash('Paciente actualizado exitosamente!')
        return redirect(url_for('index')) 
    
    return render_template('edit_paciente.html', paciente=paciente)

# Ruta para actualizar prueba
@app.route('/edit_prueba/<int:id_prueba>', methods=['GET', 'POST'])
def update_prueba(id_prueba):
    cursor = mysql.connection.cursor()

    # Obtener prueba existente
    cursor.execute("SELECT * FROM Pruebas WHERE id_prueba=%s", (id_prueba,))
    prueba = cursor.fetchone()
    cursor.close()
    if request.method == 'POST':
        id_paciente = request.form['id_paciente']
        nombre_tipo_prueba = request.form['nombre_tipo_prueba']
        fecha = request.form['fecha']
        descripcion = request.form['descripcion']

        cursor.execute("""
            UPDATE Pruebas SET id_paciente=%s, nombre_tipo_prueba=%s, fecha=%s, descripcion=%s
            WHERE id_prueba=%s
        """, (id_paciente, nombre_tipo_prueba, fecha, descripcion, id_prueba))
        mysql.connection.commit()
        cursor.close()

        flash('Prueba actualizado exitosamente!')
        return redirect(url_for('pruebas'))

    return render_template('edit_prueba.html', prueba=prueba)

# Ruta para actualizar el resultado de una prueba
@app.route('/edit_resultado/<int:id_resultados>', methods=['GET', 'POST'])
def update_resultado(id_resultados):
    cursor = mysql.connection.cursor()

    # Obtener resultado de prueba existente
    cursor.execute("SELECT * FROM Resultados WHERE id_resultados=%s", (id_resultados,))
    resultado = cursor.fetchone()
    cursor.close()
    if request.method == 'POST':
        id_prueba = request.form['id_prueba']
        parametro = request.form['parametro']
        valor = request.form['valor']
        unidad = request.form['unidad']
        rango_min = request.form['rango_min']
        rango_max = request.form['rango_max']

        cursor.execute("""
            UPDATE Resultados SET id_prueba=%s, parametro=%s, valor=%s, unidad=%s, rango_min=%s, rango_max=%s
            WHERE id_prueba=%s
        """, (id_prueba, parametro, valor, unidad, rango_min, rango_max, id_resultados))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('resultados'))

    return render_template('edit_resultados.html', resultado=resultado)

# Eliminar paciente
@app.route('/delete_paciente/<int:id_paciente>', methods=['GET', 'POST'])
def delete_paciente(id_paciente):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM Pacientes WHERE id_paciente = %s', (id_paciente,))
        mysql.connection.commit()
        cur.close()
        flash('Paciente eliminado exitosamente', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al eliminar el paciente: {str(e)}', 'error')
    return redirect(url_for('index'))

# Eliminar prueba
@app.route('/delete_prueba/<int:id_prueba>', methods=['GET', 'POST'])
def delete_prueba(id_prueba):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM Pruebas WHERE id_prueba=%s", (id_prueba,))
        mysql.connection.commit()
        cursor.close()
        flash('Prueba eliminado exitosamente', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al eliminar la prueba: {str(e)}', 'error')
    return redirect(url_for('pruebas'))

# Eliminar resultado
@app.route('/delete_resultado/<int:id_resultados>', methods=['GET', 'POST'])
def delete_resultado(id_resultados):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM Resultados WHERE id_resultados=%s", (id_resultados,))
        mysql.connection.commit()
        cursor.close()
        flash('Resultado de la prueba eliminado exitosamente', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al eliminar el resultado de la prueba: {str(e)}', 'error')
    return redirect(url_for('resultados'))

if __name__ == "__main__":
    app.run(debug=True)