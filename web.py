from flask import Flask, render_template_string, request, redirect
import pandas as pd
import os
import urllib.parse

data_path = os.path.join(os.path.dirname(__file__), "data")

# Initialize Flask app
app = Flask(__name__)

# HTML template for the calendar
calendar_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Select Date</title>
</head>
<body>
    <h1>Select a Date</h1>
    <form action="/display" method="post">
        <label for="date">Date:</label>
        <input type="date" id="date" name="date">
        <input type="submit" value="Submit">
    </form>
</body>
</html>
'''

# Define the HTML template
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSV Data Display</title>
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
        }
        th {
            background-color: #f2f2f2;
            text-align: left;
        }
    </style>
</head>
<body>
    {% if columns and rows %}
    <h2>Tracking data</h2>
    <form action="/view_path" method="get">
        <input type="hidden" name="lat_lng" value="{{ lat_lng }}">
        <button type="submit">View Path on Google Maps</button>
    </form>
    <table>
        <thead>
            <tr>
                {% for column in columns %}
                <th>{{ column }}</th>
                {% endfor %}
            </tr>
        </thead>
        <tbody>
            {% for row in rows %}
            <tr>
                {% for cell in row[:-1] %}
                <td>{{ cell }}</td>
                {% endfor %}
                <td><a href="{{ row[-1] }}" target="_blank">Map Link</a></td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% endif %}
</body>
</html>
"""

def process_csv(file):
    # Load and process the CSV file
    file_path = data_path + "/" + file
    data = pd.read_csv(file_path)
    columns_to_display = ["VehID", "stime", "lat", "lng", "velocity", "TotalDistance", "trangThai", "PowerSupply"]
    data = data[columns_to_display]

    # Convert the time column to a datetime object and sort by time
    data["stime"] = pd.to_datetime(data["stime"], format="%H:%M:%S %d/%m/%Y")
    data = data.sort_values(by="stime", ascending=False)

    # Add a Google Maps link column
    def create_google_maps_link(lat, lng):
        return f"https://www.google.com/maps?q={lat},{lng}"

    data["GoogleMapsLink"] = data.apply(lambda row: create_google_maps_link(row["lat"], row["lng"]), axis=1)

    # Prepare latitudes and longitudes for viewing the path
    lat_lng = "|".join([f"{lat},{lng}" for lat, lng in zip(data["lat"], data["lng"])])
    
    return data, lat_lng

# Define the route for the homepage
@app.route('/')
def index():
    return render_template_string(calendar_template, columns=None, rows=None, lat_lng=None)

# Define the route to display the file
@app.route('/display', methods=['POST'])
def display_file():
    file = str(request.form.get('date')) + '.csv'
    try:
        # Process the uploaded CSV file
        data, lat_lng = process_csv(file)
        rows = data.values.tolist()
        columns = data.columns.tolist()
        return render_template_string(html_template, columns=columns, rows=rows, lat_lng=lat_lng)
    except Exception as e:
        return f"Error: {str(e)}"

# Define the route to view the path on Google Maps
@app.route('/view_path', methods=['GET'])
def view_path():
    lat_lng = request.args.get('lat_lng')
    if lat_lng:
        # Create the Google Maps URL with polyline of the vehicle path
        base_url = "https://www.google.com/maps/dir/?api=1"
        path_url = base_url + "&waypoints=" + urllib.parse.quote(lat_lng)
        return redirect(path_url)
    return "No path data found"

if __name__ == '__main__':
    app.run(debug=True)
