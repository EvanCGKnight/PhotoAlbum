#!/usr/bin/env python
import sys
from flask import Flask, jsonify, abort, request, make_response, session, send_file
from flask_restful import reqparse, Resource, Api
from flask_session import Session
import base64
import MySQLdb
import json
import ldap
import ssl
import settings # Our server and db settings, stored in settings.py

app = Flask(__name__)

# force std to use utf-8
reload(sys)
sys.setdefaultencoding('utf-8')

app.secret_key = settings.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'peanutButter'
app.config['SESSION_COOKIE_DOMAIN'] = settings.APP_HOST
Session(app)

####################################################################################
#
# Error handlers
#
@app.errorhandler(400) # decorators to add to 400 response
def not_found(error):
	return make_response(jsonify( { 'status': 'Bad request' } ), 400)

@app.errorhandler(403) # decorators to add to 403 response
def not_found(error):
	return make_response(jsonify( { 'status': 'Forbidden' } ), 403)

@app.errorhandler(404) # decorators to add to 404 response
def not_found(error):
	return make_response(jsonify( { 'status': 'Resource not found' } ), 404)

####################################################################################
#wu-tang forever
class Root(Resource): # NEW FOR STATIC PAGE
	def get(self):
		return app.send_static_file('index.html')

####################################################################################

class User(Resource):

	#Allows the user to log in by creating session data
	def post(self):
		if not request.json:
			abort(400)
		parser = reqparse.RequestParser()
 		try:
	 		parser.add_argument('username', type=str, required=True)
			parser.add_argument('password', type=str, required=True)
			request_params = parser.parse_args()
		except:
			abort(400)
		if 'username' in session:
			response = {'status': 'Already Signed in', 'username': session['username']}
			responseCode = 200
		else:
			try:
				l = ldap.open(settings.LDAP_HOST)
				l.start_tls_s()
				l.simple_bind_s("uid="+request_params['username']+
					", ou=People,ou=fcs,o=unb", request_params['password'])
				session['username'] = request_params['username']
				response = {'status': 'success', 'username': session['username']}
				responseCode = 201
				session.modified = True
			except ldap.LDAPError:
				response = {'status': 'Access denied'}
				responseCode = 401
			finally:
				l.unbind()
		return make_response(jsonify(response), responseCode)

	def get(self):
		if 'username' in session:
			response = ({'username': session['username']}, 200)
		else:
			abort(401)
		return response

	#Allows the user to log out by deleting their session data
	def delete(self):
		try:
			session.clear()
		except:
			abort(400)
		response = {'status': 'success'}
		responseCode = 200
		return make_response(jsonify(response), responseCode)

####################################################################################

class Pictures(Resource):
	# GET: Return all picture resources (note: this includes data associated with the pictures, but not the images themselves)
	def get(self):

		if 'username' in session:
			response = {'status': 'success'}
			responseCode = 200
			try:
				connection = MySQLdb.connect(host=settings.MYSQL_HOST,user=settings.MYSQL_USER,passwd=settings.MYSQL_PASSWD,db=settings.MYSQL_DB, use_unicode=True, charset='utf8')
				cursor = connection.cursor()
				cursor.callproc('getPictures')

				rows = cursor.fetchall()

				field_names = [i[0] for i in cursor.description]
				set = [{description: value for description, value in zip(field_names, row)} for row in rows]
			except Exception as e:
				print(str(e))
				abort(500)

			cursor.close()
			connection.close()
			return make_response(jsonify({'pictures': set}), 200)

		else:
			response = {'status': 'fail'}
			responseCode = 403
			return make_response(jsonify(response), responseCode)

	#POST: Allows the user to create a picture (note: they will send the data for the image file in a different request)
	def post(self):
		if not request.json or not 'username' in session:
			abort(400) # bad request

		# Pull the results out of the json request
		title = request.json['Title'];
		description = request.json['Description'];
		#usernameIN = request.json['Username'];
		usernameIN = session['username']
		try:
			connection = MySQLdb.connect(host=settings.MYSQL_HOST,user=settings.MYSQL_USER,passwd=settings.MYSQL_PASSWD,db=settings.MYSQL_DB, use_unicode=True, charset='utf8')
			cursor = connection.cursor()
			cursor.callproc('postPicture', (title, usernameIN, description,  'NULL'))
			connection.commit() # database was modified, commit the changes
			cursor.close()

			cursor = connection.cursor()
			cursor.callproc('getMaxPictureIDByUsername', [usernameIN])
			rows = cursor.fetchone()
			pic = rows[0]
			responseCode = 201
		except:
			abort(500) # Nondescript server error

		cursor.close()
		connection.close()
		return make_response(jsonify({'status': 'success', 'pictureID': pic}), responseCode)

####################################################################################

