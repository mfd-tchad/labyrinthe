# -*-coding:Utf-8 -*

"""Fichier contenant la classe Mur, un obstacle impassable."""

from obstacle.obstacle import Obstacle

class Libre(Obstacle):

    """Classe représentant un mur, un obstacle impassable."""

    peut_traverser = True
    nom = "libre"
    symbole = " "
