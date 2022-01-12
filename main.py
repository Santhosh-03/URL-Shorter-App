from flask import Flask, render_template, request, redirect, url_for, abort, flash
import random, os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'abarakadabra'

##############################

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://lehwatanwaoydj:055b01d50772ecd5ba272189fece969a00dc1520997ed80bbb4d3ff72ed874ce@ec2-34-236-87-247.compute-1.amazonaws.com:5432/da10cs3puucbkh'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
##############################


##############################

class URLSHORT(db.Model):

    __tablename__ = 'short_urls'
    id = db.Column(db.Integer, primary_key = True)
    long_url = db.Column(db.Text)
    short_code = db.Column(db.Text)
    short_url = db.Column(db.Text)

    def __init__(self, long_url, short_code, short_url):
        self.long_url = long_url
        self.short_code = short_code
        self.short_url = short_url
    
    def __repr__(self):
        return 'Original URL --> {}\t\t Shortened URL --> {}'.format(self.long_url, self.short_url)


##############################

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/your_url', methods = ['GET', 'POST'])
def your_url():
    if request.method =='GET':
        return redirect(url_for('index'))
    else:
        original_url = request.form.get('url')
        lower_case = [chr(char) for char in range(97, 123)]
        upper_case = [chr(char) for char in range(65, 91)]
        numbers = list(map(str, range(0, 10)))
        dataset = lower_case + upper_case + numbers
        urls =  URLSHORT.query.filter_by(long_url = original_url).first()
        if urls is not None:
            if original_url == urls.long_url:
                id = urls.id
                flash('The requested URL has already been shortened. You can find it at id no %d' %id)
                return redirect(url_for('history'))
        else:
            short_code = ''   
            for _ in range(6):
                short_code += random.choice(dataset)
            final_short_url = 'https://url-short-application.herokuapp.com/' + short_code
            new_url = URLSHORT(original_url, short_code, final_short_url)
            db.session.add(new_url)
            db.session.commit()
            return render_template('your_url.html', short_code = short_code)

@app.route('/history')
def history():
    urls = URLSHORT.query.all()
    return render_template('history.html', urls = urls)

@app.route('/<string:short_code>')
def redirect_to_url(short_code):
    urls =  URLSHORT.query.filter_by(short_code = short_code).first()
    if urls:
        return redirect(urls.long_url)
    else:
        abort(404)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

