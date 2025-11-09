# Airline Reservation System

![Airline Reservation System](assets/banner.svg)

Simple Airline Reservation System — a minimal, local demo app to search and book flights.

This project uses Python + Streamlit for the UI and MySQL for data storage. The app includes an automatic database setup routine that creates the database, tables, and sample data on first run.

---

## Quick Start (Windows PowerShell)

1. Create and activate a virtual environment

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
```

2. Install dependencies

```powershell
pip install -r requirements.txt
```

3. Add database credentials

Create a `.env` file in the project root (or copy `.env.example`) with these keys:

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=airline_reservation_system
```

4. Start MySQL server and run the app

```powershell
# ensure MySQL service is running, then
streamlit run app.py
```

5. Open the UI

Open your browser at `http://localhost:8501` (Streamlit may choose another free port).

Notes
- On first run the app will create the database, tables, indexes, and sample data automatically.

---

## What this project contains

- `app.py` — Streamlit application (UI + routing)
- `database.py` — DB helper functions
- `setup_database.py` — auto-create DB/tables and populate sample data
- `database_schema.sql` — SQL schema and optional manual import
- `.env.example` — template for DB credentials
- `requirements.txt` — Python dependencies

## Screenshots

<p align="center">
	<img src="images/Screenshot%202025-11-09%20163053.png" alt="screenshot1" width="45%" style="margin:4px;"/>
	<img src="images/Screenshot%202025-11-09%20163107.png" alt="screenshot2" width="45%" style="margin:4px;"/>
</p>

<p align="center">
	<img src="images/Screenshot%202025-11-09%20163146.png" alt="screenshot3" width="45%" style="margin:4px;"/>
	<img src="images/Screenshot%202025-11-09%20163206.png" alt="screenshot4" width="45%" style="margin:4px;"/>
</p>

## Admin

The app includes a simple Admin section (local demo only). Default admin password in the app is `admin123`. Change it before any public use.

## License

This project is released under the MIT License. See `LICENSE` file.

---

## Minimal usage contract

- Input: `.env` with MySQL credentials
- Output: running Streamlit app and created MySQL database `airline_reservation_system`
- Error modes: missing/incorrect DB credentials, MySQL not running

---

Happy testing.
