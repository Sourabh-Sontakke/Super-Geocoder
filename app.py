from flask import Flask, render_template, request, send_file
import geopy
import pandas
from geopy.geocoders import Nominatim
from werkzeug.utils import secure_filename

app = Flask(__name__)

geopy.geocoders.options.default_user_agent = "my"
nom = Nominatim(user_agent="my")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/success', methods=['POST'])
def success():
    global file
    if request.method == "POST":
        file = request.files['csv_file']
        file.save(secure_filename(file.filename))
        data = pandas.read_csv(file.filename)
        try:
            pin = list(data['Pincode'])
            lat = []
            lon = []
            for p in pin:
                try:
                    n = nom.geocode(p)
                    lat.append(n.latitude)
                    lon.append(n.longitude)
                except AttributeError:
                    lat.append(None)
                    lon.append(None)
            
            data['Latitude'] = lat
            data['Longitude'] = lon
            return render_template("index.html", button="download.html", table=data.to_html())
        except KeyError:
            return render_template("index.html", msg="Please make sure your file has Pincode column in it.")
        

@app.route('/download')
def download():
    return send_file(file.filename, download_name="csv_with_lat_lon.csv", as_attachment=True)

if __name__ == "__main__":
    app.debug = True
    app.run()