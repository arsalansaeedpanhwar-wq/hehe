from flask import Flask, render_template, request, send_file
import qrcode
import os
from routeros_api import RouterOsApiPool
from fpdf import FPDF
import random
import string


app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'static/qr_images'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# --- MikroTik Configuration ---
ROUTER_IP = '192.168.88.1'
ROUTER_USER = 'admin'
ROUTER_PASSWORD = 'yourpassword'
API_PORT = 8728


def create_router_connection():
try:
connection = RouterOsApiPool(
ROUTER_IP,
username=ROUTER_USER,
password=ROUTER_PASSWORD,
port=API_PORT,
plaintext_login=True
)
api = connection.get_api()
return api, connection
except Exception as e:
print("Router connection failed:", e)
return None, None


def random_string(length=6):
return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


@app.route('/')
def index():
return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
count = int(request.form['count'])
voucher_list = []


api, connection = create_router_connection()


for _ in range(count):
username = random_string(6)
password = random_string(8)


qr_filename = f"{username}.png"
qr_path = os.path.join(app.config['UPLOAD_FOLDER'], qr_filename)
img = qrcode.make(f"{username}:{password}")
img.save(qr_path)


if api:
try:
hotspot_users = api.get_resource('/ip/hotspot/user')
hotspot_users.add(name=username, password=password, profile='default')
except Exception as e:
print(f"Failed to add user {username}:", e)


voucher_list.append({'username': username, 'password': password, 'qr': qr_path})


if connection:
connection.disconnect()


pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
app.run(debug=True)
