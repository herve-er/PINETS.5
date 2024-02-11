import mysql.connector
connection_params =mysql.connector.connect(
    host="--removed for public github--",
    user="--removed for public github--",
    password="--removed for public github--",
    database="--removed for public github--",
    port=--removed for public github--
)


def connexion():  
    #connexion à la base de donnée avec les paramètres   
    try:
        if connection_params.is_connected():
            msg = "Connecté au serveur " + connection_params.get_server_info()

    except mysql.connector.Error as e:
        msg = "Erreur {}".format(e)
    return msg


def deconnexion():
    #deconnexion à la base de donnée 
    connection_params.close()
    

def addUser(Hash, nom, prenom, adresse,login):
    #ajouter un utilisateur à
    try:
        cursor = connection_params.cursor(buffered=True)
        query = "INSERT INTO Utilisateur (Hash, nom, prenom, adresse,login) VALUES (%s, %s, %s,%s,%s)"
        values = (Hash, nom, prenom, adresse,login)
        
        cursor.execute(query, values)
        connection_params.commit()
        msg= True
    except mysql.connector.Error as e:
        msg = "Erreur {}".format(e)
        return msg
    finally:
        if cursor:
            cursor.close()
        return msg


def addSensorData(id_capteur,date_heure,valeur):
    #ajouter une mesure dans la bdd
    try:
        cursor = connection_params.cursor(buffered=True)
        query = "INSERT INTO Mesure (id_capteur, date_heure, valeur) VALUES (%s, %s, %s)"
        values = (id_capteur,date_heure,valeur)
        
        cursor.execute(query, values) 
        connection_params.commit()
        #get the last id inserted
        last_id = cursor.lastrowid
        print("ajout capteur effectuée")
        return last_id
    except mysql.connector.Error as e:
        msg = "Erreur {}".format(e)
        return msg
    finally:
        if cursor:
            cursor.close()
    

def getSensorType(id_capteur):
    #Récupérer le type de capteur à partir de l'id du capteur
    try:
        cursor = connection_params.cursor(buffered=True)
        query = "SELECT type_capteur FROM Capteur WHERE id_capteur=%s"
        values = (id_capteur,)
        cursor.execute(query, values)
        result = cursor.fetchone()
        if result:
           column_names = [i[0] for i in cursor.description]
           result_dict = dict(zip(column_names, result))
           return result_dict
        else:
             return None  # Retournez None si aucun résultat trouvé
    except mysql.connector.Error as e:
        msg = "Erreur {}".format(e)
        return msg
    finally:
        if cursor:
            cursor.close()


def addSensor( id_client, id_piece, type_capteur):
    #ajouter un capteur à la bdd
    try:
        cursor = connection_params.cursor(buffered=True)
        query = "INSERT INTO Capteur ( id_client, id_piece, type_capteur) VALUES ( %s, %s, %s)"
        values = (id_client, id_piece, type_capteur)
        
        cursor.execute(query, values)
        connection_params.commit()
        msg="ajout capteur effectuée"
        return msg
    except mysql.connector.Error as e:
        msg = "Erreur {}".format(e)
        return msg
    finally:
        if cursor:
            cursor.close()


def addRoom(id_piece, nom, id_client):
    # Ajouter une piece à la bdd
    try:
        cursor = connection_params.cursor(buffered=True)
        query = "INSERT INTO Capteur (id_piece, nom, id_client) VALUES (%s, %s, %s)"
        values = (id_piece, nom, id_client)
        
        cursor.execute(query, values)
        connection_params.commit()
        msg="ajout capteur effectuée"
    except mysql.connector.Error as e:
        msg = "Erreur {}".format(e)
        return msg
    finally:
        if cursor:
            cursor.close()

