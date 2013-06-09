import sys
from os import listdir
from os.path import isfile, join, dirname


from flask import Flask
from flask import Response, send_file, request, abort, url_for, redirect

import re

import json

import Image
import tempdir

import atexit

from werkzeug import SharedDataMiddleware


watch_path = sys.argv[1]

app = Flask(__name__)

app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
  '/': join(dirname(__file__), 'static')
})


jpg_re = re.compile(r".*\.jpg$",flags=re.IGNORECASE)

images = [ f for f in listdir(watch_path) if (isfile(join(watch_path,f)) and jpg_re.match(f)) ]

thumbnails_dir = tempdir.TempDir()

page_structure = {}

for infile in images:
	page_structure[infile] = { "id" : infile, "name" : infile, "pages" : [infile] }
	try:
		im = Image.open(join(watch_path,infile))
		size = 200,500
		im.thumbnail(size)
		im.save(join(thumbnails_dir.name,infile), "JPEG")
	except IOError,e:
		print str(e)
		print "cannot create thumbnail for", infile

print images

def cleanup_temp():
	thumbnails_dir.dissolve()

atexit.register(cleanup_temp)

@app.route("/")
def index():
    return redirect('/index.html')

@app.route("/pages/<image_name>",methods=['DELETE'])
def delete_pages(image_name):
	if image_name not in page_structure:
		abort(404)
		return
	if image_name in request.json:
		abort(500)
		return
	for page in request.json:
		if page in page_structure[image_name]['pages']:
			page_structure[image_name]['pages'].remove(page)
			page_structure[page] = { "id" : page, "name" : page, "pages" : [page] }

	return Response(json.dumps(page_structure[image_name]),mimetype="application/json")


@app.route("/pages/<image_name>",methods=['GET'])
def get_pages(image_name):
	if image_name not in page_structure:
		abort(404)
		return
	return Response(json.dumps(page_structure[image_name]),mimetype="application/json")

@app.route("/pages/<image_name>",methods=['PUT'])
def put_pages(image_name):
	if image_name not in page_structure:
		abort(404)
		return

	if pages in request.json:
		page_structure[image_name]['pages'] = request.json['pages']

	if name in request.json:
		page_structure[image_name]['name'] = request.json['name']

	return Response(json.dumps(page_structure[image_name]),mimetype="application/json")

@app.route("/pages/<image_name>",methods=['POST'])
def post_pages(image_name):
	if image_name not in page_structure:
		abort(404)
		return
	for page in request.json:
		if page in page_structure and page != image_name:
			del page_structure[page]
			page_structure[image_name]['pages'].append(page)
	return Response(json.dumps(page_structure[image_name]),mimetype="application/json")

@app.route("/pages")
def merged_list():
	return Response(json.dumps(page_structure),mimetype='application/json')

@app.route("/imagelist")
def image_list():
	return Response(json.dumps(images), mimetype='application/json')

@app.route("/images/<original>")
def original(original):
	if original not in images:
		abort(404)
		return
	print join(watch_path,original)
	return send_file(join(watch_path,original))


@app.route("/thumbnails/<image>")
def thumbnail(image):
	if image not in images:
		return
	return send_file(join(thumbnails_dir.name,image))

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True,use_reloader=False)

