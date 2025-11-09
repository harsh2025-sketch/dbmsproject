"""
Database connection and operations module
"""
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random
import string

# Load environment variables
load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '3306')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.database = os.getenv('DB_NAME', 'airline_reservation_system')
        self.connection = None
    
    def connect(self):
        """Create database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                return True
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"Error executing query: {e}")
            return []
    
    def execute_update(self, query, params=None):
        """Execute an INSERT, UPDATE, or DELETE query"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            last_id = cursor.lastrowid
            cursor.close()
            return last_id
        except Error as e:
            print(f"Error executing update: {e}")
            self.connection.rollback()
            return None
    
    # Flight Operations
    def search_flights(self, origin_code, destination_code, departure_date):
        """Search for available flights"""
        query = """
            SELECT 
                f.flight_id,
                f.flight_number,
                f.departure_time,
                f.arrival_time,
                f.base_price,
                f.status,
                o.airport_code as origin_code,
                o.airport_name as origin_name,
                o.city as origin_city,
                d.airport_code as destination_code,
                d.airport_name as destination_name,
                d.city as destination_city,
                a.aircraft_model,
                a.total_seats,
                (SELECT COUNT(*) FROM Reservations r WHERE r.flight_id = f.flight_id AND r.status = 'confirmed') as booked_seats
            FROM Flights f
            JOIN Airports o ON f.origin_airport_id = o.airport_id
            JOIN Airports d ON f.destination_airport_id = d.airport_id
            JOIN Aircraft a ON f.aircraft_id = a.aircraft_id
            WHERE o.airport_code = %s 
            AND d.airport_code = %s 
            AND DATE(f.departure_time) = %s
            AND f.status = 'scheduled'
            ORDER BY f.departure_time
        """
        return self.execute_query(query, (origin_code, destination_code, departure_date))
    
    def get_all_airports(self):
        """Get all airports"""
        query = "SELECT * FROM Airports ORDER BY city"
        return self.execute_query(query)
    
    def get_flight_details(self, flight_id):
        """Get detailed information about a flight"""
        query = """
            SELECT 
                f.*,
                o.airport_code as origin_code,
                o.airport_name as origin_name,
                o.city as origin_city,
                d.airport_code as destination_code,
                d.airport_name as destination_name,
                d.city as destination_city,
                a.aircraft_model,
                a.total_seats,
                a.business_class_seats,
                a.economy_class_seats
            FROM Flights f
            JOIN Airports o ON f.origin_airport_id = o.airport_id
            JOIN Airports d ON f.destination_airport_id = d.airport_id
            JOIN Aircraft a ON f.aircraft_id = a.aircraft_id
            WHERE f.flight_id = %s
        """
        result = self.execute_query(query, (flight_id,))
        return result[0] if result else None
    
    # Passenger Operations
    def create_passenger(self, first_name, last_name, email, phone, date_of_birth, passport_number, nationality):
        """Create a new passenger or return existing one"""
        # Check if passenger exists
        check_query = "SELECT passenger_id FROM Passengers WHERE email = %s"
        existing = self.execute_query(check_query, (email,))
        
        if existing:
            return existing[0]['passenger_id']
        
        # Create new passenger
        query = """
            INSERT INTO Passengers (first_name, last_name, email, phone, date_of_birth, passport_number, nationality)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return self.execute_update(query, (first_name, last_name, email, phone, date_of_birth, passport_number, nationality))
    
    def get_passenger_by_email(self, email):
        """Get passenger by email"""
        query = "SELECT * FROM Passengers WHERE email = %s"
        result = self.execute_query(query, (email,))
        return result[0] if result else None
    
    # Seat Operations
    def get_available_seats(self, flight_id):
        """Get available seats for a flight"""
        query = """
            SELECT s.seat_id, s.seat_number, s.seat_class
            FROM Seats s
            JOIN Flights f ON s.aircraft_id = f.aircraft_id
            WHERE f.flight_id = %s
            AND s.seat_id NOT IN (
                SELECT seat_id FROM Reservations 
                WHERE flight_id = %s AND status = 'confirmed' AND seat_id IS NOT NULL
            )
            ORDER BY s.seat_class, s.seat_number
        """
        return self.execute_query(query, (flight_id, flight_id))
    
    # Reservation Operations
    def generate_booking_reference(self):
        """Generate a unique booking reference"""
        while True:
            ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            query = "SELECT booking_reference FROM Reservations WHERE booking_reference = %s"
            existing = self.execute_query(query, (ref,))
            if not existing:
                return ref
    
    def create_reservation(self, passenger_id, flight_id, seat_id, ticket_price):
        """Create a new reservation"""
        booking_ref = self.generate_booking_reference()
        query = """
            INSERT INTO Reservations (passenger_id, flight_id, seat_id, booking_reference, ticket_price, status, payment_status)
            VALUES (%s, %s, %s, %s, %s, 'confirmed', 'paid')
        """
        reservation_id = self.execute_update(query, (passenger_id, flight_id, seat_id, booking_ref, ticket_price))
        return booking_ref if reservation_id else None
    
    def get_reservation_by_reference(self, booking_reference):
        """Get reservation details by booking reference"""
        query = """
            SELECT 
                r.*,
                p.first_name, p.last_name, p.email, p.phone,
                f.flight_number, f.departure_time, f.arrival_time,
                o.airport_code as origin_code, o.city as origin_city,
                d.airport_code as destination_code, d.city as destination_city,
                s.seat_number
            FROM Reservations r
            JOIN Passengers p ON r.passenger_id = p.passenger_id
            JOIN Flights f ON r.flight_id = f.flight_id
            JOIN Airports o ON f.origin_airport_id = o.airport_id
            JOIN Airports d ON f.destination_airport_id = d.airport_id
            LEFT JOIN Seats s ON r.seat_id = s.seat_id
            WHERE r.booking_reference = %s
        """
        result = self.execute_query(query, (booking_reference,))
        return result[0] if result else None
    
    def cancel_reservation(self, booking_reference):
        """Cancel a reservation"""
        query = """
            UPDATE Reservations 
            SET status = 'cancelled', payment_status = 'refunded'
            WHERE booking_reference = %s
        """
        self.execute_update(query, (booking_reference,))
    
    def get_passenger_reservations(self, email):
        """Get all reservations for a passenger"""
        query = """
            SELECT 
                r.*,
                f.flight_number, f.departure_time, f.arrival_time, f.status as flight_status,
                o.airport_code as origin_code, o.city as origin_city,
                d.airport_code as destination_code, d.city as destination_city,
                s.seat_number
            FROM Reservations r
            JOIN Passengers p ON r.passenger_id = p.passenger_id
            JOIN Flights f ON r.flight_id = f.flight_id
            JOIN Airports o ON f.origin_airport_id = o.airport_id
            JOIN Airports d ON f.destination_airport_id = d.airport_id
            LEFT JOIN Seats s ON r.seat_id = s.seat_id
            WHERE p.email = %s
            ORDER BY f.departure_time DESC
        """
        return self.execute_query(query, (email,))
    
    # Admin Operations
    def get_all_flights(self):
        """Get all flights for admin view"""
        query = """
            SELECT 
                f.*,
                o.airport_code as origin_code,
                o.city as origin_city,
                d.airport_code as destination_code,
                d.city as destination_city,
                a.aircraft_model,
                (SELECT COUNT(*) FROM Reservations r WHERE r.flight_id = f.flight_id AND r.status = 'confirmed') as booked_seats
            FROM Flights f
            JOIN Airports o ON f.origin_airport_id = o.airport_id
            JOIN Airports d ON f.destination_airport_id = d.airport_id
            JOIN Aircraft a ON f.aircraft_id = a.aircraft_id
            ORDER BY f.departure_time DESC
        """
        return self.execute_query(query)
    
    def get_flight_manifest(self, flight_id):
        """Get passenger manifest for a flight"""
        query = """
            SELECT 
                p.first_name, p.last_name, p.email, p.phone, p.passport_number,
                r.booking_reference, r.status, r.payment_status,
                s.seat_number, s.seat_class
            FROM Reservations r
            JOIN Passengers p ON r.passenger_id = p.passenger_id
            LEFT JOIN Seats s ON r.seat_id = s.seat_id
            WHERE r.flight_id = %s
            ORDER BY s.seat_number
        """
        return self.execute_query(query, (flight_id,))
    
    def update_flight_status(self, flight_id, status):
        """Update flight status"""
        query = "UPDATE Flights SET status = %s WHERE flight_id = %s"
        self.execute_update(query, (status, flight_id))
    
    def get_statistics(self):
        """Get dashboard statistics"""
        stats = {}
        
        # Total flights
        result = self.execute_query("SELECT COUNT(*) as count FROM Flights")
        stats['total_flights'] = result[0]['count'] if result else 0
        
        # Total passengers
        result = self.execute_query("SELECT COUNT(*) as count FROM Passengers")
        stats['total_passengers'] = result[0]['count'] if result else 0
        
        # Total reservations
        result = self.execute_query("SELECT COUNT(*) as count FROM Reservations WHERE status = 'confirmed'")
        stats['total_reservations'] = result[0]['count'] if result else 0
        
        # Total revenue
        result = self.execute_query("SELECT SUM(ticket_price) as revenue FROM Reservations WHERE payment_status = 'paid'")
        stats['total_revenue'] = result[0]['revenue'] if result and result[0]['revenue'] else 0
        
        return stats