def setPosition_animal(id_mesure):
    try:
       cursor=connection_params.cursor(buffered=True)
       query0="SELECT valeur FROM Mesure WHERE id_mesure=%s"
       value1 = (id_mesure,)
       cursor.execute(query0,value1)
       value = cursor.fetchone()
       
       query1="SELECT date_heure FROM Mesure WHERE id_mesure=%s"
       cursor.execute(query1,value1)
       date_heure = cursor.fetchone()
       
       query2="SELECT DISTINCT c.id_piece FROM Capteur c JOIN Mesure m ON c.id_capteur = m.id_capteur WHERE m.id_mesure = %s"
       cursor.execute(query2,value1)
       id_piece = cursor.fetchone()
       
       query3="SELECT id_client FROM Capteur WHERE id_capteur=(SELECT DISTINCT id_capteur FROM Mesure WHERE id_mesure=%s)"
       cursor.execute(query3, value1)
       id_client= cursor.fetchone()
       
       query3="SELECT id_animal FROM Utilisateur WHERE id_client = %s"
       value2=(id_client[0],)
       cursor.execute(query3,value2)
       id_animal = cursor.fetchone()
       values=(id_animal[0],id_client[0], id_piece[0], date_heure[0])
       if value[0]>0:
           query4="INSERT INTO Position_animal (id_animal, id_client, id_piece, date_heure) VALUES (%s,%s, %s, %s)"
           
           cursor.execute(query4, values)
           connection_params.commit()
           msg="ajout capteur effectuée"
           return msg
       elif(verification_animal_present(id_client[0])==False):
           query4="INSERT INTO Position_animal (id_animal, id_client, id_piece, date_heure) VALUES (%s,%s, %s, %s)"
           values=(id_animal[0],id_client[0], 0, date_heure[0])
           cursor.execute(query4, values)
           connection_params.commit()
           msg="ajout capteur effectuée"
       
    except mysql.connector.Error as e:
        msg = "Erreur {}".format(e)
        return msg
    finally:
        if cursor:
            cursor.close()

def verification_animal_present(id_client):
    try:
        cursor = connection_params.cursor(buffered=True)
        query="SELECT DISTINCT id_capteur FROM Capteur WHERE id_client=%s AND type_capteur='presence'"
        cursor.execute(query,(id_client,))
        capteurs = cursor.fetchall()
    
        result_list=[]
    
        for capteur_id in capteurs:
            # Obtenez les informations du capteur pour chaque capteur_id
            query2 ="SELECT valeur,id_mesure FROM Mesure WHERE id_capteur = %s ORDER BY date_heure DESC LIMIT 1"
            cursor.execute(query2, (capteur_id[0],))
            result = cursor.fetchone()
            if result:
                # Ajoutez lesinformations du capteur au dictionnaire
                result_dict=result[0]
                result_list.append(result_dict)
                
        
        if all(element == 0 for element in result_list):
            return False
        else:
            return True
    except mysql.connector.Error as e:
        msg = "Erreur {}".format(e)
        return msg
    finally:
        if cursor:
            cursor.close()

def removeUser(id_client):
    #Suppression d'un utilisateur avecc son id en paramètre
    try:
        cursor = connection_params.cursor(buffered=True)
        query="DELETE FROM Utilisateur WHERE id_client= %s"
        values = (id_client,)
        cursor.execute(query,values)
        connection_params.commit()
        msg="utilisateur supprimé"
    except mysql.connector.Error as e:
        msg = "Erreur {}".format(e)
        return msg
    finally:
        if cursor:
            cursor.close()


def removeSensor(id_capteur):
    #Suppression d'un capteur avec son id en paramètre
    try:
        cursor = connection_params.cursor(buffered=True)
        query="DELETE FROM Capteur WHERE id_capteur= %s"
        values = (id_capteur,)
        cursor.execute(query,values)
        connection_params.commit()
        msg="utilisateur supprimé"
    except mysql.connector.Error as e:
        msg = "Erreur {}".format(e)
        return msg
    finally:
        if cursor:
            cursor.close()


def removeSensorData(id_mesure):
    #Suppression d'une mesure avec son id en paramètre

    try:
        cursor = connection_params.cursor(buffered=True)
        query="DELETE FROM Mesure WHERE id_mesure= %s"
        values = (id_mesure,)
        cursor.execute(query,values)
        connection_params.commit()
        msg="utilisateur supprimé"
    except mysql.connector.Error as e:
        msg = "Erreur {}".format(e)
        return msg
    finally:
        if cursor:
            cursor.close()          


def removeRoom(id_piece):
    #Suppression d'une piece avec son id en paramètre

    try:
        cursor = connection_params.cursor(buffered=True)
        query="DELETE FROM Piece WHERE id_piece= %s"
        values = (id_piece,)
        cursor.execute(query,values)
        connection_params.commit()
        msg="utilisateur supprimé"
    except mysql.connector.Error as e:
        msg = "Erreur {}".format(e)
        return msg
    finally:
        if cursor:
            cursor.close()  


