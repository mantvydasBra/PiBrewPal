import os
import sys
import bcrypt
import mariadb
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


PASSWORD = os.environ.get("db_password")
USERNAME = os.environ.get("db_user")
db_name = os.environ.get("db_name")
PORT = os.environ.get("db_port")
SALT = bytes(os.environ.get("SALT"), 'utf-8')

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
                    TempFreq INT not null,
                    MixFreq INT not null,
                    LogFilePath VARCHAR(255) not null,
                    WebPort INT not null,
                    MailTempMin FLOAT not null,
                    MailTempMax FLOAT not null
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
    except mariadb.Error as e:
        print(f"Error: {e}")

    cur.close()
    return

def populateDefaults(conn, ip_address):
    cur = conn.cursor()
    try:
        # Insert default configuration
        cur.execute("INSERT INTO Configuration (IpAddress, ModuleList, DataBaseAddr, TempFreq, MixFreq, LogFilePath, WebPort, MailTempMin, MailTempMax) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                    (ip_address, "['84848-asd', '99536-ddsad']", '127.0.0.1', 0, 0, '/var/log/pibrewpal.log', 5000, 0, 0))
        
        print("Insertion success!")
        conn.commit()
    except mariadb.Error as e:
        print(f"Error: {e}")

    cur.close()
    return

def loadTemperature():

    engine = create_engine(f"mariadb+mariadbconnector://{USERNAME}:{PASSWORD}@127.0.0.1:{PORT}/{db_name}")

    # Create a SQL query to select the desired columns
    query = "SELECT MeasurementTime, MeasuredValue FROM Temperature"

    # Execute the query and store the result in a DataFrame
    df = pd.read_sql_query(query, engine)

    # Close the database connection
    engine.dispose()

    return df

def writeTemp(MeasurementTime, MeasuredValue):
    conn = dbConnect()
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO Temperature (SensorId, MeasurementTime, MeasuredValue) VALUES (?, ?, ?)", 
                    ('28-03199779c8dc', MeasurementTime, MeasuredValue))
        print("New Temperature data inserted!")
        conn.commit()
    except mariadb.Error as e:
        print(f"Error: {e}")
    cur.close()
    return

def insertUser(userID, email, passw):
    conn = dbConnect()
    cur = conn.cursor()

    hashed_password = bcrypt.hashpw(passw.encode(), SALT)

    try:
        cur.execute("INSERT INTO User (UserID, Email, Password) VALUES (?, ?, ?)", 
                    (userID, email, hashed_password))
        print("New user was inserted!")
        conn.commit()
    except mariadb.Error as e:
        print(f"Error: {e}")
    
    cur.close()
    conn.close()
    return

def getUser(email, passw):
    conn = dbConnect()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id, password FROM User WHERE Email = ?", (email,))
        user = cur.fetchone()
         
        if user:
            user_id, hashed_pass = user

            entered_hashed_pass = bcrypt.hashpw(passw.encode(), SALT)

             # Check if the provided password matches the hashed password
            if bcrypt.checkpw(passw.encode(), hashed_pass.encode('utf-8')):
                print("Password matches! User authenticated.")
                return user_id
            else:
                print("Password does not match.")
                return False
        else:
            print("No user found with that email.")
            return False

    except mariadb.Error as e:
        print(f"Error: {e}")

    cur.close()
    conn.close()
    return
    
def getUserByID(user_id):
    conn = dbConnect()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id, userid, email, password FROM User WHERE id = %s", (user_id,))
        return cur.fetchone()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

def getConfig():
    conn = dbConnect()
    cur = conn.cursor()

    try:
        cur.execute("SELECT TempFreq, MixFreq, MailTempMin, MailTempMax FROM Configuration")
        return cur.fetchone()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()
            


def checkUserNumber():
    conn = dbConnect()
    cur = conn.cursor()

    try:
        cur.execute("SELECT COUNT(*) FROM User")
        result = cur.fetchone()
        if result[0] > 0:
            return False
        else:
            return True
    except mariadb.Error as e:
        print(f"Error: {e}")

    cur.close()
    conn.close()
    return
    
def getTempFreq():
    conn = dbConnect()
    cur = conn.cursor()

    try:
        cur.execute("SELECT TempFreq FROM Configuration")
        return cur.fetchone()
    except mariadb.Error as e:
        print(f"Error: {e}")

    cur.close()
    conn.close()
    return  

def getMinMaxEmail():
    conn = dbConnect()
    cur = conn.cursor()

    try:
        cur.execute("SELECT MailTempMin, MailTempMax FROM Configuration")
        return cur.fetchone()
    except mariadb.Error as e:
        print(f"Error: {e}")

    cur.close()
    conn.close()
    return

def setConfig(values: list):
    conn = dbConnect()
    cur = conn.cursor()
    
    try:
        # Begin a transaction
        conn.begin()

        # Update the User table if password is provided
        if values.get('password') != '':
            hashed_password = bcrypt.hashpw(values['password'].encode(), SALT)
            cur.execute("UPDATE User SET password=%s", (hashed_password,))

        # Check if the following values are not empty
        if values.get('email') is not None and values.get('name') is not None:
            if values.get('email') is not '' and values.get('name') is not '':
                cur.execute("UPDATE User SET email=%s, UserID=%s", (values['email'], values['name']))

        # Update the Configuration table
        if values.get('measurement_interval') is not None and values.get('mixing_interval') is not None:
            if values.get('measurement_interval') is not '' and values.get('mixing_interval') is not '':
                cur.execute("UPDATE Configuration SET TempFreq=%s, MixFreq=%s",
                        (values['measurement_interval'], values['mixing_interval']))
                                
        if values.get('temperature_min') is not None and values.get('temperature_max') is not None:
            if values.get('temperature_min') is not '' and values.get('temperature_max') is not '':
                cur.execute("UPDATE Configuration SET MailTempMin=%s, MailTempMax=%s",
                            (values['temperature_min'], values['temperature_max']))

        # Commit the transaction
        conn.commit()

    except mariadb.Error as e:
        # Rollback the transaction on error
        conn.rollback()
        print(f"Error: {e}")
    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()


def main():

    # Get current local ip address
    command = "ifconfig wlan0 | grep 'inet' | cut -d: -f2 | awk '{print $2}' | tr -d '\\n'"
    ip_address = os.popen(command).read().strip()

    conn = dbConnect()

    # Create tables if they don't exist already
    createTables(conn)

    # Populate with defaults, will fix later
    populateDefaults(conn, ip_address)

    conn.close()


if __name__ == "__main__":
    main()