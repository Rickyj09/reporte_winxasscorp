from typing import Text
from urllib import response
from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from aplicacion import config
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from aplicacion.forms import LoginForm, UploadForm,alumno,campeonato,buscapac,campeonato_combate\
    ,campeonato_pommse,horario_ent,fechas_buscar
from wtforms import SubmitField
from flask_wtf.file import FileField, FileRequired
from jinja2 import Environment, FileSystemLoader
from os import listdir
from flask_login import LoginManager, login_user, logout_user, login_required,\
    current_user

from sqlalchemy import create_engine
from aplicacion.forms import LoginForm, FormUsuario
import pdfkit
import os
import pymysql
import csv
import pandas as pd


UPLOAD_FOLDER = os.path.abspath("./static/uploads/")
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpge"])


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.config.from_object(config)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# Mysql Connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'winxasscorp'
mysql = MySQL(app)

# setting
app.secret_key = 'millave'


@login_manager.user_loader
def load_user(user_id):
    return (user_id)


@app.route('/')
def inicio():
    return render_template("inicio.html")


@app.route('/inicio_1')
@app.route('/inicio_1/<id>')
def inicio_1(id='0'):
    from aplicacion.models import Articulos, Categorias
    categoria = Categorias.query.get(id)
    if id == '0':
        articulos = Articulos.query.all()
    else:
        articulos = Articulos.query.filter_by(CategoriaId=id)
    categorias = Categorias.query.all()
    return render_template("inicio_1.html", articulos=articulos, categorias=categorias, categoria=categoria)


@app.route('/inicio_new')
@app.route('/inicio_new/<id>')
def inicio_new(id='0'):
    from aplicacion.models import Articulos, Categorias
    categoria = Categorias.query.get(id)
    if id == '0':
        articulos = Articulos.query.all()
    else:
        articulos = Articulos.query.filter_by(CategoriaId=id)
    categorias = Categorias.query.all()
    return render_template("inicio_new.html", articulos=articulos, categorias=categorias, categoria=categoria)

@app.route('/nosotros')
def nosotros():
    return render_template("nosotros.html")



@app.route('/historia')
def historia():
    return render_template("historia.html")


@app.route('/ocupa')
def ocupa():
    return render_template("ocupa.html")



@app.route('/resumen')
@login_required
def resumen():
    datos = request.cookies.get('cookie_pac')
    cursor = mysql.connection.cursor()
    cursor.execute(
        "select apellido1,nombres from paciente a  inner join pruebas b on  a.iden = b.id_paci where iden = %s;" , [datos])
    nom_pac = cursor.fetchone()
    cursor.execute(
        "select medico from paciente a inner join pruebas b on  a.iden = b.id_paci where iden = %s;" , [datos])
    med = cursor.fetchone()
    cursor.execute(
        "SELECT (TIMESTAMPDIFF(YEAR,fec_nac,CURDATE())) AS edad FROM paciente a  inner join pruebas b on  a.iden = b.id_paci where iden = %s;" , [datos])
    edad = cursor.fetchone()
    cursor.execute("select CURDATE();")
    fec_hoy = cursor.fetchone()
    cursor.execute(
        "select iden from paciente a  inner join pruebas b on  a.iden = b.id_paci where iden = %s;" , [datos])
    ci = cursor.fetchone()
    cursor.execute(
        "select * from pruebas where id = (select MAX(id) from pruebas);")
    datos = cursor.fetchall()
    print(datos)
    cursor.close()

    return render_template('resumen.html', nom_pac=nom_pac, med=med, edad=edad, fec_hoy=fec_hoy, ci=ci, datos=datos)


@login_manager.user_loader
def load_user(user_id):
    from aplicacion.models import Usuarios
    return Usuarios.query.get(int(user_id))


@app.route('/upload', methods=['get', 'post'])
def upload():
    form = UploadForm()  # carga request.from y request.file
    if form.validate_on_submit():
        f = form.photo.data
        filename = secure_filename(f.filename)
        f.save(app.root_path+"/static/img/subidas/"+filename)
        return redirect(url_for('inicio_foto'))
    return render_template('upload.html', form=form)


