import os
import sys
import mariadb
from dotenv import load_dotenv

load_dotenv()

PASSWORD = os.environ.get("db_password")
USERNAME = os.environ.get("db_user")
db_name = os.environ.get("db_name")

def dbConnect():
    # Connect to MariaDB Platform
    try:
        conn = mariadb.connect(
            user=USERNAME,
            password=PASSWORD,
            host="127.0.0.1",
            port=3306,
            database=db_name
        )

        print('Connection Successful!')
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    
    return conn

def createTables(conn):
    try:
        cur = conn.cursor()
        # Create a User table. This table will only have one item at all times
        cur.execute("""create table if not exists User (
                    id int primary key auto_increment,
                    UserID VARCHAR(255) not null,
                    Email VARCHAR(255) not null,
                    Password VARCHAR(255) not null
        );
        """)
        print("User table created!")

        # Create a Configuration table. This table will only have one item at all times. It will be used to store settings
        cur.execute(f"""create table if not exists Configuration (
                    id int primary key auto_increment,
                    IpAddress VARCHAR(255) not null,
                    ModuleList TEXT,
                    DataBaseAddr VARCHAR(255) not null,
                    TempFreq FLOAT not null,
                    MixFreq FLOAT not null,
                    LogFilePath VARCHAR(255) not null,
                    WebPort INT not null
        );
        """)
        print("Configuration table created!")

        # Create a table for mixing. This will contain many log events
        cur.execute("""create table if not exists Mixing (
                    id int primary key auto_increment,
                    SensorId VARCHAR(255) not null,
                    MixingDate DATETIME not null,
                    SuccessStatus BOOL not null
        );
        """)
        print("Mixing table created!")

        # Create a table for Temperature measurements. This will contain many items and will be used for graphing
        cur.execute("""create table if not exists Temperature (
                    id int primary key auto_increment,
                    SensorId VARCHAR(255) not null,
                    MeasurementTime DATETIME not null,
                    MeasuredValue FLOAT not null
        );
        """)
        print("Temperature table created!")

        # Commit the changes to the database
        conn.commit()
        cur.close()
    except mariadb.Error as e:
        print(f"Error: {e}")

    return

def populateDefaults(conn, ip_address):
    try:
        cur = conn.cursor()
        # Insert default user
        cur.execute("INSERT INTO User (UserID, Email, Password) VALUES (?, ?, ?)", 
                    ('manbra', 'admin@admin.net', '1234'))
        # Insert default configuration
        cur.execute("INSERT INTO Configuration (IpAddress, ModuleList, DataBaseAddr, TempFreq, MixFreq, LogFilePath, WebPort) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                    (ip_address, "['84848-asd', '99536-ddsad']", '127.0.0.1', 30, 30, '/var/log/pibrewpal.log', 5000))
        
        print("Insertion success!")
        conn.commit()
        cur.close()
    except mariadb.Error as e:
        print(f"Error: {e}")
    return


def main():

    # Get current local ip address
    command = "ifconfig wlan0 | grep 'inet' | cut -d: -f2 | awk '{print $2}' | tr -d '\\n'"
    ip_address = os.popen(command).read().strip()

    conn = dbConnect()

    # Create tables if they don't exist already
    createTables(conn)

    # Populate with defaults, will fix later
    # populateDefaults(cur, ip_address)

    # Fetch all tables and print the result
    # cur.execute('show tables;')
    # result = cur.fetchall()
    # print(result)

    conn.close()


if __name__ == "__main__":
    main()