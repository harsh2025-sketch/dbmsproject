"""
Automatic Database Setup Script
This script automatically creates the database and all tables when you run the application
"""
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_database():
    """Create database and tables automatically"""
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '3306')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    database = os.getenv('DB_NAME', 'airline_reservation_system')
    
    print(" Starting database setup...")
    
    try:
        # First, connect without specifying database to create it
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password
        )
        
        cursor = connection.cursor()
        
        # Create database if not exists
        print(f" Creating database '{database}'...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        print(f" Database '{database}' ready")
        
        # Use the database
        cursor.execute(f"USE {database}")
        
        # Check if tables already exist
        cursor.execute("SHOW TABLES")
        existing_tables = cursor.fetchall()
        
        if existing_tables:
            print(f"ℹ️  Database already has {len(existing_tables)} table(s).")
            # Check if tables have data
            cursor.execute("SELECT COUNT(*) FROM Airports")
            airport_count = cursor.fetchone()[0]
            
            if airport_count > 0:
                print(f"✅ Data already exists ({airport_count} airports). Setup complete!")
                cursor.close()
                connection.close()
                return True
            else:
                print("⚠️  Tables exist but are empty. Inserting sample data...")
                insert_sample_data(cursor, connection)
                cursor.close()
                connection.close()
                print("✅ Database setup completed successfully!")
                return True
        
        print("📋 Creating tables...")
        
        # Create Airports table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Airports (
                airport_id INT PRIMARY KEY AUTO_INCREMENT,
                airport_code VARCHAR(10) UNIQUE NOT NULL,
                airport_name VARCHAR(100) NOT NULL,
                city VARCHAR(50) NOT NULL,
                country VARCHAR(50) NOT NULL,
                timezone VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  ✓ Airports table created")
        
        # Create Aircraft table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Aircraft (
                aircraft_id INT PRIMARY KEY AUTO_INCREMENT,
                aircraft_model VARCHAR(50) NOT NULL,
                registration_number VARCHAR(20) UNIQUE NOT NULL,
                manufacturer VARCHAR(50),
                total_seats INT NOT NULL,
                business_class_seats INT DEFAULT 0,
                economy_class_seats INT DEFAULT 0,
                status ENUM('active', 'maintenance', 'retired') DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  ✓ Aircraft table created")
        
        # Create Flights table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Flights (
                flight_id INT PRIMARY KEY AUTO_INCREMENT,
                flight_number VARCHAR(20) UNIQUE NOT NULL,
                aircraft_id INT NOT NULL,
                origin_airport_id INT NOT NULL,
                destination_airport_id INT NOT NULL,
                departure_time DATETIME NOT NULL,
                arrival_time DATETIME NOT NULL,
                base_price DECIMAL(10, 2) NOT NULL,
                status ENUM('scheduled', 'boarding', 'departed', 'arrived', 'cancelled', 'delayed') DEFAULT 'scheduled',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (aircraft_id) REFERENCES Aircraft(aircraft_id),
                FOREIGN KEY (origin_airport_id) REFERENCES Airports(airport_id),
                FOREIGN KEY (destination_airport_id) REFERENCES Airports(airport_id)
            )
        """)
        print("  ✓ Flights table created")
        
        # Create Passengers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Passengers (
                passenger_id INT PRIMARY KEY AUTO_INCREMENT,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone VARCHAR(20),
                date_of_birth DATE,
                passport_number VARCHAR(20) UNIQUE,
                nationality VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  ✓ Passengers table created")
        
        # Create Seats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Seats (
                seat_id INT PRIMARY KEY AUTO_INCREMENT,
                aircraft_id INT NOT NULL,
                seat_number VARCHAR(10) NOT NULL,
                seat_class ENUM('business', 'economy') NOT NULL,
                UNIQUE KEY unique_seat (aircraft_id, seat_number),
                FOREIGN KEY (aircraft_id) REFERENCES Aircraft(aircraft_id)
            )
        """)
        print("  ✓ Seats table created")
        
        # Create Reservations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Reservations (
                reservation_id INT PRIMARY KEY AUTO_INCREMENT,
                passenger_id INT NOT NULL,
                flight_id INT NOT NULL,
                seat_id INT,
                booking_reference VARCHAR(20) UNIQUE NOT NULL,
                booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ticket_price DECIMAL(10, 2) NOT NULL,
                status ENUM('confirmed', 'cancelled', 'checked_in', 'completed') DEFAULT 'confirmed',
                payment_status ENUM('pending', 'paid', 'refunded') DEFAULT 'pending',
                FOREIGN KEY (passenger_id) REFERENCES Passengers(passenger_id),
                FOREIGN KEY (flight_id) REFERENCES Flights(flight_id),
                FOREIGN KEY (seat_id) REFERENCES Seats(seat_id)
            )
        """)
        print("  ✓ Reservations table created")
        
        # Create indexes (skip if they already exist)
        print("📊 Creating indexes...")
        indexes = [
            ("idx_flight_number", "Flights", "flight_number"),
            ("idx_flight_departure", "Flights", "departure_time"),
            ("idx_flight_origin", "Flights", "origin_airport_id"),
            ("idx_flight_destination", "Flights", "destination_airport_id"),
            ("idx_passenger_email", "Passengers", "email"),
            ("idx_reservation_booking_ref", "Reservations", "booking_reference"),
            ("idx_reservation_passenger", "Reservations", "passenger_id"),
            ("idx_reservation_flight", "Reservations", "flight_id")
        ]
        
        for idx_name, table_name, column_name in indexes:
            try:
                cursor.execute(f"CREATE INDEX {idx_name} ON {table_name}({column_name})")
            except Error as e:
                if e.errno != 1061:  # Duplicate key name error
                    pass  # Index already exists, skip
        print("  ✓ Indexes created")
        
        connection.commit()
        
        # Insert sample data
        print("📥 Inserting sample data...")
        insert_sample_data(cursor, connection)
        
        cursor.close()
        connection.close()
        
        print("✅ Database setup completed successfully!")
        return True
        
    except Error as e:
        print(f"❌ Error during database setup: {e}")
        return False

def insert_sample_data(cursor, connection):
    """Insert sample data into tables"""
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM Airports")
    if cursor.fetchone()[0] > 0:
        print("  ℹ️  Sample data already exists. Skipping insertion.")
        return
    
    # Sample Airports
    airports = [
        ('JFK', 'John F. Kennedy International Airport', 'New York', 'USA', 'America/New_York'),
        ('LAX', 'Los Angeles International Airport', 'Los Angeles', 'USA', 'America/Los_Angeles'),
        ('ORD', 'O\'Hare International Airport', 'Chicago', 'USA', 'America/Chicago'),
        ('LHR', 'London Heathrow Airport', 'London', 'UK', 'Europe/London'),
        ('CDG', 'Charles de Gaulle Airport', 'Paris', 'France', 'Europe/Paris'),
        ('DXB', 'Dubai International Airport', 'Dubai', 'UAE', 'Asia/Dubai'),
        ('HND', 'Tokyo Haneda Airport', 'Tokyo', 'Japan', 'Asia/Tokyo'),
        ('SIN', 'Singapore Changi Airport', 'Singapore', 'Singapore', 'Asia/Singapore'),
        ('DEL', 'Indira Gandhi International Airport', 'New Delhi', 'India', 'Asia/Kolkata'),
        ('SFO', 'San Francisco International Airport', 'San Francisco', 'USA', 'America/Los_Angeles')
    ]
    
    cursor.executemany("""
        INSERT INTO Airports (airport_code, airport_name, city, country, timezone)
        VALUES (%s, %s, %s, %s, %s)
    """, airports)
    print("  ✓ Airports data inserted")
    
    # Sample Aircraft
    aircraft = [
        ('Boeing 737-800', 'N12345', 'Boeing', 189, 12, 177, 'active'),
        ('Airbus A320', 'N23456', 'Airbus', 180, 12, 168, 'active'),
        ('Boeing 777-300ER', 'N34567', 'Boeing', 396, 42, 354, 'active'),
        ('Airbus A350-900', 'N45678', 'Airbus', 325, 36, 289, 'active'),
        ('Boeing 787-9', 'N56789', 'Boeing', 290, 30, 260, 'active'),
        ('Airbus A380', 'N67890', 'Airbus', 525, 58, 467, 'active')
    ]
    
    cursor.executemany("""
        INSERT INTO Aircraft (aircraft_model, registration_number, manufacturer, total_seats, 
                            business_class_seats, economy_class_seats, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, aircraft)
    print("  ✓ Aircraft data inserted")
    
    # Sample Seats for Aircraft 1 (Boeing 737-800)
    seats = []
    for row in range(1, 31):
        for seat_letter in ['A', 'B', 'C', 'D', 'E', 'F']:
            seat_number = f"{row}{seat_letter}"
            seat_class = 'business' if row <= 3 else 'economy'
            seats.append((1, seat_number, seat_class))
            if len(seats) >= 189:
                break
        if len(seats) >= 189:
            break
    
    cursor.executemany("""
        INSERT INTO Seats (aircraft_id, seat_number, seat_class)
        VALUES (%s, %s, %s)
    """, seats)
    print("  ✓ Seats data inserted")
    
    # Sample Flights
    flights = [
        ('AA101', 1, 1, 2, '2025-11-15 08:00:00', '2025-11-15 11:30:00', 350.00, 'scheduled'),
        ('AA102', 2, 2, 1, '2025-11-15 14:00:00', '2025-11-15 22:45:00', 380.00, 'scheduled'),
        ('UA201', 3, 1, 4, '2025-11-16 18:00:00', '2025-11-17 07:00:00', 850.00, 'scheduled'),
        ('BA301', 4, 4, 6, '2025-11-17 10:00:00', '2025-11-17 19:30:00', 650.00, 'scheduled'),
        ('DL401', 5, 3, 10, '2025-11-18 09:00:00', '2025-11-18 11:45:00', 280.00, 'scheduled'),
        ('SQ501', 6, 8, 7, '2025-11-19 23:00:00', '2025-11-20 07:30:00', 720.00, 'scheduled'),
        ('AI601', 3, 9, 1, '2025-11-20 02:00:00', '2025-11-20 07:00:00', 920.00, 'scheduled'),
        ('EK701', 4, 6, 5, '2025-11-21 15:00:00', '2025-11-21 20:30:00', 550.00, 'scheduled')
    ]
    
    cursor.executemany("""
        INSERT INTO Flights (flight_number, aircraft_id, origin_airport_id, destination_airport_id,
                           departure_time, arrival_time, base_price, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, flights)
    print("  ✓ Flights data inserted")
    
    # Sample Passengers
    passengers = [
        ('John', 'Doe', 'john.doe@email.com', '+1-555-0101', '1985-05-15', 'P12345678', 'USA'),
        ('Jane', 'Smith', 'jane.smith@email.com', '+1-555-0102', '1990-08-22', 'P23456789', 'USA'),
        ('Robert', 'Johnson', 'robert.j@email.com', '+44-20-1234-5678', '1978-03-10', 'P34567890', 'UK'),
        ('Maria', 'Garcia', 'maria.garcia@email.com', '+33-1-2345-6789', '1992-11-30', 'P45678901', 'France'),
        ('Ahmed', 'Hassan', 'ahmed.hassan@email.com', '+971-4-123-4567', '1988-07-18', 'P56789012', 'UAE')
    ]
    
    cursor.executemany("""
        INSERT INTO Passengers (first_name, last_name, email, phone, date_of_birth, passport_number, nationality)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, passengers)
    print("  ✓ Passengers data inserted")
    
    # Sample Reservations
    reservations = [
        (1, 1, 15, 'BK2025001', 350.00, 'confirmed', 'paid'),
        (2, 2, 20, 'BK2025002', 380.00, 'confirmed', 'paid'),
        (3, 3, 25, 'BK2025003', 850.00, 'confirmed', 'paid')
    ]
    
    cursor.executemany("""
        INSERT INTO Reservations (passenger_id, flight_id, seat_id, booking_reference, 
                                ticket_price, status, payment_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, reservations)
    print("  ✓ Reservations data inserted")
    
    connection.commit()

if __name__ == "__main__":
    setup_database()