class PictureResource(Resource):
	#Allows the user to edit the title and description of a specific picture.
	def put(self, pictureId):
		if 'username' in session:
			title = request.json['Title'];
			description = request.json['Description'];
			try:
				connection = MySQLdb.connect(host=settings.MYSQL_HOST,user=settings.MYSQL_USER,passwd=settings.MYSQL_PASSWD,db=settings.MYSQL_DB, use_unicode=True, charset='utf8')
				cursor = connection.cursor()
				cursor.callproc('getPictureUsernameByID', [pictureId])

				row = cursor.fetchone()
				cursor.close()
				if session['username'] == row[0]:
					cursor = connection.cursor()
					cursor.callproc('updatePictureByID', (title, description,pictureId))
					connection.commit()
				else:
					abort(403)

			except Exception as e:
				print(str(e))
	  			abort(500)

	  		cursor.close()
	  		connection.close()
	  		return make_response(jsonify({'status': 'success'}), 202)

		else:
			response = {'status': 'fail'}
			responseCode = 403
		return make_response(jsonify(response), responseCode)

	#Returns the data assicated with a specific picture (but does not returns the image itself)
	def get(self, pictureId):
		if 'username' in session:
           		try:
				connection = MySQLdb.connect(host=settings.MYSQL_HOST,user=settings.MYSQL_USER,passwd=settings.MYSQL_PASSWD,db=settings.MYSQL_DB, use_unicode=True, charset='utf8')
				cursor = connection.cursor()
				cursor.callproc('getPictureByID',[pictureId])
				rows = cursor.fetchall()
				field_names = [i[0] for i in cursor.description]
				set = [{description: value for description, value in zip(field_names, row)} for row in rows]
				if not set:
					abort(404)
				else:
					responseCode = 200
			except Exception as e:
				print(str(e))
				abort(404)

			cursor.close()
			connection.close()
			return make_response(jsonify({'picture': set}), responseCode)
		else:
			response = {'status': 'fail'}
			responseCode = 403
			return make_response(jsonify(response), responseCode)

	#Deletes a specific picture
	def delete(self, pictureId):
		if 'username' in session:
			try:
				print("this is the number! " + str(pictureId))
				connection = MySQLdb.connect(host=settings.MYSQL_HOST,user=settings.MYSQL_USER,passwd=settings.MYSQL_PASSWD,db=settings.MYSQL_DB, use_unicode=True, charset='utf8')
				cursor = connection.cursor()
				cursor.callproc('getPictureUsernameByID', [pictureId])

				row = cursor.fetchone()
				cursor.close()
				if session['username'] == row[0]:
					cursor = connection.cursor()
					cursor.callproc('deletePicture', [pictureId])
					connection.commit()
				else:
					abort(403)

			except Exception as e:
				print(str(e))
	  			abort(500)

			cursor.close()
			connection.close()
			return make_response(jsonify({'status': 'success'}), 200)
		else:
			response = {'status': 'fail'}
			responseCode = 403
			return make_response(jsonify(response), responseCode)

####################################################################################

class PictureResourceImage(Resource):

	#Given a pictureID, allows the user to submit the data for the image file associated with the picture resource.
	#Image data is sent in binary form, then base 64 encoded and stored as a BLOB in database
	#Note: due to database packet size limitations, image files need to be relatively small. Images greater than 1MB will not properly send.
	#Sample request: curl -H "Content-Type: application/x-www-form-urlencoded" -X PUT --data-binary @"dope_whale.jpg" -b cookie-jar -k https://info3103.cs.unb.ca:57723/pictures/58/image
	def put(self, pictureId):
		if 'username' in session:
			try:
				connection = MySQLdb.connect(host=settings.MYSQL_HOST,user=settings.MYSQL_USER,passwd=settings.MYSQL_PASSWD,db=settings.MYSQL_DB, use_unicode=True, charset='utf8')
				cursor = connection.cursor()
				cursor.callproc('getPictureUsernameByID', [pictureId])

				row = cursor.fetchone()
				cursor.close()
				if session['username'] == row[0]:
					image = request.get_data()
					encoded = base64.b64encode(image)
					cursor = connection.cursor()
					cursor.callproc('updatePictureImageByID', (pictureId,  encoded))
					connection.commit()
				else:
					abort(403)

			except Exception as e:
				print(str(e))
	  			abort(500)

	  		cursor.close()
	  		connection.close()
	  		return make_response(jsonify({'status': 'success'}), 202)

		else:
			response = {'status': 'fail'}
			responseCode = 403
		return make_response(jsonify(response), responseCode)

	#Returns the base64 encoding of the binary data associated with the image file. This essentially is sendinf the image file via text.
	def get(self, pictureId):
		if 'username' in session:
           		try:
				connection = MySQLdb.connect(host=settings.MYSQL_HOST,user=settings.MYSQL_USER,passwd=settings.MYSQL_PASSWD,db=settings.MYSQL_DB, use_unicode=True, charset='utf8')
				cursor = connection.cursor()
				cursor.callproc('getPictureImage',[pictureId])
				data = cursor.fetchone()
				responseCode = 200
			except Exception as e:
				print str(e)
				abort(404)

			cursor.close()
			connection.close()
			#return make_response(jsonify({'image': data[0]}), responseCode)
			response = make_response(data[0])
    			response.headers['Content-Type'] = 'image/jpeg'
    			response.headers['Content-Disposition'] = 'attachment; filename=image' + str(pictureId) + '.jpg'
    			return response

		else:
			response = {'status': 'fail'}
			responseCode = 403

			return make_response(jsonify(response), responseCode)

####################################################################################
#
# Identify/create endpoints and endpoint objects
#
api = Api(app)
api.add_resource(Pictures, '/pictures')
api.add_resource(PictureResource, '/pictures/<int:pictureId>')
api.add_resource(PictureResourceImage, '/pictures/<int:pictureId>/image')
api.add_resource(User, '/signIn')
api.add_resource(Root,'/')

#############################################################################
if __name__ == "__main__":

    context = ('cert.pem', 'key.pem') # Identify the certificates you've generated.
    app.run(host=settings.APP_HOST, port=settings.APP_PORT, ssl_context=context, debug=settings.APP_DEBUG)
