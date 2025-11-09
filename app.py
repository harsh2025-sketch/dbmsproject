"""
Airline Reservation System - Main Streamlit Application
"""
import streamlit as st
from datetime import datetime, date, timedelta
import pandas as pd
from database import Database
from setup_database import setup_database
import os

# Page configuration
st.set_page_config(
    page_title="Airline Reservation System",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def load_custom_css():
    st.markdown("""
        <style>
        /* Main styling */
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .flight-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
            border-left: 4px solid #667eea;
        }
        
        .seat-available {
            background-color: #4ade80;
            padding: 0.5rem;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            text-align: center;
        }
        
        .seat-booked {
            background-color: #ef4444;
            padding: 0.5rem;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            text-align: center;
        }
        
        .info-box {
            background: #f0f9ff;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #0284c7;
            margin: 1rem 0;
        }
        
        .success-box {
            background: #f0fdf4;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #22c55e;
            margin: 1rem 0;
        }
        
        .stButton>button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.5rem 2rem;
            border-radius: 5px;
            font-weight: bold;
        }
        
        .stButton>button:hover {
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        }
        </style>
    """, unsafe_allow_html=True)

# Initialize database with auto-setup
@st.cache_resource
def init_database():
    # First, run database setup (creates tables if they don't exist)
    setup_success = setup_database()
    
    if not setup_success:
        return None
    
    # Then connect to the database
    db = Database()
    if db.connect():
        return db
    return None

# Main application
def main():
    load_custom_css()
    
    # Check for database connection
    db = init_database()
    if not db:
        st.error("⚠️ Could not connect to database. Please check your .env configuration.")
        st.info("""
        ### Setup Instructions:
        1. Create a `.env` file in the project root
        2. Add your MySQL credentials:
        ```
        DB_HOST=localhost
        DB_PORT=3306
        DB_USER=your_username
        DB_PASSWORD=your_password
        DB_NAME=airline_reservation_system
        ```
        3. Run the `database_schema.sql` file to create the database
        4. Restart the application
        """)
        return
    
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>✈️ Airline Reservation System</h1>
            <p>Book your flights with ease and comfort</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["🏠 Home", "🔍 Search Flights", "📝 Book Flight", "🎫 My Bookings", "👥 Admin Dashboard"]
    )
    
    if page == "🏠 Home":
        show_home_page(db)
    elif page == "🔍 Search Flights":
        show_search_page(db)
    elif page == "📝 Book Flight":
        show_booking_page(db)
    elif page == "🎫 My Bookings":
        show_my_bookings_page(db)
    elif page == "👥 Admin Dashboard":
        show_admin_page(db)

