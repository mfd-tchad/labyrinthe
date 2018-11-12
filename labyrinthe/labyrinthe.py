# -*-coding:Utf-8 -*

"""Ce module contient la classe Labyrinthe."""

import os
import pickle

from obstacle.mur import Mur
from obstacle.porte import Porte
from obstacle.sortie import Sortie
from obstacle.libre import Libre
from robot import Robot
import random

# Constantes


class Labyrinthe:

    """Classe représentant un labyrinthe.

    Un labyrinthe est une grille comprenant des murs placés à endroits fixes
    ainsi qu'un robot représentant chaque joueur (ajoutés après l'initialisation). D'autres types d'obstacles pourraient également s'y
    rencontrer.

    Paramètres à préciser à la construction :
        obstacles -- une liste des obstacles déjà positionnés

    Pour créer un labyrinthe à partir d'une chaîne (par exemple à partir
    d'un fichier), considérez la fonction 'creer_labyrinthe_depuis_chaine'
    définie au-dessous de la classe.

    """

    limite_absolue_x = 20
    limite_absolue_y = 20
    def __init__(self, obstacles):
        self.robot = []
        self.grille = {}
        self.invisibles = []
        self.gagnee = False
        dernier_obstacle = obstacles[-1]
        self.limite_x = min(dernier_obstacle.x +1, self.limite_absolue_x)
        self.limite_y = min(dernier_obstacle.y +1, self.limite_absolue_y)
        for obstacle in obstacles:
            if (obstacle.x, obstacle.y) in self.grille:
                raise ValueError("les coordonnées x={} y={} sont déjà " \
                        "utilisées dans cette grille".format(obstacle.x,
                        obstacle.y))

            if obstacle.x > self.limite_absolue_x or obstacle.y > self.limite_absolue_y:
                raise ValueError("l'obstacle {} a des coordonnées trop " \
                        "grandes".format(obstacle))

            self.grille[obstacle.x, obstacle.y] = obstacle

    def ajouter_robot_xy(self,num_robot,x,y):
        """ Ajoute un robot à des coordonnées x,y précisées 
        son numéro + 1 va devenir son symbole """
        robot = Robot (x, y, str(num_robot+1))
        self.grille[robot.x, robot.y] = robot
        self.robot.append(robot)

    def ajouter_robot(self,num_robot,cases_libres):
        """ Choisir une position de façon aléatoire pour le nouveau robot 
        dans la liste des cases libres, et place le robot à cette position """
        objet = random.choice(cases_libres)
        self.ajouter_robot_xy(num_robot,objet.x,objet.y) 
        cases_libres.remove(objet) 

    def retirer_robot(self, num_robot):
        """ Retire un robot de la liste des robots et de la grille """
        if num_robot >= 0:
            robot = self.robot[num_robot]
            del self.grille[robot.x,robot.y]
            del self.robot[num_robot]
        else:
            raise ValueError("le no de robot 'num_robot' est incorrect. On attend une valeur >=O ")

    def nom_robot(self,num_robot):
        return self.robot[num_robot].get_symbole()

    def creer_chaine(self):
        """ Transforme le labyrinthe en chaine de caractères.

        On prend les limites pour afficher la grille. Les obstacles et
        le robot sont affichés en utilisant leur attribut de classe 'symbole'.
        """
        y = 0
        grille = ""

        while y < self.limite_y:
            x = 0
            while x < self.limite_x:
                case = self.grille.get((x, y))
                if case:
                    grille += case.symbole
                else:
                    grille += " "

                x += 1

            grille += "\n"
            y += 1
        return grille

    def afficher(self):
        """Affiche le labyrinthe dans une console."""
        grille = self.creer_chaine()
        print(grille, end="")

    def actualiser_invisibles(self):
        """Cette méthode actualise les obstacles invisibles.

        Si le robot passe sur un obstacle passable (disons une porte),
        l'obstacle ne s'affiche pas. En fait, il est supprimé de la grille,
        mais placé dans les obstacles invisibles et sera de nouveau
        afficher quand le robot se sera de nouveau déplacé.

        """
        for obstacle in list(self.invisibles):
            if (obstacle.x, obstacle.y) not in self.grille:
                self.grille[obstacle.x, obstacle.y] = obstacle
                self.invisibles.remove(obstacle)

    def deplacer_robot(self, num_robot, direction):
        """Déplace le robot.

        La direction est à préciser sous la forme de chaîne, "n" (Nord),
        "e"(Est), "s" (Sud), ou "o" (Ouest). 
        Si le robot rencontre un obstacle impassable, il s'arrête.

        """
        robot = self.robot[num_robot]
        coords = [robot.x, robot.y]
        if direction == "n":
            coords[1] -= 1
        elif direction == "e":
            coords[0] += 1
        elif direction == "s":
            coords[1] += 1
        elif direction == "o":
            coords[0] -= 1
        else:
            raise ValueError("direction {} inconnue".format(direction))

        x, y = coords
        if x >= 0 and x < self.limite_x and y >= 0 and y < self.limite_y:
            # On essaye de déplacer le robot
            # On vérifie qu'il n'y a pas d'obstacle à cet endroit
            obstacle = self.grille.get((x, y))
            if obstacle is None or obstacle.peut_traverser:
                if obstacle:
                    self.invisibles.append(obstacle)

                # On supprime l'ancienne position du robot
                del self.grille[robot.x, robot.y]

                # On place le robot au nouvel endroit
                self.grille[x, y] = robot
                robot.x = x
                robot.y = y
                self.actualiser_invisibles()
                self.afficher()

                # On appelle la méthode 'arriver' de l'obstacle, si il existe
                if obstacle:
                    obstacle.arriver(self, robot)

    def murer_porte(self,num_robot,direction):
        """ Transforme en obstacle la porte qui se trouve juste à côté du robot
        de num_joueur dans la direction indiquee.
        direction peut valoir "n"(Nord), "e"(Est), "s" (Sud), ou "o" (Ouest). 
        Si l'obstacle dans la direction indiquée n'est pas une porte, rien ne se passe
        """
        robot = self.robot[num_robot]
        coords = [robot.x, robot.y]
        if direction == "n":
            coords[1] -= 1
        elif direction == "e":
            coords[0] += 1
        elif direction == "s":
            coords[1] += 1
        elif direction == "o":
            coords[0] -= 1
        else:
            raise ValueError("direction {} inconnue".format(direction))

        x, y = coords
        if x >= 0 and x < self.limite_x and y >= 0 and y < self.limite_y:
            # On essaye de mettre un mur
            # On vérifie qu'il y a bien une porte
            obstacle = self.grille.get((x, y))
            if obstacle :
                if obstacle.est_une_porte():
                    self.grille[(x,y)] = Mur(obstacle.x,obstacle.y)

    def percer_porte(self,num_robot,direction):
        """ Transforme en obstacle la porte qui se trouve juste à côté du robot
        de num_joueur dans la direction indiquee.
        direction peut valoir "n"(Nord), "e"(Est), "s" (Sud), ou "o" (Ouest). 
        Si l'obstacle dans la direction indiquée n'est pas une porte, rien ne se passe
        """
        robot = self.robot[num_robot]
        coords = [robot.x, robot.y]
        if direction == "n":
            coords[1] -= 1
        elif direction == "e":
            coords[0] += 1
        elif direction == "s":
            coords[1] += 1
        elif direction == "o":
            coords[0] -= 1
        else:
            raise ValueError("direction {} inconnue".format(direction))

        x, y = coords
        if x >= 0 and x < self.limite_x and y >= 0 and y < self.limite_y:
            # On essaye de mettre un mur
            # On vérifie qu'il y a bien une porte
            obstacle = self.grille.get((x, y))
            if obstacle and not obstacle.peut_traverser:
                self.grille[(x,y)] = Porte(obstacle.x,obstacle.y)

def creer_labyrinthe_depuis_chaine(chaine):
    """Crée un labyrinthe depuis une chaîne.
    Les symboles sont définis par correspondance ici.
    """
    symboles = {
        "o": Mur,
        ".": Porte,
        "u": Sortie,
        " ": Libre,
    }

    x = 0
    y = 0
    obstacles = []
    cases_libres = []
    for lettre in chaine:
        if lettre == "\n":
            x = 0
            y += 1
            continue
        elif lettre.lower() =="x": # on ignore le robot puisque les robots seront définis plus tard 
            objet = Libre(x, y)
            cases_libres.append(objet)
        elif lettre.lower() in symboles:
            classe = symboles[lettre.lower()]
            objet = classe(x, y)
            
            if type(objet) is Libre:
                cases_libres.append(objet)
            else:
                obstacles.append(objet)
        else:
            raise ValueError("symbole inconnu {}".format(lettre))

        x += 1

    labyrinthe = Labyrinthe(obstacles)
    return labyrinthe, cases_libres
