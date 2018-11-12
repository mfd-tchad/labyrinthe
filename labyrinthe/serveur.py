# -*-coding:Utf-8 -*

"""Ce fichier contient le code principal du jeu.

Exécutez-le avec Python pour lancer le jeu.

Avant le code principal, vous trouverez diverses fonctions d'envoi et de réception 
de messages vers un ou des clients
"""
import socket
import select
import os
import time

from carte import Carte

def creer_chaine_labyrinthe_et_envoyer(clients_connectes):
    """ Crée une chaine à partir du labyrinthe et l'envoie à tous les clients connectés """
    chaine = labyrinthe.creer_chaine()
    chaine = chaine.encode()
    for client in clients_connectes:
        client.send(chaine)

def envoyer_message_bienvenue(nom_joueur,num_joueur,clients_connectes):
    """ Envoie un message de bienvenue au nouveau joueur qui vient de se connecter (identifé par son nom et son numéro)
    et avertit les autres joueurs (connectés précédemment) de son arrivée 
    """
    msg_a_envoyer = "Bienvenue, joueur " + nom_joueur + "\nNotez bien votre numéro, il vous identifie dans le labyrinthe\n"
    msg_a_envoyer += "Appuyez sur c pour commencer la partie\n"
    msg_a_envoyer = msg_a_envoyer.encode()
    clients_connectes[num_joueur].send(msg_a_envoyer)
    # informer les autres joueurs de son arrivée
    if num_joueur >= 1:
        msg_a_envoyer = "Nouvelle connexion : le joueur " + nom_joueur + " est entré dans la partie\n"
        msg_a_envoyer += "Appuyez sur c pour commencer la partie\n"
        msg_a_envoyer = msg_a_envoyer.encode()
        for i in range (num_joueur):
            clients_connectes[i].send(msg_a_envoyer) 

def envoyer_message_abandon_joueur(nom_joueur,clients_connectes):
    """ Avertit les autres joueurs que le joueur nommé 'nom_joueur' a quitté la partie """
    msg_a_envoyer = "le joueur " + nom_joueur + " a quitté le jeu.\n "
    msg_a_envoyer = msg_a_envoyer.encode()
    for client in clients_connectes:
        client.send(msg_a_envoyer)

def envoyer_message_commence(clients_connectes):
    """ Avertit tous les joueurs que le jeu commence """
    msg_a_envoyer = b"c"
    for client in clients_connectes:
        client.send(msg_a_envoyer)

def envoyer_message_joueur_suivant(num_joueur,nom_joueur,clients_connectes):
    """ Avertit le joueur nommé 'nom_joueur' ayant pour numéro 'num_joueur' dans la liste 'clients-connectes'
    que c'est son tour de jouer.
    Et donne cette information aux autres joueurs connectés
    """
    msg_a_envoyer = "Joueur : " + nom_joueur + " , c'est à vous de jouer\n"
    msg_a_envoyer1 = "C'est le tour du joueur : " + nom_joueur + "\n"
    msg_a_envoyer = msg_a_envoyer.encode()
    msg_a_envoyer1 = msg_a_envoyer1.encode() 
    nb_joueurs = len(clients_connectes)  
    for i  in range(nb_joueurs):
        if i == num_joueur:
            clients_connectes[i].send(msg_a_envoyer)
        else:
            clients_connectes[i].send(msg_a_envoyer1)
            
def envoyer_message_gagne(num_joueur,nb_joueurs,clients_connectes):
    """ Avertit le joueur identifié par son numéro 'num_joueur' dans la liste 'clients_connectes'
    qu'il a gagné
    et informe les autres joueurs que le jeu est terminé de ce fait
    """
    msg_a_envoyer = b"g"                            
    # On annonce la fin de la partie aux autres joueurs
    msg_a_envoyer1 = b"f" 
    for i  in range(nb_joueurs):
        if i == num_joueur:
            clients_connectes[i].send(msg_a_envoyer)
        else:
            clients_connectes[i].send(msg_a_envoyer1)

def recevoir_message(nom_joueur,client):
    """ Reçoit un message de la part du client identifié par son socket et son nom
    et retourne la chaine de caractère décodée
    """
    msg_recu = client.recv(1024)
    msg_recu = msg_recu.decode()
    print("\nReçu {0} de la part du joueur {1}\n".format(msg_recu, nom_joueur))
    return msg_recu

