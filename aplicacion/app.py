from typing import Text
from urllib import response
from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from aplicacion import config
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from aplicacion.forms import LoginForm, UploadForm,alumno,campeonato,buscapac,campeonato_combate\
    ,campeonato_pommse,horario_ent,fechas_buscar,buscxc
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





@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    form = fechas_buscar()
    if form.validate_on_submit():
        return redirect(url_for('inicio'))
    return render_template('home.html', form=form)





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
        cursor.execute("""SELECT  a.codart,a.nomart,a.codcla,a.marca,a.exiact,a.tippro,b.codalm
                    FROM articulos a
                    left join articulobodega b
                    on a.codart = b.codart
                    WHERE a.estado = 'A'
                    and a.codart = %s """,[id])
        data = cursor.fetchall()
        return render_template('listar-articulo1.html', data=data)


@app.route('/bus_cxc', methods = ['POST', 'GET'])
@login_required
def bus_cxc():
    form = buscxc()
    if request.method == 'POST':
        iden = request.form['iden']
        fec_ini = request.form['fec_ini'] 
        print(iden)
        cursor = mysql.connection.cursor()
        cursor.execute("""SELECT cxc.codemp,cxc.codmon,cxc.fecemi,cxc.codcli,cli.nomcli,cli.codcla
                            FROM cuentasporcobrar cxc INNER JOIN tipodocumentos tipd ON cxc.tipdoc = tipd.tipdoc 
                            INNER JOIN clientes cli ON cxc.codemp = cli.codemp AND cxc.codcli = cli.codcli
                            WHERE cxc.fecemi < %s and cli.nomcli like %s""", [fec_ini,'%'+iden+'%'])
        data = cursor.fetchall()
        #print(data[0])
        return render_template('listar-cxc.html', data=data)
    return render_template("bus_cxc.html", form=form)


@app.route('/busc_cxc/<id>/<fec>/<emp>/<mon>/<cla>')
@login_required
def busc_cxc(id,fec,emp,mon,cla):
        cursor = mysql.connection.cursor()
        cursor.execute("""CREATE TEMPORARY TABLE tmpestadocuentas AS( 	
		            SELECT cli.codemp,cli.codcli,
			        SUM( cxc.valcob *( 44 - Ascii ( tipd.sigdoc ) ) ) AS valcob
		            FROM cuentasporcobrar cxc INNER JOIN tipodocumentos tipd ON cxc.tipdoc = tipd.tipdoc 
		            INNER JOIN clientes cli ON cxc.codemp = cli.codemp AND cxc.codcli = cli.codcli 
		            WHERE cxc.codemp = %s AND 
			        cxc.codmon = %s AND
			        cxc.fecemi < %s AND
			        cxc.codcli = %s AND
			        cli.codcla LIKE %s
		            GROUP BY cli.codemp,cli.codcli
		            ORDER BY cli.codcli)""", [emp,mon,fec,id,'%'+cla+'%'])
        cursor.execute("select CURDATE();")
        fec_hoy = cursor.fetchone()
        cursor.execute("""SELECT clientes.codcli,   
	                clientes.nomcli,   
                    cuentasporcobrar.numdoc,   
                    cuentasporcobrar.tipdoc,   
                    cuentasporcobrar.fecven,   
                    cuentasporcobrar.concep,   
                    cuentasporcobrar.valcob,   
                    tmpestadocuentas.valcob,   
                    clientes.codcla,   
                    tipodocumento.sigdoc,   
                    CASE WHEN COALESCE(clientes.codcta,'') <> '' THEN clientes.codcta 
                    ELSE (SELECT grp.codcta FROM clasesclientes grp WHERE clientes.codemp = grp.codemp AND clientes.codcla = grp.codcla) 
                    END AS codcta,   
                    cuentasporcobrar.numtra,   
                    cuentasporcobrar.fectra,   
                    cuentasporcobrar.numdoc,   
                    cuentasporcobrar.fecemi  
                FROM cuentasporcobrar LEFT OUTER JOIN tmpestadocuentas ON cuentasporcobrar.codemp = tmpestadocuentas.codemp AND cuentasporcobrar.codcli = tmpestadocuentas.codcli      
                                            INNER JOIN tipodocumento ON cuentasporcobrar.tipdoc = tipodocumento.tipdoc
                                            INNER JOIN clientes ON cuentasporcobrar.codemp = clientes.codemp AND cuentasporcobrar.codcli = clientes.codcli
                WHERE cuentasporcobrar.codemp = %s  AND  
                    cuentasporcobrar.codcli = %s   AND  
                    clientes.codcla LIKE %s   AND  
                    cuentasporcobrar.fecemi BETWEEN %s AND %s AND  
                    cuentasporcobrar.codmon = %s     
                ORDER BY cuentasporcobrar.codcli ASC,   
                    cuentasporcobrar.numtra ASC,   
                    tipodocumento.sigdoc DESC,   
                    cuentasporcobrar.fecven ASC """,[emp,id,'%'+cla+'%',fec,fec_hoy,mon])
        data = cursor.fetchall()
        print(fec_hoy)
        return render_template('listar-ccxc.html', data=data)


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

@app.route('/import_csv_cxc')
@login_required
def import_csv_cxc():
    df = pd.read_excel("clientes.xlsx")
    df1 = pd.read_excel("CuentasporCobrar.xlsx")
    df2 = pd.read_excel("TipoDocumentos.xlsx")
    df3 = pd.read_excel("ClasesClientes.xlsx")
    engine = create_engine("mysql://root:1234@localhost/winxasscorp")
    engine1 = create_engine("mysql://root:1234@localhost/winxasscorp")
    engine2 = create_engine("mysql://root:1234@localhost/winxasscorp")
    engine3 = create_engine("mysql://root:1234@localhost/winxasscorp")
    df.to_sql(name='clientes', con=engine, if_exists='replace', index=False)
    df1.to_sql(name='cuentasporcobrar', con=engine1, if_exists='replace', index=False)
    df2.to_sql(name='tipodocumento', con=engine2, if_exists='replace', index=False)
    df3.to_sql(name='clasesclientes', con=engine3, if_exists='replace', index=False)
    return redirect(url_for("bus_cxc"))

