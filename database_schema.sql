-- Airline Reservation System Database Schema

DROP DATABASE IF EXISTS airline_reservation_system;
CREATE DATABASE airline_reservation_system;
USE airline_reservation_system;

-- Airports Table
CREATE TABLE Airports (
    airport_id INT PRIMARY KEY AUTO_INCREMENT,
    airport_code VARCHAR(10) UNIQUE NOT NULL,
    airport_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    timezone VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Aircraft Table
CREATE TABLE Aircraft (
    aircraft_id INT PRIMARY KEY AUTO_INCREMENT,
    aircraft_model VARCHAR(50) NOT NULL,
    registration_number VARCHAR(20) UNIQUE NOT NULL,
    manufacturer VARCHAR(50),
    total_seats INT NOT NULL,
    business_class_seats INT DEFAULT 0,
    economy_class_seats INT DEFAULT 0,
    status ENUM('active', 'maintenance', 'retired') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Flights Table
CREATE TABLE Flights (
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
);

-- Passengers Table
CREATE TABLE Passengers (
    passenger_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    date_of_birth DATE,
    passport_number VARCHAR(20) UNIQUE,
    nationality VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seats Table
CREATE TABLE Seats (
    seat_id INT PRIMARY KEY AUTO_INCREMENT,
    aircraft_id INT NOT NULL,
    seat_number VARCHAR(10) NOT NULL,
    seat_class ENUM('business', 'economy') NOT NULL,
    UNIQUE KEY unique_seat (aircraft_id, seat_number),
    FOREIGN KEY (aircraft_id) REFERENCES Aircraft(aircraft_id)
);

-- Reservations Table
CREATE TABLE Reservations (
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
);

-- Indexes for better query performance
CREATE INDEX idx_flight_number ON Flights(flight_number);
CREATE INDEX idx_flight_departure ON Flights(departure_time);
CREATE INDEX idx_flight_origin ON Flights(origin_airport_id);
CREATE INDEX idx_flight_destination ON Flights(destination_airport_id);
CREATE INDEX idx_passenger_email ON Passengers(email);
CREATE INDEX idx_reservation_booking_ref ON Reservations(booking_reference);
CREATE INDEX idx_reservation_passenger ON Reservations(passenger_id);
CREATE INDEX idx_reservation_flight ON Reservations(flight_id);

-- Insert Sample Data

-- Sample Airports
INSERT INTO Airports (airport_code, airport_name, city, country, timezone) VALUES
('JFK', 'John F. Kennedy International Airport', 'New York', 'USA', 'America/New_York'),
('LAX', 'Los Angeles International Airport', 'Los Angeles', 'USA', 'America/Los_Angeles'),
('ORD', 'O\'Hare International Airport', 'Chicago', 'USA', 'America/Chicago'),
('LHR', 'London Heathrow Airport', 'London', 'UK', 'Europe/London'),
('CDG', 'Charles de Gaulle Airport', 'Paris', 'France', 'Europe/Paris'),
('DXB', 'Dubai International Airport', 'Dubai', 'UAE', 'Asia/Dubai'),
('HND', 'Tokyo Haneda Airport', 'Tokyo', 'Japan', 'Asia/Tokyo'),
('SIN', 'Singapore Changi Airport', 'Singapore', 'Singapore', 'Asia/Singapore'),
('DEL', 'Indira Gandhi International Airport', 'New Delhi', 'India', 'Asia/Kolkata'),
('SFO', 'San Francisco International Airport', 'San Francisco', 'USA', 'America/Los_Angeles');

-- Sample Aircraft
INSERT INTO Aircraft (aircraft_model, registration_number, manufacturer, total_seats, business_class_seats, economy_class_seats, status) VALUES
('Boeing 737-800', 'N12345', 'Boeing', 189, 12, 177, 'active'),
('Airbus A320', 'N23456', 'Airbus', 180, 12, 168, 'active'),
('Boeing 777-300ER', 'N34567', 'Boeing', 396, 42, 354, 'active'),
('Airbus A350-900', 'N45678', 'Airbus', 325, 36, 289, 'active'),
('Boeing 787-9', 'N56789', 'Boeing', 290, 30, 260, 'active'),
('Airbus A380', 'N67890', 'Airbus', 525, 58, 467, 'active');

-- Sample Seats for Aircraft 1 (Boeing 737-800)
INSERT INTO Seats (aircraft_id, seat_number, seat_class)
SELECT 1, CONCAT(row_num, seat_letter), 
       CASE WHEN row_num <= 3 THEN 'business' ELSE 'economy' END
FROM (
    SELECT r.row_num, s.seat_letter
    FROM (
        SELECT 1 AS row_num UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 
        UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10
        UNION SELECT 11 UNION SELECT 12 UNION SELECT 13 UNION SELECT 14 UNION SELECT 15
        UNION SELECT 16 UNION SELECT 17 UNION SELECT 18 UNION SELECT 19 UNION SELECT 20
        UNION SELECT 21 UNION SELECT 22 UNION SELECT 23 UNION SELECT 24 UNION SELECT 25
        UNION SELECT 26 UNION SELECT 27 UNION SELECT 28 UNION SELECT 29 UNION SELECT 30
    ) r
    CROSS JOIN (
        SELECT 'A' AS seat_letter UNION SELECT 'B' UNION SELECT 'C' 
        UNION SELECT 'D' UNION SELECT 'E' UNION SELECT 'F'
    ) s
) seat_combinations
LIMIT 189;

-- Sample Flights
INSERT INTO Flights (flight_number, aircraft_id, origin_airport_id, destination_airport_id, departure_time, arrival_time, base_price, status) VALUES
('AA101', 1, 1, 2, '2025-11-15 08:00:00', '2025-11-15 11:30:00', 350.00, 'scheduled'),
('AA102', 2, 2, 1, '2025-11-15 14:00:00', '2025-11-15 22:45:00', 380.00, 'scheduled'),
('UA201', 3, 1, 4, '2025-11-16 18:00:00', '2025-11-17 07:00:00', 850.00, 'scheduled'),
('BA301', 4, 4, 6, '2025-11-17 10:00:00', '2025-11-17 19:30:00', 650.00, 'scheduled'),
('DL401', 5, 3, 10, '2025-11-18 09:00:00', '2025-11-18 11:45:00', 280.00, 'scheduled'),
('SQ501', 6, 8, 7, '2025-11-19 23:00:00', '2025-11-20 07:30:00', 720.00, 'scheduled'),
('AI601', 3, 9, 1, '2025-11-20 02:00:00', '2025-11-20 07:00:00', 920.00, 'scheduled'),
('EK701', 4, 6, 5, '2025-11-21 15:00:00', '2025-11-21 20:30:00', 550.00, 'scheduled');

-- Sample Passengers
INSERT INTO Passengers (first_name, last_name, email, phone, date_of_birth, passport_number, nationality) VALUES
('John', 'Doe', 'john.doe@email.com', '+1-555-0101', '1985-05-15', 'P12345678', 'USA'),
('Jane', 'Smith', 'jane.smith@email.com', '+1-555-0102', '1990-08-22', 'P23456789', 'USA'),
('Robert', 'Johnson', 'robert.j@email.com', '+44-20-1234-5678', '1978-03-10', 'P34567890', 'UK'),
('Maria', 'Garcia', 'maria.garcia@email.com', '+33-1-2345-6789', '1992-11-30', 'P45678901', 'France'),
('Ahmed', 'Hassan', 'ahmed.hassan@email.com', '+971-4-123-4567', '1988-07-18', 'P56789012', 'UAE');

-- Sample Reservations
INSERT INTO Reservations (passenger_id, flight_id, seat_id, booking_reference, ticket_price, status, payment_status) VALUES
(1, 1, 15, 'BK2025001', 350.00, 'confirmed', 'paid'),
(2, 2, 20, 'BK2025002', 380.00, 'confirmed', 'paid'),
(3, 3, 25, 'BK2025003', 850.00, 'confirmed', 'paid');
