import unittest
from labyrinthe import Labyrinthe, creer_labyrinthe_depuis_chaine
#from labyrinthe import labyrinthe

from obstacle.mur import Mur
from obstacle.porte import Porte
from obstacle.sortie import Sortie
from obstacle.libre import Libre
from robot import Robot
import random

class LabyrintheTest(unittest.TestCase):

    """Test case utilisé pour tester les fonctions du module 'labyrinthe'."""
    def setUp(self):
        """Initialisation des tests."""
        self.num_robot = 0
        self.chaine = "OOOOOOOOOO\nO . O.O  O\nO      O O\nO . O OO O\nOOOOOOOOOO\n"
        self.obstacles = [Mur(0,0),Mur(1,0),Mur(2,0),Mur(3,0),Mur(4,0),Mur(5,0),Mur(6,0),\
        Mur(0,1),Porte(3,1),Mur(6,1),\
        Mur(0,2),Mur(4,2),Mur(6,2),\
        Mur(0,3),Mur(2,3),Porte(3,3),Mur(4,3),Mur(6,3),\
        Mur(0,4),Mur(2,4),Mur(3,4),Mur(4,4),Sortie(6,4),\
        Mur(0,5),Mur(2,5),Porte(5,5),Mur(6,5),\
        Mur(0,6),Mur(1,6),Mur(2,6),Mur(3,6),Mur(4,6),Mur(5,6),Mur(6,6)]
        self.x = 5
        self.y = 4

    def test_creer_labyrinthe(self):
        labyrinthe = Labyrinthe(self.obstacles)
        labyrinthe.afficher()
        for element in labyrinthe.grille.values():
            self.assertIn(element,self.obstacles)

    def test_creer_labyrinthe_depuis_chaine(self):
        """ Teste la création d'un labyrinthe à partir d'une chaine et inversement"""
        cases_libres = []
        labyrinthe, cases_libres = creer_labyrinthe_depuis_chaine(self.chaine)
        for element in cases_libres:
            self.assertIsInstance(element,Libre) 
        chaine1 = labyrinthe.creer_chaine()
        self.assertEqual(self.chaine,chaine1)

    def test_ajouter_robot(self):
        """ Teste le fonctionnement de la méthode 'ajouter_robot' """
        cases_libres = []
        labyrinthe, cases_libres = creer_labyrinthe_depuis_chaine(self.chaine)
        grille_sauv = list(labyrinthe.grille)
        self.assertEqual(len(labyrinthe.robot),0)
        
        labyrinthe.ajouter_robot(self.num_robot,cases_libres)
        # On vérifie qu'un robot a bien été créé et ajouté à la liste
        self.assertEqual(len(labyrinthe.robot),1)
        self.assertIsInstance(labyrinthe.robot[self.num_robot], Robot)
        # On vérifie que le robot a bien été introduit dans la grille
        robot = labyrinthe.robot[self.num_robot]
        self.assertNotIn((robot.x,robot.y),grille_sauv)
        self.assertIsInstance(labyrinthe.grille[robot.x,robot.y],Robot)
        # On vérifie que le robot a bien été choisi dans les limites
        self.assertLess(robot.x,labyrinthe.limite_x)
        self.assertLess(robot.y,labyrinthe.limite_y)

        # On teste l'ajout d'un deuxième robot
        labyrinthe.ajouter_robot(self.num_robot+1,cases_libres)
        robot1 = labyrinthe.robot[self.num_robot+1]
        self.assertIsInstance(labyrinthe.grille[robot1.x,robot1.y],Robot)
        # on vérifie qu'il est bien différent du premier
        self.assertNotEqual(robot,robot1)
        self.assertNotEqual(robot1.symbole,robot.symbole)

    def test_retirer_robot(self):
        """ Teste le retrait d'un robot """
        labyrinthe, cases_libres = creer_labyrinthe_depuis_chaine(self.chaine)
        labyrinthe.ajouter_robot(self.num_robot,cases_libres)
        robot = labyrinthe.robot[self.num_robot]
        
        labyrinthe.retirer_robot(self.num_robot)
        self.assertEqual(len(labyrinthe.robot),0)
        # on vérifie que le robot ne se trouve plus dans la grille
        self.assertNotIn((robot.x,robot.y),labyrinthe.grille.keys())
    

        # Maintenant on teste le retrait d'un robot sur deux
        labyrinthe.ajouter_robot(self.num_robot,cases_libres)
        robot = labyrinthe.robot[self.num_robot]
        labyrinthe.ajouter_robot(self.num_robot+1,cases_libres)
        robot1 = labyrinthe.robot[self.num_robot+1]
        nom_robot1 = labyrinthe.nom_robot(self.num_robot+1)
        # On supprime le premier robot créé, alors le 2eme devient premier dans la liste
        labyrinthe.retirer_robot(self.num_robot)
        # On vérifie que le deuxième robot créé n'a pas changé de nom, 
        # même s'il a changé de numéro d'ordre
        self.assertEqual(nom_robot1,labyrinthe.nom_robot(self.num_robot))
        # Et qu'il n'a pas changé de position
        self.assertTupleEqual((robot1.x,robot1.y),\
        (labyrinthe.robot[self.num_robot].x,labyrinthe.robot[self.num_robot].y))



    def test_deplacer_robot(self):
        """ Teste le déplacement d'un robot """
        labyrinthe = Labyrinthe(self.obstacles)
        # on ajoute un robot à côté de la sortie
        labyrinthe.ajouter_robot_xy(self.num_robot,self.x,self.y)

        # on tente un déplacement vers un obstacle
        labyrinthe.deplacer_robot(self.num_robot,"o")
        # on vérifie que le robot n'a pas bougé
        robot = labyrinthe.robot[self.num_robot]
        self.assertTupleEqual((robot.x,robot.y),(self.x,self.y))
        self.assertIsInstance(labyrinthe.grille[self.x,self.y],Robot)

        # on déplace le robot vers une porte et on vérifie que ça passe
        labyrinthe.deplacer_robot(self.num_robot,"s")
        self.assertTupleEqual((robot.x,robot.y),(self.x,self.y+1))
        self.assertIsInstance(labyrinthe.grille[self.x,self.y+1],Robot)
        # on vérifie aussi que la porte est enregistrée dans les points invisibles
        self.assertIsInstance(labyrinthe.invisibles[0],Porte)

        # et si on sort de la porte, elle réapparait dans la grille
        labyrinthe.deplacer_robot(self.num_robot,"n")
        self.assertTupleEqual((robot.x,robot.y),(self.x,self.y))
        self.assertIsInstance(labyrinthe.grille[self.x,self.y],Robot)
        self.assertIsInstance(labyrinthe.grille[self.x,self.y+1],Porte)

        # on déplace vers la sortie et on vérifie que la partie est gagnée
        self.assertFalse(labyrinthe.gagnee)
        labyrinthe.deplacer_robot(self.num_robot,"e")
        self.assertTupleEqual((robot.x,robot.y),(self.x+1,self.y))
        self.assertIsInstance(labyrinthe.grille[self.x+1,self.y],Robot)
        self.assertTrue(labyrinthe.gagnee)


    def test_murer_porte(self):
        """ Teste le murage d'une porte : transformation d'une porte en mur """
        labyrinthe = Labyrinthe(self.obstacles)
        # on ajoute un robot à côté d'une porte
        labyrinthe.ajouter_robot_xy(self.num_robot,self.x,self.y)
        self.assertIsInstance(labyrinthe.grille[self.x,self.y+1],Porte)
        labyrinthe.murer_porte(self.num_robot,"s")
        self.assertIsInstance(labyrinthe.grille[self.x,self.y+1],Mur)

    def test_percer_porte(self):
        """ Teste la transformation d'un mur en porte """
        labyrinthe = Labyrinthe(self.obstacles)
        # on ajoute un robot à côté d'un mur
        labyrinthe.ajouter_robot_xy(self.num_robot,self.x,self.y)
        self.assertIsInstance(labyrinthe.grille[self.x-1,self.y],Mur)
        labyrinthe.percer_porte(self.num_robot,"o")
        self.assertIsInstance(labyrinthe.grille[self.x,self.y+1],Porte)