############################################################################
# CODE PRINCIPAL du SERVEUR                                                #
############################################################################

# On charge les cartes existantes
cartes = []
for nom_fichier in os.listdir("cartes"):
    if nom_fichier.endswith(".txt"):
        chemin = os.path.join("cartes", nom_fichier)
        nom_carte = nom_fichier[:-3].lower()
        with open(chemin, "r") as fichier:
            contenu = fichier.read()
            try:
                carte = Carte(nom_carte, contenu)
            except ValueError as err:
                print("Erreur lors de la lecture de {} : {}.".format(
                        chemin, str(err)))
            else:
                cartes.append(carte)

# On affiche les cartes existantes
print("Labyrinthes existants :")
for i, carte in enumerate(cartes):
    print("  {} - {}".format(i + 1, carte.nom))

# Choix de la carte
labyrinthe = None
while labyrinthe is None:
    choix = input("Entrez un numéro de labyrinthe pour commencer à jouer : ")
    try:
        choix = int(choix)
    except ValueError:
        print("Choix invalide : {}".format(choix))
    else:
        if choix < 1 or choix > len(cartes):
            print("Numéro invalide : ", choix)
            continue
        carte = cartes[choix - 1]
        labyrinthe = carte.labyrinthe
        labyrinthe.afficher()

# Ouverture de la connexion
hote = ''
port = 12800
connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_principale.bind((hote, port))
connexion_principale.listen(5)
print("Le serveur écoute à présent sur le port {}".format(port))
print("On attend les clients.")

