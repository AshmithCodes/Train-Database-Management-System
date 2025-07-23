from flask import Flask, render_template, redirect, url_for, request, flash
from flask_mail import Mail, Message #autosends email
from PIL import Image, ImageDraw, ImageFont #PIL - IMAGE TO PDF
from reportlab.pdfgen import canvas 
from reportlab.lib.pagesizes import letter
from io import BytesIO
import sqlite3 #sql connectivity
import os
from tempfile import NamedTemporaryFile
import werkzeug #improves security
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key' 

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'appstfu123@gmail.com'  # replace with your email
app.config['MAIL_PASSWORD'] = 'qbqm nspb bacu weir'  # replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = 'appstfu123@gmail.com'  # replace with your email

mail = Mail(app)

def generate_ticket_image(ticket_data):
    """Generate a ticket image and return it as a BytesIO object."""
    img = Image.new('RGB', (800, 600), color=(240, 248, 255))  # Light background
    d = ImageDraw.Draw(img)
    
    # Define fonts and colors
    header_font = ImageFont.load_default()  # Replace with a custom font if available
    details_font = ImageFont.load_default()
    title_font = ImageFont.load_default()
    small_font = ImageFont.load_default()
    
    primary_color = (0, 0, 0)  # MMT-like blue
    secondary_color = (0, 0, 0)  # Black for text
    
    # Add a header section with a logo-like area
    d.rectangle([(0, 0), (800, 80)], fill=primary_color)
    
    # Add Ticket Confirmation Title
    d.text((50, 100), f"Train Ticket Confirmation", fill=primary_color, font=title_font)

    # Draw a line to separate sections
    d.line((50, 140, 750, 140), fill=primary_color, width=2)
    
    d.text((50, 160), f"Train ID: {ticket_data['train_id']}", fill=secondary_color, font=details_font)
    d.text((50, 190), f"From: {ticket_data['from_city']}", fill=secondary_color, font=details_font)
    d.text((50, 220), f"To: {ticket_data['to_city']}", fill=secondary_color, font=details_font)
    d.text((50, 250), f"Travel Date: {ticket_data['travel_date']}", fill=secondary_color, font=details_font)
    d.text((50, 280), f"Departure Time: {ticket_data['departure_time']}", fill=secondary_color, font=details_font)
    d.text((50, 310), f"Arrival Time: {ticket_data['arrival_time']}", fill=secondary_color, font=details_font)
    d.text((50, 340), f"Train Operator: {ticket_data['train_operator']}", fill=secondary_color, font=details_font)
    d.text((50, 380), f"Passengers: {ticket_data['passenger_count']}", fill=secondary_color, font=details_font)
    d.text((50, 410), f"Selected Seats: {ticket_data['selected_seats']}", fill=secondary_color, font=details_font)
    d.text((50, 440), f"Total Price: INR {ticket_data['total_price']}", fill=(255, 69, 0), font=details_font)
    

    # Save to BytesIO
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return img_buffer

def convert_image_to_pdf(img_buffer):
    """Convert an image in BytesIO format to a PDF."""
    pdf_buffer = BytesIO()

    # Create a temporary file to save the image
    with NamedTemporaryFile(suffix='.png', delete=False) as temp_img_file:
        temp_img_file.write(img_buffer.getvalue())
        temp_img_file_path = temp_img_file.name

    # Create a PDF from the image using ReportLab
    pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=letter)
    pdf_canvas.drawImage(temp_img_file_path, 50, 500, width=500, height=300)  # Adjust as needed
    pdf_canvas.showPage()
    pdf_canvas.save()

    # Clean up the temporary image file
    os.remove(temp_img_file_path)

    pdf_buffer.seek(0)
    
    return pdf_buffer
 
