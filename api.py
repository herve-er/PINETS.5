import hug
import time
import random
import string
import bddAccess


sessions_list = [] # {'usr_id': 1, 'start_time': 1234567890, 'session_id': 'abcde12345'}

def session_id_generator():
    #Generates a random string of 10 characters for the session id wich is not already in use
    result = ''.join(random.choice(string.ascii_letters) for i in range(10))
    for session in sessions_list:
        if session['session_id'] == result:
            return session_id_generator()
    return result


def validate_user(usr_login, usr_hash):
    usr = bddAccess.getUserbylogin(usr_login)
    if(not usr):
        return False
    print(usr)
    hash = usr['hash']
    if(hash == usr_hash):
        return True
    else:
        return False


def isSessionActive(usr_id):
    for session in sessions_list:
        #session maxtime = 5minutes
        if session['usr_id'] == usr_id:
            if session['start_time'] - time.time() < 300:
                return True
            else:
                removeSession(usr_id)
                return False
    return False   


def getSessionId(usr_id):
    for session in sessions_list:
        if session['usr_id'] == usr_id:
            if(isSessionActive(usr_id)):
                return session['session_id']
    return False


def addSession(usr_id):
    
    sessionId = session_id_generator()
    sessions_list.append({'usr_id': usr_id, 'start_time': time.time(), 'session_id': sessionId})
    return getSessionByUsrId(usr_id)


def removeSession(usr_id):
    for session in sessions_list:
        if session['usr_id'] == usr_id:
            sessions_list.remove(session)
            return True
    return False


def getSessionByUsrId(usr_id):
    for session in sessions_list:
        if session['usr_id'] == usr_id:
            return session
    return False


def getSessionBySessionId(session_id):
    for session in sessions_list:
        if session['session_id'] == session_id:
            return session
    return False


##IHM APIgetUserId
@hug.get('/startSession')
def startSession(usr_login: hug.types.text, usr_hash: hug.types.text):
    if(validate_user(usr_login, usr_hash)):
        usr_id = bddAccess.getUserbylogin(usr_login)['id_client']
        session = getSessionByUsrId(usr_id)
        if(session):
            res = session
            res['error_code'] = 200
            return session
        else:
            res = addSession(usr_id)
            res['error_code'] = 200
            return res
    else:
        return {'error': 'invalid usr_id or usr_hash', 'error_code': 400}


@hug.get('/endSession')
def endSession(session_id: hug.types.text):
    print("removing session")
    for session in sessions_list:
        if session['session_id'] == session_id:
            sessions_list.remove(session)
            res = {'success': 'session ended','error_code': 200}
            return res
    return {'error': 'invalid session_id', 'error_code': 401}


@hug.get('/getEnvironmentData')
def getEnvironmentData(session_id: hug.types.text, nb_values: hug.types.number = 1, timestamp: hug.types.number = 0):
    session = getSessionBySessionId(session_id)

    if(not session):
        return {'error': 'invalid session_id', 'error_code': 401}
    
    if(nb_values > 100):
        return {'error': 'too many values requested', 'error_code': 402}
    
    #verifie que le timestamp est valide
    if(timestamp != 0):
        if(timestamp > time.time()+10):
            return {'error': 'invalid timestamp (futur)', 'error_code': 403}
        
        if(timestamp < time.time()- 31536000):
            return {'error': 'invalid timestamp (too old, max 1 year)', 'error_code': 407}

    #mesure: {'room_name': 'room1', 'room_id', 'type': 'temperature', 'value': 60, 'time': 1234567890}
    #TODO: populate mesure_list with data from database
    #Ajoute la liste des rooms
    rooms = bddAccess.getRoomById(session['usr_id']) #[{'id_piece': 1, 'nom': 'room1'}, {'id_piece': 2, 'nom': 'room2'}, {'id_piece': 3, 'nom': 'room3'}]
    #Ajoute la liste des capteurs
    sensors = bddAccess.getSensor(session['usr_id']) #[{'id_capteur': 1, 'id_piece': 1, 'type': 'temperature'}, {'id_capteur': 2, 'id_piece': 1, 'type': 'humidity'}, {'id_capteur': 3, 'id_piece': 2, 'type': 'temperature'}, {'id_capteur': 4, 'id_piece': 2, 'type': 'humidity'}, {'id_capteur': 5, 'id_piece': 3, 'type': 'temperature'}, {'id_capteur': 6, 'id_piece': 3, 'type': 'humidity'}]
    #sensors = [{'id_capteur': 1, 'id_piece': 1, 'type_capteur': 'temperature'}, {'id_capteur': 2, 'id_piece': 1, 'type_capteur': 'humidity'}, {'id_capteur': 3, 'id_piece': 2, 'type_capteur': 'temperature'}, {'id_capteur': 4, 'id_piece': 2, 'type_capteur': 'humidity'}, {'id_capteur': 5, 'id_piece': 3, 'type_capteur': 'temperature'}, {'id_capteur': 6, 'id_piece': 3, 'type_capteur': 'humidity'}]
    rooms_data = []
    for room in rooms:
        #{'room_id': room['id_piece'], 'room_name': room['nom'], 'sensors': [{'type': 'temperature', 'id': 1}, {'type': 'humidity', 'id': 2}]}
        rooms_data.append({'room_id': room['id_piece'], 'room_name': room['nom'], 'sensors': []})
    for sensor in sensors:
        for room in rooms_data:
            if(sensor['id_piece'] == room['room_id']):
                room['sensors'].append({'type_capteur': sensor['type_capteur'], 'id': sensor['id_capteur']})

    capteurs_values = {}
    if(timestamp != 0):
        for sensor in sensors:
            capteurs_values[sensor['id_capteur']] = bddAccess.getSensorData(sensor['id_capteur'], timestamp)
    else:
        for sensor in sensors:
            capteurs_values[sensor['id_capteur']] = bddAccess.getSensorDataHist(sensor['id_capteur'], nb_values)

    sub_res = {}
    print(rooms_data)
    for room in rooms_data:
        sub_res[room['room_name']] = []
        if(capteurs_values[room['sensors'][0]['id']] != None):
            nb_sensor = len(room['sensors'])
            max_nb_value = 0
            for sensor in range(nb_sensor):
                if(len(capteurs_values[room['sensors'][sensor]['id']]) > max_nb_value):
                    max_nb_value = len(capteurs_values[room['sensors'][sensor]['id']])
            for nb_value in range(max_nb_value):
                single_value = {}
                for sensor in room['sensors']:
                    if(len(capteurs_values[sensor['id']]) > nb_value):
                        single_value[sensor['type_capteur']] = capteurs_values[sensor['id']][nb_value]['valeur']
                        single_value['timestamp'] = capteurs_values[sensor['id']][nb_value]['date_heure']
                sub_res[room['room_name']].append(single_value)

    res = {'rooms': sub_res, 'error_code': 200}
    return res
 
    #random time
    res = {'rooms':{
            'room1': [{
                'temperature': 20,
                'humidity': 60,
                'timestamp': 1234567890
            },{
                'temperature': 23,
                'humidity': 40,
                'timestamp': 1234567895
            }],
            'room2': [{
                'temperature': 22,
                'humidity': 55,
                'timestamp': 1234567890
            },
            {
                'temperature': 25,
                'humidity': 69,
                'timestamp': 1234567895
            }],
            'room3': [{
                'temperature': 23,
                'humidity': 40,
                'timestamp': 1234567890
            },{
                'temperature': 29,
                'humidity': 10,
                'timestamp': 1234567895
            }]
        },'error_code': 200}
    return res


