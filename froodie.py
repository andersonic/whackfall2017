from flask import Flask, render_template, request
import json
from time import gmtime, strftime

app = Flask(__name__)

filename = 'data.json'

# Wipe any previous file contents and set an empty list.
def start_json_file():
    f = open(filename, 'w')
    f.write('[]')
    f.close()

# Read the JSON file and return a list of JSON objects
def read_database():
    f = open(filename, 'r')
    fileText = f.read()
    data = json.loads(fileText)
    f.close()
    return data

# Take a location and number of servings at that location. Construct a JSON object with those two
# pieces of information and the current time. Add this new item to the JSON file.
def add_location(currentLocation, numServings):
    data = {"location": currentLocation, "time": get_current_time(), "servings":numServings}
    oldData = read_database()
    oldData.append(data)
    with open(filename, 'w') as data_file:
        json.dump(oldData, data_file)

# Get the current time, in GMT+0, as a string.
def get_current_time():
    return strftime("%H:%M", gmtime())

# Loop through the list of JSON objects and return a list of just the locations.
def get_location_list():
    data = read_database()
    locations = []
    for location in data:
        locations.append(location['location'])
    return locations

# Decrease the recorded number of servings at a given location.
def decrement_servings(locationToDecrement):
    oldData = read_database()
    currentIndex = 0
    index = -1
    for datapoint in oldData:
        if datapoint['location'] == locationToDecrement:
            index = currentIndex
        currentIndex += 1
    if index != -1:
        oldData[index]['servings'] -= 1
    with open(filename, 'w') as data_file:
        json.dump(oldData, data_file)

# Does not work
def is_one_hour_old(oldTime):
    currentTime = get_current_time()
    currentTimeArray = [currentTime[0]*10 + currentTime[1], currentTime[3]*10 + currentTime[4]]
    oldTimeArray = [oldTime[0]*10 + oldTime[1], oldTime[3]*10 + oldTime[4]]

    if currentTimeArray[0] == 0:
        currentTime[0] += 24
    if oldTimeArray[0] == 0:
        oldTimeArray[0] += 24

    if oldTimeArray[0] - 1 > currentTimeArray[0]:
        return True
    elif oldTimeArray[0] > currentTimeArray[0] and oldTimeArray[1] >= currentTimeArray[1]:
        return True
    else:
        return False


# Loop through the locations and remove any locations whose number of remaining servings is below zero.
# Also define as finished any location over 1 hour old, though it doesn't work.
def remove_finished_locations():
    oldData = read_database()
    index = 0
    for datapoint in oldData:
        if datapoint['servings'] <= 0:
            del oldData[index]
        #elif is_one_hour_old(datapoint['time']):
            #del oldData[index]
        else:
            index += 1
    with open(filename, 'w') as data_file:
        json.dump(oldData, data_file)

@app.route('/')
def default():
    return render_template('default.html')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/getlocation')
def getlocation():
    remove_finished_locations()
    return render_template('getlocation.html')

@app.route('/havefood')
def havefood():
    return render_template('havefood.html')

@app.route('/wantfood', methods=['POST'])
def wantfood(source = None):
    theirLocation = request.form['yourlocation'].replace(" ", "+")
    data = read_database()
    foodLocations = ""
    for food in data:
        location = food['location'].replace(" ", "+")
        foodLocations += location + '|'
    image = "https://maps.googleapis.com/maps/api/staticmap?center="\
            + theirLocation + "&zoom=13&size=600x300&maptype=roadmap"\
            + "&markers=color:red%7Clabel:F%7C"\
            + foodLocations\
            + "&key=AIzaSyDEcCaNT7FKxd2p7DO37MuzS1NLsI59H10"
    return render_template('wantfood.html', source = image)

@app.route('/foodsubmission', methods=['POST'])
def foodsubmission():
    location = request.form['location']
    servings = request.form['servings']
    add_location(location, servings)
    return render_template('responsereceived.html')

if __name__ == '__main__':
    start_json_file()
    app.run(debug=True, use_reloader=True)
