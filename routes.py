from flask import *
import MySQLdb
import config
from flask import request, url_for, jsonify
import os
from werkzeug import secure_filename
import urllib
# from flask_bootstrap import Bootstrap
# from flask_appconfig import AppConfig
app =  Flask(__name__)
app.config.from_object('config')
app.secret_key = 'dfmm234xdsfdfssf2133edssdgfqwewqewr'


@app.route('/',methods=["GET","POST"])
@app.route('/index',methods=["GET","POST"])
@app.route('/login',methods=["GET","POST"])
def index():
	error=None
	if request.method == 'POST'	:
		if request.form['user_name'] != 'admin' or request.form['user_password'] !='admin' :
			error="Invalid User or Password"
		else :
			session['logged_in']=True
			return redirect(url_for('dashboard'))
	return render_template('index.html' , error=error)

@app.route('/register',methods=["GET","POST"])
def register():
	error=None
	if session['logged_in'] == True	:
			return redirect(url_for('dashboard'))

	return render_template('register.html' , error=error)

@app.route('/dashboard')
def dashboard():
	ip = '5.5'
	if(session['logged_in']==True) :
		return render_template('dashboard.html',ip=ip)
	else :
		return	redirect(url_for('/'))
@app.route('/get_ip', methods=['GET', 'POST'])
def get_ip():
	location = urllib.urlopen('http://api.hostip.info/get_html.php?ip='+request.remote_addr+'&position=true').read()
	print location
	return  request.remote_addr

def create_tables():
	db = MySQLdb.connect(user=config.DB_USERNAME, passwd=config.DB_PASSWORD, db=config.DB_NAME)
	cursor = db.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('Insert into Info values("abc")')
	db.commit()
	db.close()


@app.route('/logout')
def logout():
	session['logged_in']=None
	return redirect(url_for('index'))


#--------------uploader -------------------
def save_file(data_file, file_name):
	#global dump
	try:
		location = os.getcwd() + "/uploads"
		with open(file_name, 'wb') as location:
			shutil.copyfileobj(data_file, location)
	except:
		return "error"

    #del dump
	return 

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(config.UPLOAD_FOLDER,
                               filename)

@app.route('/+upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        # we are expected to return a list of dicts with infos about the already available files:
        file_infos = []
        for file_name in list_files():
            file_url = url_for('download', file_name=file_name)
            file_size = os.stat(file_name).st_size
            file_infos.append(dict(name=file_name,
                                   size=file_size,
                                   url=file_url))
        return jsonify(files=file_infos)

    if request.method == 'POST':
        # we are expected to save the uploaded file and return some infos about it:
        #                              vvvvvvvvv   this is the name for input type=file
        data_file = request.files.get('data_file')
        file_name = data_file.filename
        #saved_file=save_file(data_file, file_name)
        if data_file :
        	filename = secure_filename(data_file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        data_file.save(os.path.join(config.UPLOAD_FOLDER, filename))
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        #return redirect()
        #file_size = get_file_size(file_name)
        file_url = url_for('uploaded_file',
                                filename=filename)
        # providing the thumbnail url is optional
        thumbnail_url = url_for('uploaded_file',
                                filename=filename)
        file_size = os.stat(os.path.join(config.UPLOAD_FOLDER, filename)).st_size
        return jsonify(name=file_name,
                       size=file_size,
                       url=file_url,
                       thumbnail=thumbnail_url)

if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0', port=8080)