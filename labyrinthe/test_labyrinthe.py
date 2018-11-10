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
        self.num_robot = 1
        self.chaine = "OOOOOOOOOO\nO . O.O  O\nO      O O\nO . O OO O\nOOOOOOOOOO\n"
    
    def test_creer_labyrinthe_depuis_chaine(self):
        """ Teste la création d'un labyrinthe à partir d'une chaine et inversement"""
        cases_libres = []
        labyrinthe, cases_libres = creer_labyrinthe_depuis_chaine(self.chaine)
        for element in cases_libres:
            self.assertIsInstance(element,Libre) 
        chaine1 = labyrinthe.creer_chaine()
        self.assertEqual(self.chaine,chaine1)
        print(self.chaine)
        print(chaine1)

    def test_ajouter_robot(self):
        """ Teste le fonctionnement de la méthode 'ajouter_robot' """
        cases_libres = []
        labyrinthe, cases_libres = creer_labyrinthe_depuis_chaine(self.chaine)
        cases_libres_sauv = list(cases_libres)
        grille_sauv = list(labyrinthe.grille)
        self.assertEqual(len(labyrinthe.robot),0)
        
        labyrinthe.ajouter_robot(self.num_robot,cases_libres)
        # On vérifie qu'un robot a bien été créé et ajouté à la liste
        self.assertEqual(len(labyrinthe.robot),1)
        self.assertIsInstance(labyrinthe.robot[self.num_robot-1], Robot)
        # On vérifie que le robot a bien été introduit dans la grille
        robot = labyrinthe.robot[self.num_robot-1]
        self.assertNotIn((robot.x,robot.y),grille_sauv)
        self.assertIsInstance(labyrinthe.grille[robot.x,robot.y],Robot)
        # On vérifie que le robot a bien été choisi parmi les cases libres
        self.assertEqual(labyrinthe.grille[robot.x,robot.y],str(self.num_robot))
        self.assertIn(Libre(robot.x,robot.y),cases_libres_sauv)
        self.assertNotIn(Libre(robot.x,robot.y),cases_libres)

    def test_retirer_robot(self):
        """ Teste le retrait d'un robot """
        labyrinthe, cases_libres = creer_labyrinthe_depuis_chaine(self.chaine)
        labyrinthe.ajouter_robot(self.num_robot,cases_libres)
        robot = labyrinthe.robot[self.num_robot-1]
        
        labyrinthe.retirer_robot(self.num_robot)
        self.assertEqual(len(labyrinthe.robot),0)
        self.assertIn((robot.x,robot.y),labyrinthe.grille)
        self.assertIsInstance(labyrinthe.grille[robot.x,robot.y],Libre)
        