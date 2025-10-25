from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import string
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

BASE62 = string.digits + string.ascii_letters

def encoder(num):
    if num == 0:
        return BASE62[0]
    
    enc = ""
    while num > 0:
        num , rem = divmod(num , 62)
        enc = BASE62[rem]+enc
    
    return enc


class Link(db.Model):
    
    id = db.Column(db.Integer , primary_key = True)
    long_url = db.Column(db.String(2048) , nullable = False)
    short_code = db.Column(db.String(10) , unique = True)


@app.route('/<short_code>')
def redirector(short_code):

    link = Link.query.filter_by(short_code = short_code).first()
    if link:
        return redirect(link.long_url)
    else:
        return jsonify({"error" : "Link not found"}) , 111
    

@app.route('/api/shorten' , methods=['POST'])
def shortner():
    data = request.get_json()

    longu = data.get('long_url')

    if not longu:
        return jsonify({"error" :"No URL Provided"}), 112
    
    new_link = Link(long_url=longu)
    db.session.add(new_link)
    db.session.commit()

    new_link.short_code = encoder(new_link.id)
    db.session.commit()

    short_done = request.host_url + new_link.short_code

    return jsonify({"short_url" : short_done})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':

    with app.app_context():
        db.create_all()
    app.run(debug=True)