def removePosition_animal(id_position):
    #Suppression d'une position de l'animal avec son id en paramètre

    try:
        cursor = connection_params.cursor(buffered=True)
        query="DELETE FROM Position_animal WHERE id_position= %s"
        values = (id_position,)
        cursor.execute(query,values)
        connection_params.commit()
        msg="utilisateur supprimé"
    except mysql.connector.Error as e:
        msg = "Erreur {}".format(e)
        return msg
    finally:
        if cursor:
            cursor.close()     
        

def getSensorData(date_heure,id_capteur):
    # Récupérer la mesure d'un capteur à la date la plus proche de date_heure
    #La fonction renvoie sous forme de dictionnaire les données suivantes : id_mesure, valeur, time réel, type_capteur
    try:
        cursor = connection_params.cursor(buffered=True)
        query="SELECT id_mesure,valeur,date_heure FROM Mesure WHERE id_capteur = %s ORDER BY ABS(date_heure- %s) LIMIT 1"
        values = (id_capteur,date_heure)
        cursor.execute(query,values)
        result = cursor.fetchone()  
        if result:
           column_names = [i[0] for i in cursor.description]

           result_dict = dict(zip(column_names, result))
           
           query2="SELECT type_capteur FROM Capteur WHERE id_capteur=(SELECT id_capteur FROM Mesure WHERE id_mesure=%s)"
           value2=(result_dict['id_mesure'],)
           cursor.execute(query2,value2)
           type_capteur=cursor.fetchone()
           result_dict['type_capteur'] = type_capteur[0]
           
           return result_dict
        else:
             return None  # Retournez None si aucun résultat trouvé
        
    except mysql.connector.Error as e:
        result = "Erreur {}".format(e)
    finally:
        if cursor:
            cursor.close()


def getUserbyid(id_client):
    # Cette fonction renvoie sous forme de dictionnnaire les données suivantes : id_client,nom,prenom,adresse,login
    try:
        cursor = connection_params.cursor(buffered=True)
        query="SELECT id_client,nom,prenom,adresse,login FROM Utilisateur WHERE id_client= %s"
        values = (id_client,)
        cursor.execute(query,values)
        result = cursor.fetchone()
        if result:
           column_names = [i[0] for i in cursor.description]

           result_dict = dict(zip(column_names, result))
           return result_dict
        else:
             return None  # Retournez None si aucun résultat trouvé

    except mysql.connector.Error as e:
        result = "Erreur {}".format(e)
        return result
    finally:
        if cursor:
            cursor.close()
        

def getUserbylogin(login):
    # Cette fonction renvoie sous forme de dictionnnaire les données suivantes : hash,id_client,nom,prenom,adresse,login
    try:
        cursor = connection_params.cursor(buffered=True)
        query="SELECT hash,id_client,nom,prenom,adresse,login FROM Utilisateur WHERE login= %s"
        values = (login,)
        cursor.execute(query,values)
        result = cursor.fetchone()
        if result:
           column_names = [i[0] for i in cursor.description]

           result_dict = dict(zip(column_names, result))
           return result_dict
        else:
             return None  # Retournez None si aucun résultat trouvé

    except mysql.connector.Error as e:
        result = "Erreur {}".format(e)
        return result
    finally:
        if cursor:
            cursor.close()

            
def getSensor(id_client):
    # Cette fonction renvoie l'id du capteur à partir de l'id_client
    try:

        cursor = connection_params.cursor(buffered=True)
        query="SELECT id_capteur FROM Capteur WHERE id_client=%s"
        cursor.execute(query,(id_client,))
        capteurs = cursor.fetchall()
        
        result_list=[]
        
        for capteur_id in capteurs:
            query2 = "SELECT id_capteur, type_capteur, id_piece FROM Capteur WHERE id_capteur=%s"
            cursor.execute(query2, (capteur_id[0],))
            result = cursor.fetchone()
     
            if result:
                column_names = [i[0] for i in cursor.description]

                result_dict= dict(zip(column_names, result))
                result_list.append(result_dict)


        return result_list if result_list else None

         
    except mysql.connector.Error as e:
        result = "Erreur {}".format(e)
        return result