@hug.get('/getRooms')
def getRooms(session_id: hug.types.text):

    session = getSessionBySessionId(session_id)
    if(not session):
        return {'error': 'invalid session_id', 'error_code': 401}
    
    list_rooms = bddAccess.getRoomById(session['usr_id'])
    res = {'rooms': list_rooms, 'error_code': 200}
    return res


@hug.get('/getPetLocation')
def getPetLocation(session_id: hug.types.text, timestamp: hug.types.number = 0):
    session = getSessionBySessionId(session_id)
    if not session:
        return {'error': 'invalid session_id', 'error_code': 401}
    
    if timestamp == 0 :
        timestamp = time.time()
    elif timestamp > time.time()+10:
        return {'error': 'invalid timestamp (futur)', 'error_code': 403}
    elif timestamp < time.time()- 31536000:
        return {'error': 'invalid timestamp (too old, max 1 year)', 'error_code': 407}
    
    position = bddAccess.getPosition_animal(session['usr_id'], timestamp)

    print(position)
    rooms = bddAccess.getRoomById(session['usr_id'])
    print(rooms)
    for r in rooms:
        if r["id_piece"] == position["id_piece"]:
            position["nom_piece"] = r["nom"]

    if "nom_piece" not in position:
        position["nom_piece"] = "unknown"

    res = {'room_id': position["id_piece"] , 'room_name': position["nom_piece"], 'time': position["date_heure"], 'error_code': 200}
    return res


@hug.get('/addUser')
def addUser(usr_hash: hug.types.text,usr_login: hug.types.text, usr_name: hug.types.text, usr_lastname: hug.types.text, usr_adress: hug.types.text):
    if(bddAccess.addUser(usr_hash, usr_name, usr_lastname, usr_adress,usr_login)):
        return {'success': 'user added','error_code': 200}
    else:
        return {'error': 'user not added', 'error_code': 405}


@hug.get('/removeUser')
def removeUser(usr_id: hug.types.text, usr_hash: hug.types.text):
    if(not validate_user(usr_id, usr_hash)):
        return {'error': 'invalid usr_id or password', 'error_code': 400}
   
    if(bddAccess.removeUser(usr_id)):
       return {'success': 'user removed','error_code': 200}
    else:
        return {'error': 'user not removed', 'error_code': 406}
    

@hug.get('/getUser')
def getUser(session_id: hug.types.text):
    session = getSessionBySessionId(session_id)
    if(not session):
        return {'error': 'invalid session_id', 'error_code': 401}
    
    res = bddAccess.getUserbyid(session['usr_id'])
    res = {'usr_id': res['id_client'], 'usr_name': res['nom'], 'usr_surname': res['prenom'], 'usr_adress': res['adresse'],'error_code': 200}
    return res


##Capteurs API
@hug.get('/addSensorData')
def addSensorData(sensor_id: hug.types.text, sensor_value: hug.types.float_number, timestamp: hug.types.number):
    id_mesure = bddAccess.addSensorData(sensor_id, timestamp, sensor_value)
    
    type_sensor = bddAccess.getSensorType(sensor_id)
    print("type sensor: ",type_sensor)
    if(type_sensor != None):
        if(type_sensor["type_capteur"] == "presence"):
            print("presence")
            bddAccess.setPosition_animal(id_mesure)
               
            
    return {'success': 'data added','error_code': 200}
    


@hug.response_middleware()
def CORS(request, response, resource):
    response.set_header('Access-Control-Allow-Origin', '*')

    
def start():
    print("starting server")
    api = hug.API(__name__).http.serve(port=8080)


start()
