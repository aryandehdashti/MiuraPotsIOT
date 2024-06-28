from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import asyncio
import threading
from bot import bot, send_message

app = Flask(__name__)

MAX_SENSORS = 5
DATABASE = "sensors.db"

async def send_alert(potName):
    await send_message(potName)

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def add_sensor(name, inputID):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sensors (name, inputID) VALUES (?, ?)", (name, inputID))
    conn.commit()
    conn.close()

def get_sensors():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sensors")
    sensors = cursor.fetchall()
    conn.close()
    return sensors

def get_sensor(sensor_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sensors WHERE name = ?", (sensor_name,))
    sensor = cursor.fetchone()
    conn.close()
    return sensor

def update_sensor(name, inputID, original_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE sensors SET name = ?, inputID = ? WHERE name = ?", (name, inputID, original_name))
    conn.commit()
    conn.close()

def delete_sensor(sensor_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sensors WHERE name = ?", (sensor_name,))
    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def sensors():
    if request.method == "POST":
        if len(get_sensors()) >= MAX_SENSORS:
            return "Maximum sensor limit reached!", 400

        new_sensor_name = request.form.get("sensor_name")
        new_sensor_inputID = int(request.form.get("sensor_inputID"))
        add_sensor(new_sensor_name, new_sensor_inputID)
        return redirect(url_for("sensors"))  
    else:
        sensors = get_sensors()
        return render_template("sensors.html", sensors=sensors)
    
@app.route("/edit/<string:sensor_name>", methods=["POST"])
def edit_sensor(sensor_name):
    new_name = request.form.get("sensor_name")
    new_inputID = int(request.form.get("sensor_inputID"))
    update_sensor(new_name, new_inputID, sensor_name)
    return redirect(url_for("sensors"))

@app.route("/delete/<string:sensor_name>", methods=["POST"])
def delete_sensor_route(sensor_name):
    delete_sensor(sensor_name)
    return redirect(url_for("sensors"))

@app.route("/sensors", methods=["POST"])
def receive_sensor_data():
    if request.method == "POST":
        received_data = request.get_json()
        active_sensors = get_sensors()
        for profile in active_sensors:
            inputID, name = profile["inputID"], profile["name"]
            for data in received_data:
                if str(inputID) in data and received_data[data]:
                    asyncio.run_coroutine_threadsafe(send_alert(name), loop)
                    break

        return "Sensor data received!", 200
    else:
        return "Method not allowed", 405

def create_sensors_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS sensors (
        inputID INTEGER NOT NULL,
        name TEXT PRIMARY KEY NOT NULL
    )''')
    conn.commit()
    conn.close()

def start_event_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

create_sensors_table()

loop = asyncio.new_event_loop()
t = threading.Thread(target=start_event_loop, args=(loop,))
t.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
