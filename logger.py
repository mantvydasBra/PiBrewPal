# Function to write into log file
def writeLog(curTime, temperature):
    # Check if both variables have any data in them
    if curTime is not None and temperature is not None:
        strLine = f"Temperature measured! Time: {curTime} Temperature: {temperature}\n---------------------------\n"
        # Write to file
        with open("events.log", "a") as file:
            file.write(strLine + "\n")

# Function to read log file and load it into dashboard
def getLog():
    with open("events.log", "r") as file:
        logData = file.read()
        # If there is any data, return it
        if logData:
            return logData