def getPosition_animal(id_client,date_heure):
    # Cette fonction renvoie la position de l'animal à l'heure la plus proche de date_heure
    try:
        cursor = connection_params.cursor(buffered=True)
        query="SELECT * FROM Position_animal WHERE id_client= %s ORDER BY ABS(date_heure- %s) LIMIT 1"
        values = (id_client,date_heure)
        cursor.execute(query,values)
        result = cursor.fetchone()
        if result:
           column_names = [i[0] for i in cursor.description]

           result_dict = dict(zip(column_names, result))
           return result_dict
        else:
             return None  # Retournez None si aucun résultat trouvé
    except mysql.connector.Error as e:
        result = "Erreur {}".format(e)
        return result
    finally:
        if cursor:
            cursor.close()


def getRoom(id_piece):
    #Cette fonction renvoie une piece de la bdd par l'id de la piece
    try:
        cursor = connection_params.cursor(buffered=True)
        query="SELECT * FROM Piece WHERE id_piece= %s"
        values = (id_piece,)
        cursor.execute(query,values)
        result = cursor.fetchone()
        if result:
           column_names = [i[0] for i in cursor.description]

           result_dict = dict(zip(column_names, result))
           return result_dict
        else:
             return None  # Retournez None si aucun résultat trouvé
    except mysql.connector.Error as e:
        result = "Erreur {}".format(e)
        return result
    finally:
        if cursor:
            cursor.close()


def getRoomById(id_client):
    #Cette fonction renvoie les pieces d'un utilisateur 

    try:
        cursor = connection_params.cursor(buffered=True)
        query="SELECT * FROM Piece WHERE id_client= %s"
        values = (id_client,)
        cursor.execute(query,values)
        result = cursor.fetchall()
        if result:
           column_names = [i[0] for i in cursor.description]

           result_dict = [dict(zip(column_names, row)) for row in result]
           return result_dict
        else:
             return None  # Retournez None si aucun résultat trouvé
    except mysql.connector.Error as e:
        result = "Erreur {}".format(e)
        return result
    finally:
        if cursor:
            cursor.close()


def getSensorDataHist(id_capteur,nb_val):
    #Cette fonction renvoie l'historique des valeurs 
    try:
        cursor = connection_params.cursor(buffered=True)
        query="SELECT m.valeur, m.date_heure FROM Capteur c LEFT JOIN Mesure m ON c.id_capteur = m.id_capteur WHERE c.id_capteur=%s ORDER BY m.date_heure DESC LIMIT %s"
        cursor.execute(query,(id_capteur,nb_val))
        result = cursor.fetchall()
        if result:
           column_names = [i[0] for i in cursor.description]
           result_dict =  [dict(zip(column_names, row)) for row in result]
           
           return result_dict
        else:
             return None  # Retournez None si aucun résultat trouvé
    except mysql.connector.Error as e:
        result = "Erreur {}".format(e)
    return result   


def getHistoric_th():
    #WARNING : NOT USED !!!!!
    try:
        cursor = connection_params.cursor(buffered=True)
        query="(SELECT * FROM Capteur INNER JOIN Mesure ON Capteur.id_capteur = Mesure.id_capteur WHERE Capteur.type_capteur = 'temperature' ORDER BY Mesure.date_heure DESC LIMIT 2) UNION (SELECT * FROM Capteur INNER JOIN Mesure ON Capteur.id_capteur = Mesure.id_capteur WHERE Capteur.type_capteur = 'humidité' ORDER BY Mesure.date_heure DESC LIMIT 2)"
        cursor.execute(query)
        result = cursor.fetchall()
        if result:
           column_names = [i[0] for i in cursor.description]

           result_dict = [dict(zip(column_names, row)) for row in result]
           return result_dict
        else:
             return None  # Retournez None si aucun résultat trouvé
    except mysql.connector.Error as e:
        result = "Erreur {}".format(e)
        return result
    finally:
        if cursor:
            cursor.close()   


def getHistoric_mouv():
    #WARNING : NOT USED !!!!!
    try:
        cursor = connection_params.cursor(buffered=True)
        query="(SELECT * FROM Position_animal INNER JOIN Piece ON Position_animal.id_piece = Piece.id_piece ORDER BY Position_animal.date_heure DESC LIMIT 2)"
        cursor.execute(query)
        result = cursor.fetchall()
        if result:
           column_names = [i[0] for i in cursor.description]

           result_dict = [dict(zip(column_names, row)) for row in result]
           return result_dict
        else:
             return None  # Retournez None si aucun résultat trouvé
    except mysql.connector.Error as e:
        result = "Erreur {}".format(e)
        return result   
    finally:
        if cursor:
            cursor.close()

