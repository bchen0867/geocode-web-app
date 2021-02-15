from flask import Flask, render_template, request, send_file
from flask_bootstrap import Bootstrap
import pandas as pd
from geopy.geocoders import ArcGIS

app = Flask(__name__)
Bootstrap(app)


def file_validation(df):
    # check if there's address column in the file
    if "Address" in list(df.columns) or "address" in list(df.columns):
        return True
    return False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/success-table", methods=["POST"])
def success():
    global file
    if request.method == "POST":
        file = request.files["file"]

        # reading the data as a dataframe
        try:
            df = pd.read_csv(file)
        except:
            fail_msg1 = "Submission Failed! \nPlease choose a file to upload."
            print(fail_msg1)
            return render_template("index.html", text=fail_msg1)

        # check if the data contains address column
        if not file_validation(df):
            fail_msg2 = "Submission Failed! \nPlease make sure your file contains a column named 'address' or 'Address'!"
            return render_template("index.html", text=fail_msg2)

        # geocode the dataframe
        nom = ArcGIS()

        df['Address'] = df['Address'] + ',' + df['City'] + ',' + df['State'] + ',' + df['Country']
        df['Coordinates'] = df['Address'].apply(nom.geocode)
        df['Latitude'] = df['Coordinates'].apply(lambda x: x.latitude if x is not None else None)
        df['Longitude'] = df['Coordinates'].apply(lambda x: x.longitude if x is not None else None)

        df = df.drop("Coordinates", 1)
        df.to_csv("uploads/geocoded.csv", index=None)

        message = df.to_html(justify="center", classes="table table-hover")

        return render_template("index.html", text=message, btn="download.html")
    print("not meeting the condition!!!!")
    return render_template("fail.html")


@app.route("/download")
def download():
    return send_file("uploads\\geocoded.csv", attachment_filename="geocodeFile.csv", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