def init_db():
    conn = sqlite3.connect('trains.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS trains (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,   
                        from_city TEXT NOT NULL,
                        to_city TEXT NOT NULL,
                        travel_date TEXT NOT NULL,z
                        departure_time TEXT NOT NULL,
                        arrival_time TEXT NOT NULL,
                        train_operator TEXT NOT NULL,
                        travel_time TEXT NOT NULL,
                        changes INTEGER NOT NULL,
                        price REAL NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS stationsline (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        station_name TEXT NOT NULL,
                        station_code TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL)''')
    conn.commit()
    conn.close()


init_db()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('name')  # Changed from 'name' to 'username' for clarity
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            flash('Passwords do not match', 'error')


        conn = sqlite3.connect('trains.db')
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM users WHERE username=?', (username,))
        result = cursor.fetchone()
        conn.close()

        if result and check_password_hash(result[0], password):  # Verify hashed password
            return redirect(url_for('destination'))
        elif username == 'admin' and password == 'password':
            return redirect(url_for('adminmenu'))
        else:
            flash('Incorrect username or password', 'error')

    return render_template('login.html')

@app.route('/create-password', methods=['GET', 'POST'])
def create_password():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('create_password'))

        # Hash the password and store user details
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        try:
            conn = sqlite3.connect('trains.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            conn.close()

            flash('Password created successfully! You can now log in.', 'success')
            return redirect(url_for('login'))  # Redirect to login or another page
        except sqlite3.IntegrityError:
            return redirect(url_for('login'))

            # flash('Username already exists. Please choose a different username.', 'error')

    return render_template('create_password.html')

@app.route('/destination', methods=['GET', 'POST'])
def destination():
    if request.method == 'POST':
        from_city = request.form.get('from')
        to_city = request.form.get('to')
        travel_date = request.form.get('date')

        
        return redirect(url_for('display', from_city=from_city, to_city=to_city, date=travel_date))

    return render_template('destination.html')

@app.route('/display')
def display():
    from_city = request.args.get('from_city')
    to_city = request.args.get('to_city')
    travel_date = request.args.get('date')

    conn = sqlite3.connect('trains.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM trains WHERE from_city=? AND to_city=? AND travel_date=?''',
                   (from_city, to_city, travel_date))
    trains = cursor.fetchall()
    conn.close()

    if not trains:
        flash('No trains found for the given criteria.', 'info')

    return render_template('display.html', trains=trains, from_city=from_city, to_city=to_city, date=travel_date)


@app.route('/getinfo', methods=['GET', 'POST'])
def getinfo():
    if request.method == 'POST':
        try:
            
            from_city = request.form['from']
            to_city = request.form['to']
            travel_date = request.form['date']
            departure_time = request.form['departure_time']
            arrival_time = request.form['arrival_time']
            train_operator = request.form['train_operator']
            travel_time = request.form['travel_time']
            changes = int(request.form['changes'])  
            price = float(request.form['price'])   

           
            conn = sqlite3.connect('trains.db')
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO trains (from_city, to_city, travel_date, departure_time, arrival_time, 
                              train_operator, travel_time, changes, price)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (from_city, to_city, travel_date, departure_time, arrival_time, 
                            train_operator, travel_time, changes, price))
            conn.commit()
            conn.close()

            
            return redirect(url_for('display', from_city=from_city, to_city=to_city, date=travel_date))
        except ValueError as e:
            flash(f'ValueError: {e}', 'error')
        except Exception as e:
            flash(f'An error occurred: {e}', 'error')

   
    conn = sqlite3.connect('trains.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM stations')
    stations = cursor.fetchall()
    conn.close()

    return render_template('getinfo.html', stations=stations)

@app.route('/trains', methods=['GET'])
def show_trains():
    try:
        conn = sqlite3.connect('trains.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM trains')
        trains = cursor.fetchall()
        conn.close()
        
        if not trains:
            flash('No trains found in the database.', 'info')

        return render_template('show_trains.html', trains=trains)
    
    except Exception as e:
        flash(f'An error occurred while fetching trains: {e}', 'error')
        return redirect(url_for('adminmenu'))


@app.route('/delete_train/<int:train_id>', methods=['POST'])
def delete_train(train_id):
    conn = sqlite3.connect('trains.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM trains WHERE id=?', (train_id,))
    conn.commit()
    conn.close()
    
    flash('Train deleted successfully!', 'success')
    return redirect(url_for('show_trains'))