TEMPS_MAX_ATTENTE_COUP = 30 #timeout en secondes pour l'attente d'un coup
serveur_lance = True
clients_connectes = []
temps_attendu = 0
nb_joueurs = 0
num_joueur = 0
num_joueur_max = 0
commence = False
nb_tours_restants = 0
while serveur_lance:
    if not commence:
        # On va vérifier si de nouveaux clients demandent à se connecter
        # Pour cela, on écoute la connexion_principale en lecture
        # On attend maximum 5s
        connexions_demandees, wlist, xlist = select.select([connexion_principale],
        [], [], 5)
    
        for connexion in connexions_demandees:
            connexion_avec_client, infos_connexion = connexion.accept()
            # On ajoute le socket connecté à la liste des clients
            clients_connectes.append(connexion_avec_client)
            nb_joueurs += 1
            # On ajoute aléatoirement un robot dans le labyrinthe pour le nouveau joueur
            labyrinthe.ajouter_robot(num_joueur_max,cartes[choix-1].cases_libres)
            nom_joueur = labyrinthe.nom_robot(num_joueur_max)
            print("Un joueur s'est connecté : ", nom_joueur)
            num_joueur_max += 1
            # on lui souhaite la bienvenue et on informe les autres joueurs de son arrivée
            envoyer_message_bienvenue(nom_joueur,nb_joueurs-1,clients_connectes)
            # on envoie le labyrinthe actualisé à tous les joueurs
            creer_chaine_labyrinthe_et_envoyer(clients_connectes)
            
        # Maintenant, on écoute la liste des clients connectés à lire
        # On attend 1s maximum pour que plusieurs joueurs puissent entrer  
        clients_a_lire = []
        # On enferme l'appel à select.select dans un bloc try pour lever une exception
        # dans le cas oà la liste des clients connectés serait vide
        try:
            clients_a_lire, wlist, xlist = select.select(clients_connectes,
                [], [], 1)
        except select.error:
            pass
        else:
            for client in clients_a_lire:   # On parcourt la liste des clients à lire           
                num_joueur = clients_connectes.index(client)
                nom_joueur = labyrinthe.nom_robot(num_joueur)
                msg_recu = recevoir_message(nom_joueur,client)
                if msg_recu == "q": 
                    labyrinthe.retirer_robot(num_joueur)
                    print("Fermeture de la connexion avec joueur : ",nom_joueur)              
                    # envoyer l'accusé de réception de quitter au joueur
                    msg_a_envoyer = b"q"
                    client.send(msg_a_envoyer)  
                    clients_connectes.remove(client)  
                    client.close()              
                    nb_joueurs -= 1        
                    # s'il n'y a plus de joueur, on arrête le jeu
                    if not clients_connectes:
                        serveur_lance = False
                    else:
                        # On avertit les autres joueurs de l'abandon
                        envoyer_message_abandon_joueur(nom_joueur,clients_connectes)
                        creer_chaine_labyrinthe_et_envoyer(clients_connectes)
                        #del nom_joueurs[num_joueur] # on retire le joueur de la liste
                elif msg_recu == "c":
                    print("Demande de démarrage de la partie envoyée par joueur : {}, c'est parti...".format(nom_joueur))
                    commence = True
                    envoyer_message_commence(clients_connectes)
                    break
                else:
                    continue
                
    else: # si la partie est commencée
        # On met en place un système pour que les joueurs jouent chacun leur tour un coup
        # avec toutefois une issue si un joueur ne répond pas au bout de TEMPS_MAX_ATTENTE_COUP
        # Dans ce cas de timeout, il perd son tour
        clients_a_lire = []
        try:
            clients_a_lire, wlist, xlist = select.select(clients_connectes,
                [], [], 1)
        except select.error:
            pass
        else:
            # On cherche le joueur dont c'est le tour dans les clients à lire
            if clients_a_lire:             
                if clients_connectes[num_joueur] not in clients_a_lire:                   
                    # le joueur attendu n'a pas joué, on patiente 1 seconde avant de réessayer
                    if nb_tours_restants >= 0:
                        time.sleep(1)
                        nb_tours_restants -= 1
                        temps_attendu += 1
                          
                    elif temps_attendu < TEMPS_MAX_ATTENTE_COUP:
                        
                        print("On attend le coup du joueur : ",nom_joueur)
                        nb_tours_restants = 15
                        envoyer_message_joueur_suivant(num_joueur,nom_joueur,clients_connectes)
                    else:
                        print("Le joueur {} n'a pas réagi dans les temps, il perd son tour".format(nom_joueur))
                        num_joueur = (num_joueur + 1) % nb_joueurs
                        nom_joueur = labyrinthe.nom_robot(num_joueur)
                        print("On attend le coup du joueur : {0}".format(nom_joueur))
                        nb_tours_restants = 15
                        temps_attendu = 0
                else:
                    nb_tours_restants = 15
                    temps_attendu = 0
                    nom_joueur = labyrinthe.nom_robot(num_joueur)
                    client = clients_connectes[num_joueur]
                    msg_recu = recevoir_message(nom_joueur,client)
                    if len(msg_recu) == 1:
                        if msg_recu == "q":   
                            labyrinthe.retirer_robot(num_joueur)
                            print("Fermeture de la connexion avec joueur ",nom_joueur)     
                            msg_a_envoyer = b"q"
                            client.send(msg_a_envoyer)  
                            clients_connectes.remove(client)    
                            client.close()
                            nb_joueurs -= 1           
                            # s'il n'y a plus de joueur, on arrête le jeu
                            if not clients_connectes:
                                serveur_lance = False
                                continue
                            else: #avertir les autres joueurs de son départ
                                envoyer_message_abandon_joueur(nom_joueur,clients_connectes)

                        elif msg_recu in "neso" :
                            labyrinthe.deplacer_robot(num_joueur, msg_recu)
                                
                    elif msg_recu[0] == "m" and msg_recu[1] in "nseo":
                        labyrinthe.murer_porte(num_joueur, msg_recu[1])
                    elif msg_recu[0] == "p" and msg_recu[1] in "nseo":
                        labyrinthe.percer_porte(num_joueur,msg_recu[1])

                    # envoyer le nouveau labyrinthe à tous les joueurs 
                    creer_chaine_labyrinthe_et_envoyer(clients_connectes)
                    if labyrinthe.gagnee:
                        serveur_lance = False
                        envoyer_message_gagne(num_joueur,nb_joueurs,clients_connectes)
                    else:
                        if msg_recu[0] != "q":
                            num_joueur = (num_joueur + 1) % nb_joueurs 
                            nom_joueur = labyrinthe.nom_robot(num_joueur)
                        if nb_joueurs > 1:
                            envoyer_message_joueur_suivant(num_joueur,nom_joueur,clients_connectes)
                          
# On attend un peu avant de fermer les connexions, pour ne pas perturber les clients         
time.sleep(5)
print("Fermeture des connexions")
for client in clients_connectes:
    client.close()

connexion_principale.close()