@app.route('/upload_1', methods=['get', 'post'])
def upload_1():
    form = UploadForm()  # carga request.from y request.file
    if form.validate_on_submit():
        f = form.photo.data
        filename = secure_filename(f.filename)
        f.save(app.root_path+"/static/img/subidas/"+filename)
        return redirect(url_for('reporte_foto'))
    return render_template('upload_1.html', form=form)


@app.route('/inicio_foto')
@login_required
def inicio_foto():
    lista = []
    for file in listdir(app.root_path+"/static/img/subidas/"):
        lista.append(file)
    return render_template("inicio_foto.html", lista=lista)


@app.route('/reporte_foto')
@login_required
def reporte_foto():
    lista = []
    for file in listdir(app.root_path+"/static/img/subidas/"):
        lista.append(file)
    return render_template("reporte_foto.html", lista=lista)


@app.route('/reporte_foto1')
@login_required
def reporte_foto1():
    lista = []
    for file in listdir(app.root_path+"/static/img/subidas/"):
        lista.append(file)
    return render_template("reporte_foto1.html", lista=lista)


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    form = fechas_buscar()
    if form.validate_on_submit():
        return redirect(url_for('inicio'))
    return render_template('home.html', form=form)


@app.route('/home_alumn', methods=['GET', 'POST'])
@login_required
def home_alumn():

    return render_template('home_alumn.html')


@app.route('/home_campeonato', methods=['GET', 'POST'])
@login_required
def home_campeonato():

    return render_template('home_campeonato.html')

@app.route('/cate_peso', methods=['GET', 'POST'])
@login_required
def cate_peso():
    cur = mysql.connection.cursor()
    cur.execute('SELECT a.nombre,b.nombre,a.genero,a.rango,b.rango FROM cat_peso a inner JOIN cat_edad b on a.id_edad = b.id ')
    data = cur.fetchall()
    cur.close()

    return render_template('cate_peso.html', data=data)


@app.route('/horario_entrena', methods=['GET', 'POST'])
@login_required
def horario_entrena():
    form = horario_ent()
    if request.method == 'POST':
        iden = request.form['iden']
        horario = request.form['horario']
        cursor = mysql.connection.cursor()
        cursor.execute('select CURDATE()')
        fecha_log = cursor.fetchone()
        cursor.execute('insert into horario (id_alumno,valor_horario,fecha) VALUES (%s,%s,%s)',
                       (iden, horario, fecha_log))
        mysql.connection.commit()
        return render_template("home.html", form=form)
    return render_template('horario_entrena.html', form=form)

@app.route('/listar_paci/<id>', methods=['POST', 'GET'])
@login_required
def listar_paci(id):
    cur = mysql.connection.cursor()
    cur.execute(
        'SELECT * FROM paciente a inner join cat_examenes b on  a.id_examen = b.id  WHERE a.iden = %s )',  [id])
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('listar-paci.html', contact=data[0])


@app.route('/busc_articulo', methods = ['POST', 'GET'])
@login_required
def busc_articulo():
    form = buscapac()
    if request.method == 'POST':
        iden = request.form['iden']
        print(iden)
        cursor = mysql.connection.cursor()
        cursor.execute("""select codart,nomart from articulos
                            where nomart like %s""", ['%'+iden+'%'])
        data = cursor.fetchall()
        print(data[0])
        return render_template('listar-articulo.html', data=data)
    return render_template("bus_articulo.html", form=form)


@app.route('/busc_articulo1/<id>')
@login_required
def busc_articulo1(id):
        cursor = mysql.connection.cursor()
        cursor.execute("""SELECT articulos.codart,articulos.nomart,
			            articulos.codcla,articulos.coduni,   
                        articulos.codemp,articulos.marca,articulos.exiact,   
                        articulos.prec01,articulos.prec02,articulos.prec03,
			            articulos.prec04,articulos.cospro,articulos.ultcos,
			            articulos.prec05,articulos.prec06,articulos.peso,
			            articulos.codiva,articulos.prcc01,articulos.prcc02,
			            articulos.prcc03,articulos.prcc04,articulos.tippro,
			            articulos.especial,
			            articulos.unicaj,
			            articulos.univen
                    FROM articulos  
                    WHERE estado = 'A'
                    and codart = %s """,[id])
        data = cursor.fetchall()
        return render_template('listar-articulo1.html', data=data)
  



