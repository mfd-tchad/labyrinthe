import socket
import sys
from threading import Thread
import time

class Recepteur(Thread):

    """Thread chargé de recevoir les réponses du serveur 
    et de les interpréter.
    Il affiche les messages utiles au jeu dans la console.
    """

    def __init__(self, socket, emetteur):
        Thread.__init__(self)
        self.socket = socket
        self.pret = False
        self.termine = False
        self.emetteur = emetteur

    def stop(self):
        self.termine = True

    def run(self):
        """Code à exécuter pendant l'exécution du thread Recepteur."""
        while not self.termine:
            try:
                msg_recu = self.socket.recv(1024)
            except:
                print("Erreur de réception avec le serveur")
                print("Désolé, le jeu est terminé")
                self.termine = True
                self.emetteur.stop()
                continue
            else:
                msg_recu = msg_recu.decode()
            
            if msg_recu == "c":
                self.emetteur.demarre_jeu()
            elif msg_recu == "q":
                self.termine = True
            elif msg_recu == "g":
                print("Félicitations ! Vous avez gagné !!!")
                self.termine = True
                self.emetteur.stop()
                
            elif msg_recu == "f":
                print("Désolé, vous avez perdu...")
                self.termine = True
                self.emetteur.stop()
            else:
                self.emetteur.serveur_pret() # On indique à l'émetteur qu'il peut opérer
                print("\n",msg_recu)

def afficher_coups_autorises():
        print("Coups autorisés :")
        print("  Q pour sauvegarder et quitter la partie en cours")
        print("  E pour déplacer le robot vers l'est")
        print("  S pour déplacer le robot vers le sud")
        print("  O pour déplacer le robot vers l'ouest")
        print("  N pour déplacer le robot vers le nord")
        print("  Vous pouvez préciser un nombre après la direction")
        print("  Pour déplacer votre robot plus vite. Exemple n3")
        print("  MD pour déplacer le robot dans la direction D (E,S,O,N)")
        print("  PD pour déplacer le robot dans la direction D (E,S,O,N)")



class Emetteur(Thread):

    """ Thread chargé de lire les commandes du joueur et de les envoyer
    au serveur.
    """

    def __init__(self, socket):
        Thread.__init__(self)
        self.socket = socket
        self.pret = False
        self.demarre = False
        self.termine = False

    def serveur_pret(self):
        """ Méthode appelée entre autres par le Recepteur pour indiquer qu'un
        message est arrivé du serveur et qu'il est prêt à recevoir des commandes
        """
        self.pret = True

    def demarre_jeu(self):
        """ Méthode appelée entre autres par le Recepteur pour indiquer que le serveur 
        a lancé la partie 
        """
        self.pret = True
        self.demarre = True
        print("La partie est démarrée")
        afficher_coups_autorises()
        print("> ")

    def stop(self):
        print("Deconnexion en cours...")
        self.termine = True
        self.pret = False

    def envoyer_message(self,msg_a_envoyer):
        try:
            self.socket.send(msg_a_envoyer)
        except:
            print("Problème de connexion avec le serveur")

    def run(self):
        """Code à exécuter pendant l'exécution du thread Emetteur."""
        
        msg_a_envoyer = b""
        while not self.termine:
            # On attend un signal de la part du récepteur avant de demander un coup au joueur
            if not self.pret:   
                time.sleep(0.5)
                continue
            coup = input("> ")
            if coup == "":
                continue
            elif not self.demarre: #si la partie n'a pas encore démarré
                if coup.lower() == "c":
                    # On demande à commencer la partie
                    self.demarre = True
                    print("Nous attendons d'autres joueurs pendant quelques secondes max avant de démarrer...")          
                elif coup.lower() == "q":
                    print("Vous nous quittez déjà ? Déconnexion en cours...")
                    self.termine = True
                    # on envoie la demande de déconnexion au serveur
                else:
                    print("La partie n'est pas encore démarrée, taper c pour démarrer")
                    continue
                msg_a_envoyer = coup.lower().encode()
                self.envoyer_message(msg_a_envoyer)
                self.pret = False
            elif coup.lower() == "q":
                # On demande à quitter la partie au serveur
                msg_a_envoyer = b"q" 
                if not self.termine: #si le jeu n'est pas terminé par ailleurs
                    self.termine = True
                    print("Vous nous quittez déjà ? Déconnexion en cours...")
                    # On envoie le message
                    self.envoyer_message(msg_a_envoyer)
                self.pret = False
            elif coup[0].lower() in "nseo":
                lettre = coup[0].lower()
                msg_a_envoyer = lettre.encode()
                # On va essayer de convertir le déplacement en coups d'une case
                coup = coup[1:]
                if coup == "":
                    nombre = 1
                else:
                    try:
                        nombre = int(coup)
                    except ValueError:
                        print("Nombre invalide : {}".format(coup))
                        continue
                while nombre >= 1:
                    # On envoie le message
                    self.envoyer_message(msg_a_envoyer)
                    self.pret = False
                    time.sleep(0.6)
                    nombre -= 1
                time.sleep(0.6)
            elif coup[0].lower() in "mp" and len(coup) == 2:
                if coup[1].lower() in "nseo":
                    msg_a_envoyer = coup.lower().encode()
                    self.envoyer_message(msg_a_envoyer)
                    self.pret = False
                else:
                    afficher_coups_autorises()

            else:
                afficher_coups_autorises()
        print("Le programme s'est terminé proprement")

# Programme client principal
hote = "localhost"
port = 12800

print("On tente de se connecter avec le serveur...")
try:
    connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print("Désolé, l'opération a échoué, veuillez réessayer plus tard")
    exit(0)

try:
    connexion_avec_serveur.connect((hote, port))
except socket.error as msg:
    print("Désolé, la connexion a échoué, veuillez réessayer plus tard")
    print(msg)
    exit(0)
else:
    print("Connexion établie avec le serveur sur le port {}".format(port))


# Création des threads
thread_emetteur = Emetteur(connexion_avec_serveur)
thread_recepteur = Recepteur(connexion_avec_serveur, thread_emetteur)

# Lancement des threads
thread_recepteur.start()
thread_emetteur.start()

# Attend que le thread récepteur se termine
thread_recepteur.join()
thread_emetteur.join(timeout=1.0)
if thread_emetteur.is_alive(): # l'émetteur ne s'est pas arrêté seul
    try:
        thread_emetteur._stop() # On force son arrêt
    except:
        pass
try:
    connexion_avec_serveur.close()
except:
    pass
else:
    print("Vous êtes déconnecté. A bientôt...")
sys.exit(0)