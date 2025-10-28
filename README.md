# TP Casse-Brique - Projet TP 4, 5 et 6

**Développé par :** Elise MUSTO et Stéfania NOUBOUA  
**Année :** 2025  
**Technologies :** Python - Tkinter  
**Encodage :** UTF-8

### Répertoire GITHUB
[GITHUB](https://github.com/444stef/TP-Casse-brique)

## Description du Projet

Un jeu de **casse-brique classique** développé en Python utilisant la bibliothèque **Tkinter** pour l'interface graphique. Le joueur contrôle une raquette pour faire rebondir une balle et détruire toutes les briques.




## Objectif du Jeu


 - **Détruire** toutes les briques avec la balle 
 - **Maximiser** votre score (perdre le - de vie possible)
 - **Survivre** le plus longtemps possible 


## Contrôles du Jeu
| Commande | Action |
|----------|--------|
| Touche Flèche Gauche | Déplacement de la raquette vers la gauche |
| Touche Flèche Droite | Déplacement de la raquette vers la droite |
| Bouton START NEW  | Lancement d'une nouvelle partie |
| Bouton LAST GAME | Reprendre la dernière partie sauvegardée |
| Bouton QUIT | Fermeture de l'application |
| Bouton PAUSE/RESUME | Mettre en pause/reprendre le jeu |
| Bouton RECENT SCORES| Affichier l'historique des scores |

## Système de Vies & Score

### Vies
- **3 vies initiales** représentées par des cœurs : ❤️ ❤️ ❤️
- **Perte d'une vie** quand la balle touche le sol 
- **Défaite** quand toutes les vies sont perdues
- **Historique des scores** se sauvagarde dans un ficher json (scores.json)

### Score
- **+1 point** par brique détruite 
- **Affichage en temps réel** du score actuel
- **Historique des scores** 


## Spécificités de l'implémentation
 **Class** : 
- **Game** : Gestion globale du jeu(boucle principale, interface Tkinter, gestion des événements (victoire, défaite, sauvegarde), clavier et boutons)
- **Paddle** : Gère la raquette avec ses mouvements, les vitesses, collisions avec la balle
- **Ball** : Gère la balle : déplacement de la ball, les rebonds sur les murs et la raquette (Loi de Descartes)
- **Brick** : Crée une brique 
- **BrickManager** : Crée l'ensemble des briques (crée la grille), détruit la brique touchée, détecte collisions balle-brique


## Structures des données utilisées 
- **Liste** : Stocke l'ensemble des briques
- **File** : sert à conserver les 5 derniers scores uniquement (le premier score ajouté et le premier supprimé)
- **Pile** : sert à gérer les vies (le dernier coeur ajouté est le premier retiré)


## Structure du fichier
TP-Casse-brique/  
├── .gitignore  
├──final_version.py # Script principal du jeu     
└── README.md # Documentation du projet


  