@app.route('/campeonato_new', methods=["get", "post"])
@login_required
def campeonato_new():
    form = campeonato()
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        nombre = request.form['nombre']
        puntua = request.form['puntua']
        fecha = request.form['fecha']
        obs = request.form['obs']
        cursor = mysql.connection.cursor()
        cursor.execute('insert into campeonato (nombre,puntua,fecha,obs) VALUES (%s,%s,%s,%s)',
                       (nombre, puntua, fecha, obs,))
        mysql.connection.commit()
        flash('Campeonato guardado correctamente')
        return render_template("home.html", form=form)
    return render_template("campeonato_new.html", form=form)


@app.route('/alumno_foto')
@login_required
def alumno_foto():
    lista = []
    for file in listdir(app.root_path+"/static/img/fotos/"):
        lista.append(file)
    return render_template("home.html", lista=lista)


@app.route('/upload_foto', methods=['get', 'post'])
def upload_foto():
    form = UploadForm()  # carga request.from y request.file
    if form.validate_on_submit():
        f = form.photo.data
        filename = secure_filename(f.filename)
        f.save(app.root_path+"/static/fotos/"+filename)
        foto = filename
        cursor = mysql.connection.cursor()
        cursor.execute('select identificacion from alumno where fecha_log = (select max(fecha_log) from alumno);')
        ident = cursor.fetchone()
        cursor.execute('insert into alumno_foto (iden,foto) VALUES (%s,%s)',(ident,foto))
        mysql.connection.commit()
        return redirect(url_for('home'))
    return render_template('upload_foto.html', form=form)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html", error="Página no encontrada..."), 404


@app.route('/cons_404', methods=['GET', 'POST'])
def cons_404():
    return render_template('404_cons.html')


@app.route('/login', methods=['get', 'post'])
def login():
    from aplicacion.models import Usuarios
    # Control de permisos
    if current_user.is_authenticated:
        # return 'OK'
        return redirect(url_for("home_alumn"))
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuarios.query.filter_by(username=form.username.data).first()
        print(user)
        pas1 = Usuarios.query.filter_by(password=form.password.data).first()
        print(pas1)
        pas = user.verify_password(form.password.data)
        print(pas)
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        form.username.errors.append("Usuario o contraseña incorrectas.")
    return render_template('login.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('inicio'))


@app.route('/perfil/<username>', methods=["get", "post"])
@login_required
def perfil(username):
    from aplicacion.models import Usuarios
    user = Usuarios.query.filter_by(username=username).first()
    if user is None:
        render_template("404.html")
    form = FormUsuario(request.form, obj=user)
    del form.password
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        return redirect(url_for("inicio"))
    return render_template("usuarios_new.html", form=form, perfil=True)


@login_manager.user_loader
def load_user(user_id):
    from aplicacion.models import Usuarios
    return Usuarios.query.get(int(user_id))




@app.route('/import_csv')
def import_csv():
    with open('test.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        print(reader)
        for row in reader:
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO posicion_camp (nombres, academia, ubicacion, puntos, obs) VALUES (%s, %s, %s, %s, %s)'%(str(row[0]),str(row[0]),str(row[2]),str(row[3]),str(row[4])))
            mysql.connection.commit()
    return 'CSV importado successfully'


@app.route('/import_csv_p')
@login_required
def import_csv_p():
    df = pd.read_excel("articulos.xlsx")
    df1 = pd.read_excel("almacenes.xlsx")
    df2 = pd.read_excel("articulobodega.xlsx")
    df3 = pd.read_excel("articulos_alternos.xlsx")
    engine = create_engine("mysql://root:1234@localhost/winxasscorp")
    engine1 = create_engine("mysql://root:1234@localhost/winxasscorp")
    engine2 = create_engine("mysql://root:1234@localhost/winxasscorp")
    engine3 = create_engine("mysql://root:1234@localhost/winxasscorp")
    df.to_sql(name='articulos', con=engine, if_exists='replace', index=False)
    df1.to_sql(name='almacenes', con=engine1, if_exists='replace', index=False)
    df2.to_sql(name='articulobodega', con=engine2, if_exists='replace', index=False)
    df3.to_sql(name='articulos_alternos', con=engine3, if_exists='replace', index=False)
    return redirect(url_for("busc_articulo"))



