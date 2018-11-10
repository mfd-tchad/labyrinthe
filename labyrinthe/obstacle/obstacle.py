# -*-coding:Utf-8 -*

"""Fichier contenant la base des obstacles."""

class Obstacle:

    """Classe représentant tous les obstacles.

    Les obstacles sont généralement hérités de cette classe. Elle
    définit plusieurs méthodes et attributs qu'il faudra peut-être modifier
    dans les classes filles.

    """

    nom = "obstacle"
    peut_traverser = True
    symbole = ""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "<{nom} (x={x}, y={y})>".format(nom=self.nom,
                x=self.x, y=self.y)

    def __str__(self):
        return "{nom} ({x}.{y})".format(nom=self.nom, x=self.x, y=self.y)

    def arriver(self, labyrinthe, robot):
        """Méthode appelée quand le robot arrive sur la case.

        Il peut être utile de redéfinir cette méthode dans certaines
        circonstances.

        """
        pass

    def est_une_porte(self):
        return(False)
        
 #   def murer(self):
        """Méthode appelée pour changer la nature de l'obstacle
        Il est utile de redéfinir cette methode dans la classe Porte"""
  #      self.symbole = "."
   #     self.peut_traverser = False
