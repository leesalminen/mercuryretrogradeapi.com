from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from skyfield.api import Topos, load

app = Flask(__name__)
CORS(app)

def is_mercury_retrograde(date):
    ts = load.timescale()
    eph = load('de440.bsp')

    t = ts.utc(date.year, date.month, date.day)
    mercury = eph['mercury']
    earth = eph['earth']

    mercury_astrometric = earth.at(t).observe(mercury)
    ra, dec, distance = mercury_astrometric.radec()

    t_plus_1_day = ts.utc(date.year, date.month, date.day) + timedelta(days=1)
    mercury_astrometric_plus_1_day = earth.at(t_plus_1_day).observe(mercury)
    ra_plus_1_day, dec_plus_1_day, distance_plus_1_day = mercury_astrometric_plus_1_day.radec()

    return bool(ra_plus_1_day.hours < ra.hours)

@app.route('/', methods=['GET'])
@cross_origin()
def mercury_retrograde():
    date_str = request.args.get('date', datetime.today().strftime('%Y-%m-%d'))
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use 'YYYY-MM-DD' format."}), 400

    is_retrograde = is_mercury_retrograde(date)
    return jsonify({"is_retrograde": is_retrograde})

@app.route('/about.html', methods=['GET'])
def about():
    return app.send_static_file('about.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0')