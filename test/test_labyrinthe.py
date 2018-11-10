import unittest
from labyrinthe.labyrinthe import Labyrinthe, creer_labyrinthe_depuis_chaine
#from labyrinthe import labyrinthe

from labyrinthe.obstacle.mur import Mur
from labyrinthe.obstacle.porte import Porte
from labyrinthe.obstacle.sortie import Sortie
from labyrinthe.obstacle.libre import Libre
from labyrinthe.robot import Robot
import random

class LabyrintheTest(unittest.TestCase):

    """Test case utilisé pour tester les fonctions du module 'labyrinthe'."""
    def setUp(self):
        """Initialisation des tests."""
        self.num_robot = 0
        self.chaine = "OOOOOOOOOO\nO . O.O  O\nO      O O\nO . O OO O\nOOOOOOOOOO\n"
    
    def test_creer_labyrinthe_depuis_chaine(self):
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
        #cases_libres = [Libre(2,1,' '),Libre(2,2,' ')]
        cases_libres = []
        labyrinthe, cases_libres = creer_labyrinthe_depuis_chaine(self.chaine)
        cases_libres_sauv = list(cases_libres)
        self.assertIsNone(labyrinthe.robot)
        labyrinthe.ajouter_robot(self.num_robot,cases_libres)
        # On vérifie qu'un robot a bien été créé et ajouté à la liste
        self.assertIsNotNone(labyrinthe.robot)
        self.assertIsInstance(labyrinthe.robot[self.num_robot], Robot)
        # On vérifie que le robot a bien été choisi parmi les cases libres
        robot = labyrinthe.robot[self.num_robot]
        #libre = Libre(robot.x,robot.y)
        self.assertIn(Libre(robot.x,robot.y),cases_libres_sauv)
        self.assertNotIn(Libre(robot.x,robot.y),cases_libres)


