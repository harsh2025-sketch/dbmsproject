"""
Test database connection and show current state
"""
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '3306')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    database = os.getenv('DB_NAME', 'airline_reservation_system')
    
    print("=" * 60)
    print("DATABASE CONNECTION TEST")
    print("=" * 60)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"User: {user}")
    print(f"Database: {database}")
    print("=" * 60)
    
    try:
        # Test connection without database
        print("\n1. Testing MySQL connection...")
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password
        )
        print(" Successfully connected to MySQL server!")
        
        cursor = connection.cursor()
        
        # Check if database exists
        print(f"\n2. Checking if database '{database}' exists...")
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]
        
        if database in databases:
            print(f"✅ Database '{database}' exists")
            
            # Connect to the database
            cursor.execute(f"USE {database}")
            
            # Check tables
            print(f"\n3. Checking tables in '{database}'...")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                print(f"✅ Found {len(tables)} table(s):")
                for table in tables:
                    print(f"   - {table[0]}")
                    
                # Count records in each table
                print(f"\n4. Checking data in tables...")
                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"   {table_name}: {count} record(s)")
            else:
                print("⚠️  No tables found in database!")
                print("   The database exists but is empty.")
        else:
            print(f"❌ Database '{database}' does NOT exist")
            print("   Need to create database and tables")
        
        cursor.close()
        connection.close()
        
        print("\n" + "=" * 60)
        print("TEST COMPLETED")
        print("=" * 60)
        
    except Error as e:
        print(f"\n❌ ERROR: {e}")
        print("\nPossible issues:")
        print("1. MySQL server is not running")
        print("2. Wrong credentials in .env file")
        print("3. User doesn't have proper permissions")
        return False
    
    return True

if __name__ == "__main__":
    test_connection()
