# -*-coding:Utf-8 -*

""" Ce module contient la classe Robot. """

class Robot:

    """Classe représentant un robot."""

    peut_traverser = False
    symbole = "X"
    def __init__(self, x, y, nom):
        self.x = x
        self.y = y
        self.symbole = nom

    def __repr__(self):
        return "<Robot du joueur : {} x={} y={}>".format(self.symbole,self.x, self.y)

    def __str__(self):
        return "Robot {}.{}".format(self.x, self.y)

    def get_symbole(self):
        return self.symbole
