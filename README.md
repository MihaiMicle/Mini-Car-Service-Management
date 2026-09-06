# Mini Car Service Management

A lightweight desktop app for a car service shop to log vehicles and their repair/maintenance history — no server, no cloud, just Python and a local SQLite file. Built with Tkinter for the interface and SQLite for storage. The UI is in Romanian (Service Auto - Istoric Intervenții), matching its intended use in a Romanian auto repair shop.

# Features
Add an intervention — enter a plate number, vehicle details, and a description of the work done. If the plate number already exists, the new intervention is linked to the existing car instead of duplicating it.
Auto-fill on known plates — leaving the plate number field auto-fills the vehicle's VIN, make, model, year, engine size, and power, plus the last known client name and phone number, if that plate has been seen before.
Search history by plate — pull up every recorded intervention for a given car, most recent first.
Edit an intervention — update mileage, date, invoice number, parts supplier, client info, or description for any past entry.
Delete an intervention — remove a record after confirmation.
Detail view — selecting a row shows the full description and client details below the table.
Tech stack
Python 3
Tkinter (tkinter, ttk) — GUI, standard library
SQLite (sqlite3) — local storage, standard library

No third-party packages are required.

# Project structure
# Mini-Car-Service-Management/

├── main.py       # Entry point — launches the app

├── gui.py        # Tkinter interface (ServiceAutoApp): windows, forms, event handlers

├── database.py   # Data layer: SQLite connection, schema, and all queries

└── README.md

The project is split by responsibility so the interface and the data logic can be read, tested, and changed independently:

database.py knows nothing about Tkinter. It exposes plain functions (add_masina_si_interventie, get_istoric_by_plate, update_interventie, etc.) that take a connection and plain values/dicts and return plain tuples.
gui.py knows nothing about SQL. ServiceAutoApp builds the window and wires each button/field to a handler, and every handler calls into database.py for reads and writes.
main.py just creates a ServiceAutoApp and starts it.
Getting started

# Requirements
Python 3.8+ with Tkinter available (bundled with most Python installers; on Debian/Ubuntu you may need sudo apt install python3-tk).

bash
git clone https://github.com/MihaiMicle/Mini-Car-Service-Management.git
cd Mini-Car-Service-Management
python main.py

On first run, database.py automatically creates service_auto.db in the working directory with the required tables — no setup step needed.

Data model

Two tables, linked by masina_id:

masini — one row per vehicle: plate number, VIN, make, model, year, engine size (cm³), power (kW).
interventii — one row per service visit: linked vehicle, date, description, mileage, invoice number, parts supplier, and the client's name and phone number at the time of that visit.
License

No license has been specified for this project yet.
