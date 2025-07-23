Train Database Management System

A Flask-based Train Database Management System built using Python, SQLite, and HTML/CSS. The system allows users to view train schedules, select seats, and track live train status, while administrators can manage train, station, and passenger data through an interactive web interface.
Features
✅ Admin Features

   * Add, edit, and delete train details.

   * Manage station and passenger information.

   * Update train schedules and destinations.

✅ User Features

   * View available trains and schedules.

   * Seat selection and booking simulation.

   * Basic live tracker to check train status.

✅ General

   * Simple, interactive UI built with HTML templates and CSS.

   * Data stored in SQLite database (trains.db).

   * Lightweight Flask backend for routing and database operations.

Technology Stack
Component	Technology
Backend	Python (Flask Framework)
Database	SQLite
Frontend	HTML, CSS (basic styling)
Other	Jinja2 templates for dynamic pages
Installation & Setup
1. Clone the Repository

git clone https://github.com/your-username/train-database-management.git
cd train-database-management

2. Create a Virtual Environment & Install Requirements

python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install flask

3. Run the Application

python app.py

Then visit the link generated in terminal in your browser.
Project Structure

|-- app.py                 # Main Flask application
|-- trains.db               # SQLite database
|-- templates/              # HTML templates
|   |-- login.html
|   |-- adminmenu.html
|   |-- seat_selection.html
|   |-- live tracker.html
|   |-- ...
|-- static/                 # CSS and images
|   |-- styles.css
|   |-- train_gif.gif

Future Enhancements

   * Add user authentication for booking.

   * Real-time seat booking and cancellation.

   * Better live tracking with API integration.

   * Migration to MySQL for larger datasets.

License

This project is open-source and free to modify.