def show_home_page(db):
    """Display home page"""
    col1, col2, col3, col4 = st.columns(4)
    
    stats = db.get_statistics()
    
    with col1:
        st.metric("Total Flights", stats['total_flights'])
    with col2:
        st.metric("Total Passengers", stats['total_passengers'])
    with col3:
        st.metric("Active Reservations", stats['total_reservations'])
    with col4:
        st.metric("Total Revenue", f"${stats['total_revenue']:,.2f}")
    
    st.markdown("---")
    
    st.subheader("🌟 Welcome to Our Airline Reservation System")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Why Choose Us?
        - 🌍 **Global Network**: Fly to destinations worldwide
        - 💺 **Comfortable Seating**: Choose from business and economy class
        - 💳 **Easy Booking**: Simple and secure reservation process
        - 📱 **24/7 Support**: We're here to help you anytime
        - ✅ **Flexible Cancellation**: Cancel or modify bookings easily
        """)
    
    with col2:
        st.markdown("""
        ### Quick Links
        - Search for available flights
        - Book your next trip
        - Manage your reservations
        - Check flight status
        - View passenger manifests (Admin)
        """)
    
    st.markdown("---")
    st.info("👉 Use the sidebar to navigate to different sections of the application")

def show_search_page(db):
    """Display flight search page"""
    st.subheader("🔍 Search Flights")
    
    # Get airports
    airports = db.get_all_airports()
    
    if not airports:
        st.warning("⚠️ No airports found in database. Please wait for data to load or contact administrator.")
        return
    
    airport_options = {f"{a['airport_code']} - {a['city']} ({a['airport_name']})": a['airport_code'] 
                      for a in airports}
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        origin = st.selectbox("From", options=list(airport_options.keys()))
        origin_code = airport_options[origin] if origin else None
    
    with col2:
        destination = st.selectbox("To", options=list(airport_options.keys()))
        destination_code = airport_options[destination] if destination else None
    
    with col3:
        travel_date = st.date_input(
            "Departure Date",
            min_value=date.today(),
            value=date.today()
        )
    
    if st.button("Search Flights", type="primary"):
        if not origin_code or not destination_code:
            st.error("Please select both origin and destination airports!")
            return
        
        if origin_code == destination_code:
            st.error("Origin and destination cannot be the same!")
            return
        
        flights = db.search_flights(origin_code, destination_code, travel_date)
        
        if not flights:
            st.warning("No flights found for the selected criteria.")
        else:
            st.success(f"Found {len(flights)} flight(s)")
            
            for flight in flights:
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                    
                    with col1:
                        st.markdown(f"**Flight {flight['flight_number']}**")
                        st.text(f"Aircraft: {flight['aircraft_model']}")
                    
                    with col2:
                        dept_time = flight['departure_time'].strftime("%H:%M")
                        arr_time = flight['arrival_time'].strftime("%H:%M")
                        st.text(f"🛫 {flight['origin_city']} → {flight['destination_city']} 🛬")
                        st.text(f"⏰ {dept_time} - {arr_time}")
                    
                    with col3:
                        available = flight['total_seats'] - flight['booked_seats']
                        st.metric("Available Seats", available)
                    
                    with col4:
                        st.metric("Price", f"${flight['base_price']:.2f}")
                        if st.button(f"Book", key=f"book_{flight['flight_id']}"):
                            st.session_state['selected_flight'] = flight['flight_id']
                            st.session_state['page'] = '📝 Book Flight'
                            st.rerun()
                    
                    st.markdown("---")

def show_booking_page(db):
    """Display booking page"""
    st.subheader("📝 Book Your Flight")
    
    # Check if flight is selected
    if 'selected_flight' not in st.session_state:
        st.info("Please search and select a flight first from the Search Flights page.")
        return
    
    flight = db.get_flight_details(st.session_state['selected_flight'])
    
    if not flight:
        st.error("Flight not found!")
        return
    
    # Display flight details
    st.markdown(f"""
    <div class="info-box">
        <h3>Flight Details</h3>
        <p><strong>Flight Number:</strong> {flight['flight_number']}</p>
        <p><strong>Route:</strong> {flight['origin_city']} ({flight['origin_code']}) → {flight['destination_city']} ({flight['destination_code']})</p>
        <p><strong>Departure:</strong> {flight['departure_time'].strftime("%Y-%m-%d %H:%M")}</p>
        <p><strong>Arrival:</strong> {flight['arrival_time'].strftime("%Y-%m-%d %H:%M")}</p>
        <p><strong>Aircraft:</strong> {flight['aircraft_model']}</p>
        <p><strong>Base Price:</strong> ${flight['base_price']:.2f}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Passenger Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        first_name = st.text_input("First Name*")
        last_name = st.text_input("Last Name*")
        email = st.text_input("Email*")
        phone = st.text_input("Phone Number")
    
    with col2:
        date_of_birth = st.date_input("Date of Birth*", max_value=date.today())
        passport_number = st.text_input("Passport Number")
        nationality = st.text_input("Nationality")
    
    st.markdown("### Select Seat")
    
    # Get available seats
    available_seats = db.get_available_seats(flight['flight_id'])
    
    if not available_seats:
        st.error("No seats available on this flight!")
        return
    
    # Group seats by class
    business_seats = [s for s in available_seats if s['seat_class'] == 'business']
    economy_seats = [s for s in available_seats if s['seat_class'] == 'economy']
    
    col1, col2 = st.columns(2)
    
    with col1:
        if business_seats:
            st.markdown("**Business Class** (+ $200)")
            business_options = {s['seat_number']: s['seat_id'] for s in business_seats}
    
    with col2:
        if economy_seats:
            st.markdown("**Economy Class**")
            economy_options = {s['seat_number']: s['seat_id'] for s in economy_seats}
    
    seat_class = st.radio("Select Class", ["Economy", "Business"])
    
    if seat_class == "Business" and business_seats:
        selected_seat = st.selectbox("Select Seat", options=list(business_options.keys()))
        seat_id = business_options[selected_seat]
        ticket_price = flight['base_price'] + 200
    elif economy_seats:
        selected_seat = st.selectbox("Select Seat", options=list(economy_options.keys()))
        seat_id = economy_options[selected_seat]
        ticket_price = flight['base_price']
    else:
        st.error("No seats available in the selected class!")
        return
    
    st.markdown(f"### Total Price: ${ticket_price:.2f}")
    
    if st.button("Confirm Booking", type="primary"):
        # Validate inputs
        if not all([first_name, last_name, email]):
            st.error("Please fill in all required fields marked with *")
            return
        
        # Create passenger
        passenger_id = db.create_passenger(
            first_name, last_name, email, phone,
            date_of_birth, passport_number, nationality
        )
        
        if passenger_id:
            # Create reservation
            booking_ref = db.create_reservation(
                passenger_id, flight['flight_id'], seat_id, ticket_price
            )
            
            if booking_ref:
                st.markdown(f"""
                <div class="success-box">
                    <h3>✅ Booking Confirmed!</h3>
                    <p><strong>Booking Reference:</strong> {booking_ref}</p>
                    <p>A confirmation email has been sent to {email}</p>
                    <p>Please save your booking reference for future reference.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Clear session state
                if 'selected_flight' in st.session_state:
                    del st.session_state['selected_flight']
            else:
                st.error("Failed to create reservation. Please try again.")
        else:
            st.error("Failed to create passenger record. Please try again.")

def show_my_bookings_page(db):
    """Display user bookings page"""
    st.subheader("🎫 My Bookings")
    
    tab1, tab2 = st.tabs(["View Bookings", "Check Booking Status"])
    
    with tab1:
        email = st.text_input("Enter your email to view bookings")
        
        if st.button("Search", type="primary"):
            if not email:
                st.warning("Please enter your email address")
                return
            
            reservations = db.get_passenger_reservations(email)
            
            if not reservations:
                st.info("No bookings found for this email address.")
            else:
                st.success(f"Found {len(reservations)} booking(s)")
                
                for res in reservations:
                    with st.expander(f"Booking: {res['booking_reference']} - {res['origin_city']} to {res['destination_city']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"""
                            **Flight Details:**
                            - Flight Number: {res['flight_number']}
                            - From: {res['origin_city']} ({res['origin_code']})
                            - To: {res['destination_city']} ({res['destination_code']})
                            - Departure: {res['departure_time'].strftime("%Y-%m-%d %H:%M")}
                            - Arrival: {res['arrival_time'].strftime("%Y-%m-%d %H:%M")}
                            """)
                        
                        with col2:
                            st.markdown(f"""
                            **Booking Details:**
                            - Booking Reference: {res['booking_reference']}
                            - Seat Number: {res['seat_number'] or 'N/A'}
                            - Price: ${res['ticket_price']:.2f}
                            - Status: {res['status'].upper()}
                            - Payment: {res['payment_status'].upper()}
                            """)
                        
                        if res['status'] == 'confirmed' and res['departure_time'] > datetime.now():
                            if st.button(f"Cancel Booking", key=f"cancel_{res['booking_reference']}"):
                                db.cancel_reservation(res['booking_reference'])
                                st.success("Booking cancelled successfully!")
                                st.rerun()
    
    with tab2:
        booking_ref = st.text_input("Enter Booking Reference")
        
        if st.button("Check Status", type="primary"):
            if not booking_ref:
                st.warning("Please enter a booking reference")
                return
            
            reservation = db.get_reservation_by_reference(booking_ref)
            
            if not reservation:
                st.error("Booking not found!")
            else:
                st.markdown(f"""
                <div class="info-box">
                    <h3>Booking Information</h3>
                    <p><strong>Passenger:</strong> {reservation['first_name']} {reservation['last_name']}</p>
                    <p><strong>Email:</strong> {reservation['email']}</p>
                    <p><strong>Flight:</strong> {reservation['flight_number']}</p>
                    <p><strong>Route:</strong> {reservation['origin_city']} → {reservation['destination_city']}</p>
                    <p><strong>Departure:</strong> {reservation['departure_time'].strftime("%Y-%m-%d %H:%M")}</p>
                    <p><strong>Seat:</strong> {reservation['seat_number'] or 'N/A'}</p>
                    <p><strong>Status:</strong> {reservation['status'].upper()}</p>
                    <p><strong>Payment Status:</strong> {reservation['payment_status'].upper()}</p>
                </div>
                """, unsafe_allow_html=True)

def show_admin_page(db):
    """Display admin dashboard"""
    st.subheader("👥 Admin Dashboard")
    
    # Simple authentication (you should implement proper authentication)
    if 'admin_authenticated' not in st.session_state:
        st.session_state['admin_authenticated'] = False
    
    if not st.session_state['admin_authenticated']:
        password = st.text_input("Enter Admin Password", type="password")
        if st.button("Login"):
            if password == "admin123":  # Change this to a secure password
                st.session_state['admin_authenticated'] = True
                st.rerun()
            else:
                st.error("Invalid password!")
        return
    
    tab1, tab2, tab3 = st.tabs(["Flight Management", "Passenger Manifest", "Statistics"])
    
    with tab1:
        st.markdown("### All Flights")
        
        flights = db.get_all_flights()
        
        if flights:
            df = pd.DataFrame(flights)
            df['departure_time'] = pd.to_datetime(df['departure_time'])
            df['route'] = df['origin_city'] + ' → ' + df['destination_city']
            
            display_df = df[['flight_number', 'route', 'departure_time', 'status', 'aircraft_model', 'booked_seats']]
            st.dataframe(display_df, use_container_width=True)
            
            # Update flight status
            st.markdown("### Update Flight Status")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                flight_to_update = st.selectbox(
                    "Select Flight",
                    options=[f"{f['flight_number']}" for f in flights]
                )
            
            with col2:
                new_status = st.selectbox(
                    "New Status",
                    ["scheduled", "boarding", "departed", "arrived", "cancelled", "delayed"]
                )
            
            with col3:
                st.write("")  # Spacing
                st.write("")  # Spacing
                if st.button("Update Status"):
                    flight_id = next(f['flight_id'] for f in flights if f['flight_number'] == flight_to_update)
                    db.update_flight_status(flight_id, new_status)
                    st.success(f"Flight {flight_to_update} status updated to {new_status}")
                    st.rerun()
    
    with tab2:
        st.markdown("### Passenger Manifest")
        
        flights = db.get_all_flights()
        flight_options = {f"{f['flight_number']} - {f['origin_city']} to {f['destination_city']}": f['flight_id'] 
                         for f in flights}
        
        selected_flight = st.selectbox("Select Flight", options=list(flight_options.keys()))
        flight_id = flight_options[selected_flight]
        
        if st.button("View Manifest"):
            manifest = db.get_flight_manifest(flight_id)
            
            if not manifest:
                st.info("No passengers booked on this flight yet.")
            else:
                st.success(f"Total Passengers: {len(manifest)}")
                df = pd.DataFrame(manifest)
                st.dataframe(df, use_container_width=True)
    
    with tab3:
        st.markdown("### Statistics")
        
        stats = db.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Flights", stats['total_flights'])
        with col2:
            st.metric("Total Passengers", stats['total_passengers'])
        with col3:
            st.metric("Active Reservations", stats['total_reservations'])
        with col4:
            st.metric("Total Revenue", f"${stats['total_revenue']:,.2f}")
        
        # Additional charts can be added here using plotly

if __name__ == "__main__":
    main()
