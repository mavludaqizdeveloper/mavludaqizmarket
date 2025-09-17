from flask import Flask, render_template, jsonify, request, url_for, send_from_directory
import sqlite3
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def connent():
    conn = sqlite3.connect("database/data.db")
    cursor = conn.cursor()
    cursor.row_factory = sqlite3.Row
    
    return conn

def add_table():
    conn = connent()
    cursor = conn.cursor()
    
    conn = sqlite3.connect("database/data.db")
    cursor.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, image_url TEXT, name TEXT, about TEXT, price INT, card_price INT, stars INT)")
    conn.commit()
    conn.close()
add_table()

@app.route("/", methods=['GET'])
def home_view():
    return jsonify({"message": "Hammasi joyida!"})

@app.route("/api/products", methods=["POST"])
def add_product():
    conn = connent()
    cursor = conn.cursor()
    cursor.row_factory = sqlite3.Row
    
    
    image = request.files['image']
    imagepath = os.path.join(UPLOAD_FOLDER, image.filename)
    name = request.form.get('name')
    about = request.form.get('about')
    price = request.form.get('price')
    card_price = request.form.get('card_price')
    stars = request.form.get('stars')
    image.save(imagepath)
    
    cursor.execute("INSERT INTO products(image_url, name, about, price,card_price,stars) VALUES(?,?,?,?,?,?)", (image.filename, name, about, price, card_price, stars))

    conn.commit()
    
    try:
        return jsonify({"message": "mahsulot qo'shildi ✅", 'status': 200})
    except Exception as e:
        return jsonify({'message': f"{e}", "status": 500}), 500

@app.route("/api/products", methods=["GET"])
def product_view():
    conn = connent()
    cursor = conn.cursor()
    cursor.row_factory = sqlite3.Row
    
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    conn.close()
    product_list = []
    for row in rows:
        item = dict(row)
        item["image_url"] = url_for("uploaded_file", filename=row['image_url'], _external=True)
        product_list.append(item)
    return jsonify(product_list)

@app.route("/api/products/<path:filename>", methods=['GET'])
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
if __name__=="__main__":
    app.run(debug=True, port=8800)