from pypresence import Presence
from InquirerPy.utils import color_print
import glob, urllib, requests, json, os, time, win32gui, win32process, random , psutil

# Set this to your own client id from Discord developer portal
clientId = "1155101158780702830"

# Dont touch something below here unless you tryna do something or modify

updatable = True
redo = False

def find_between(s, first, last):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""
    
def check_roblox_focus():
        def get_active_window_process_name():
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['pid'] == pid:
                    return proc.info['name']
            return None

        active_window_process = get_active_window_process_name()
        if active_window_process != "RobloxPlayerBeta.exe":
            exit_roblox_rpc()
        return True

def exit_roblox_rpc():
    #subprocess.Popen([sys.executable, "main.py"])
    print('leaving roblox rpc')
    os._exit(1)

def getUser():
    return os.environ['USERPROFILE'].replace("C:\\Users\\", "")
    
def getCacheLog():
    list_of_files = glob.glob("C:\\Users\\" + getUser() + "\\AppData\\Local\\Roblox\\logs" + "\*.log")
    latest_file = max(list_of_files, key=os.path.getctime)
    fin = open(latest_file, "r", encoding = "ISO-8859-1").readlines()
    return fin

def getValuesFromCacheLog(logFile):

    placeId = 0
    jobId = 0
    lastJobid = 0
    serverIp = 0
    usrId = 1
    isPrivate = False
    connected = True

    line_position = 0
    for line in logFile:

        if line.find("place") > 0:
            toReplace = find_between(line, 'place ', " at")
            if toReplace != "":
                placeId = toReplace
                line_position = logFile.index(line)
                print(logFile.index(line), type(line), line)

        if line.find("Joining game") > 0:
            toReplace = find_between(line, "Joining game '", "'")
            if toReplace != "":
                jobId = toReplace
                line_position = logFile.index(line)
                print(logFile.index(line), type(line), line)

        if line.find("UDMUX") > 0:
            toReplace = find_between(line, "UDMUX server ", ",")
            if toReplace != "":
                serverIp = toReplace.split(":")
                line_position = logFile.index(line)
                print(logFile.index(line), type(line), line)

        if line.find("userid") > 0:
            toReplace = find_between(line, "userid:", ",")
            if toReplace != "":
                usrId = toReplace
                line_position = logFile.index(line)
                print(logFile.index(line), type(line), line)

        if line.find("joinGamePostPrivateServer") > 0:
            isPrivate = True
            line_position = logFile.index(line)
            print(logFile.index(line), type(line), line)

    for line in logFile:
        if line.find("Client:Disconnect") > 0 and logFile.index(line) > line_position:
            connected = False
            print(line_position)
            print(logFile.index(line), type(line), line)
        
    return connected, placeId, jobId, lastJobid, serverIp, usrId, isPrivate

def getDataForRPC(connected, placeId, jobId, lastJobid, usrId, isPrivate):
    rblx_logo = "https://blog.roblox.com/wp-content/uploads/2022/08/RBLX_Logo_Launch_Wordmark.png"
    activity = {} 

    activity['pid'] = os.getpid()   # Set process ID to close RPC as soon as this script is closed

    if connected == False:
        activity['details'] = "Idle in Menu"
        activity['large_image'] = rblx_logo

        return activity

    elif placeId and jobId:
        if lastJobid != jobId:
            universalId = urllib.request.urlopen("https://apis.roblox.com/universes/v1/places/" + placeId + "/universe")
            universalData = json.loads(universalId.read())
            theId = universalData["universeId"]

            lastJobid = jobId

            if theId:
                print(universalData, jobId, "to", lastJobid)
                
                response = urllib.request.urlopen("https://games.roblox.com/v1/games?universeIds=" + str(theId))
                data = json.loads(response.read())

                responsePlayer = urllib.request.urlopen("https://users.roblox.com/v1/users/" + str(usrId))
                dataPlayer = json.loads(responsePlayer.read())

                responeIcon = urllib.request.urlopen("https://thumbnails.roblox.com/v1/games/icons?universeIds=" + str(theId) + "&size=512x512&format=Png&isCircular=false")
                dataIcon = json.loads(responeIcon.read())

                responePfp = urllib.request.urlopen("https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds=" + str(usrId) + "&size=48x48&format=Png&isCircular=false")
                dataPfp = json.loads(responePfp.read())

                gameIcon = dataIcon["data"][0]["imageUrl"]
                pfpIcon = dataPfp["data"][0]["imageUrl"]
            
        activity['details'] = data["data"][0]["name"]
        activity['state'] = "By " + data["data"][0]["creator"]["name"]
        activity['large_image'] = gameIcon
        activity['large_text'] = data["data"][0]["name"]
        activity['small_image'] = pfpIcon
        activity['small_text'] = dataPlayer["name"]
        activity['buttons'] = [{"label": "View on website" ,"url": "https://www.roblox.com/games/" + placeId + "/"}]

        if isPrivate:
            activity['small_image'] = rblx_logo
            activity['small_text'] = "Protected"
            activity['state'] = "Reversed server"
        
        return activity
    
    else:
        activity['details'] = "Idle in Menu"
        activity['large_image'] = rblx_logo
        
        return activity

def get_activity():
    logFile = getCacheLog()

    connected, placeId, jobId, lastJobid, serverIp, usrId, isPrivate = getValuesFromCacheLog(logFile)
    print(getValuesFromCacheLog(logFile))

    activity = getDataForRPC(connected, placeId, jobId, lastJobid, usrId, isPrivate)
    print(activity)

    return activity


def main():
    global clientId
    while check_roblox_focus():
            
            activity = get_activity()
            print(activity)
            
            print("Starting Client")
            print("Waiting for Discord network...")

            RPC = Presence(clientId)
            RPC.connect()
            print("Connected to Discord network!")

            start_time = time.time()
            activity['start'] = start_time   # Set time of focused activity from the point of connection

            while True:
                check_roblox_focus()

                newActivity = get_activity()
                newActivity['start'] = start_time
                if activity != newActivity:
                    print(newActivity)
                    RPC.clear()  # Clear the presence
                    RPC.close()  # Close the RPC connection
                    break

                RPC.update(**activity)
            
                time.sleep(15)
    
if __name__ == "__main__":
        try:
            main()
        except Exception as error:
             color_print([('Red',f'{type(error), error}')])
