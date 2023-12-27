
def writeLog(curTime, temperature):
    if curTime is not None and temperature is not None:
        strLine = f"Temperature measured! Time: {curTime} Temperature: {temperature}\n---------------------------\n"
        with open("events.log", "a") as file:
            file.write(strLine + "\n")

def getLog():
    with open("events.log", "r") as file:
        logData = file.read()
        if logData:
            return logData