@app.route('/train/<int:train_id>')
def train_details(train_id):
    conn = sqlite3.connect('trains.db')
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM trains WHERE id=?''', (train_id,))
    train = cursor.fetchone()

    conn.close()

    if train:
        return render_template('train_details.html', train=train)
    else:
        flash("Train not found", 'error')
        return redirect(url_for('display'))

@app.route('/main_details', methods=['GET', 'POST'])
def main_details():
    return render_template('main_details.html') 

@app.route('/add_passengers')
def add_passengers():
    return render_template('add_passengers.html')  

@app.route('/seat_selection/<int:train_id>', methods=['GET', 'POST'])
def seat_selection(train_id):
    if request.method == 'POST':
        passenger_count = int(request.form.get('passenger_count'))
        selected_seats = request.form.getlist('selected_seats')

        # Check if the number of selected seats matches the passenger count
        if len(selected_seats) != passenger_count:
            flash('Error: Number of selected seats does not match the number of passengers.', 'error')
            return redirect(url_for('seat_selection', train_id=train_id))

        # Redirect to summary page after selection
        return redirect(url_for('summary', train_id=train_id, passenger_count=passenger_count, selected_seats=','.join(selected_seats)))

    return render_template('seat_selection.html', train_id=train_id)

@app.route('/summary/<int:train_id>', methods=['GET', 'POST'])
def summary(train_id):
    passenger_count = request.args.get('passenger_count')
    selected_seats = request.args.get('selected_seats')

    # Fetch train details for the summary
    conn = sqlite3.connect('trains.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM trains WHERE id=?', (train_id,))
    train = cursor.fetchone()
    conn.close()
    
    if not train:
        flash("Train not found", 'error')
        return redirect(url_for('display'))

    # Assuming price is at index 9 (the last column in the table definition)
    price_per_ticket = train[9]
    total_price = price_per_ticket * int(passenger_count)  # Calculate total price

    # Render the summary page
    return render_template(
        'summary.html',
        train=train,
        passenger_count=passenger_count,
        selected_seats=selected_seats,
        total_price=total_price
    )



@app.route('/add_station', methods=['GET', 'POST'])
def add_station():
    if request.method == 'POST':
        station_names = request.form.getlist('station_name[]')
        station_codes = request.form.getlist('station_code[]')

        # Store the stations in the database
        conn = sqlite3.connect('trains.db')
        cursor = conn.cursor()

        for name, code in zip(station_names, station_codes):
            cursor.execute('INSERT INTO stationsline (station_name, station_code) VALUES (?, ?)', (name, code))

        conn.commit()
        conn.close()

        flash('Stations added successfully!', 'success')
        return redirect(url_for('getinfo'))  # Redirect back to the get info page

    return render_template('add_station.html')

@app.route('/send_ticket', methods=['POST'])
def send_ticket():
    ticket_data = {
        "train_id": request.form.get('train_id', ''),
        "from_city": request.form.get('from_city', ''),
        "to_city": request.form.get('to_city', ''),
        "travel_date": request.form.get('travel_date', ''),
        "departure_time": request.form.get('departure_time', ''),
        "arrival_time": request.form.get('arrival_time', ''),
        "train_operator": request.form.get('train_operator', ''),
        "passenger_count": request.form.get('passenger_count', '0'),
        "selected_seats": request.form.get('selected_seats', ''),
        "total_price": request.form.get('total_price', '0')
    }

    try:
        # Generate ticket image and convert to PDF
        img_buffer = generate_ticket_image(ticket_data)
        pdf_buffer = convert_image_to_pdf(img_buffer)
        pdf_buffer.seek(0)

        # Specify the email address you want to send the PDF to
        recipient_email = 'appstfu123@gmail.com'

        # Create the email message
        msg = Message('Your Train Ticket Confirmation', recipients=[recipient_email])
        msg.body = (f"Here is your ticket for Train {ticket_data['train_id']} "
                    f"from {ticket_data['from_city']} to {ticket_data['to_city']}.")

        # Attach the PDF to the email
        msg.attach('ticket.pdf', 'application/pdf', pdf_buffer.read())

        # Send the email
        mail.send(msg)

        return f"Ticket confirmation for Train {ticket_data['train_id']} has been sent to {recipient_email}."

    except Exception as e:
        app.logger.error(f"Error sending ticket: {e}")
        flash(f"An error occurred while sending the ticket: {e}", "error")
        return redirect(url_for('destination'))
    
@app.route('/adminmenu', methods=['GET','POST'])
def adminmenu():
        conn = sqlite3.connect('trains.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM trains')
        trains = cursor.fetchall()
        conn.close()
        
        return render_template('adminmenu.html', trains=trains)
@app.route('/edit_train/<int:train_id>', methods=['GET', 'POST'])
def edit_train(train_id):
    conn = sqlite3.connect('trains.db')
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # Get data from form
        from_city = request.form.get('from_city')
        to_city = request.form.get('to_city')
        travel_date = request.form.get('travel_date')
        departure_time = request.form.get('departure_time')
        arrival_time = request.form.get('arrival_time')
        train_operator = request.form.get('train_operator')
        travel_time = request.form.get('travel_time')
        changes = int(request.form.get('changes'))
        price = float(request.form.get('price'))

        # Update the train record in the database
        cursor.execute('''UPDATE trains SET from_city=?, to_city=?, travel_date=?, 
                          departure_time=?, arrival_time=?, train_operator=?, 
                          travel_time=?, changes=?, price=? WHERE id=?''',
                       (from_city, to_city, travel_date, departure_time, 
                        arrival_time, train_operator, travel_time, changes, price, train_id))
        conn.commit()
        conn.close()
        flash('Train details updated successfully!', 'success')
        return redirect(url_for('adminmenu'))  # Redirect after edit

    # If GET request, fetch the train details to pre-fill the form
    cursor.execute('SELECT * FROM trains WHERE id=?', (train_id,))
    train = cursor.fetchone()
    conn.close()
    return render_template('edit_train.html', train=train)

    
    
if __name__ == '__main__':
    app.run(debug=True)
    