"""
Jeu Casse-Brique

Fonctionnalités :
- Interface Tkinter : Canvas, score, vies, menu, boutons (Start new, Last game, Pause/Resume, Recent Scores, Quit)
- Classes: Game, Paddle, Ball, Brick, BrickManager
- Raquette contrôlée par flèches gauche/droite
- Balle se déplace automatiquement avec des rebonds suivant la loi de Descartes, collisions avec murs/raquette/briques
- Plusieurs rangées de briques, destruction + score
- mise en pause/reprise du jeu
- sauvegarde automatique du jeu par pression du bouton quit si la partie n'est pas achevée
- choix de reprendre la partie (ou non) par l'utilisateur
- affichage disponible des 5 derniers scores
- Vies (par défaut 3), affichage, fin de partie (victoire / game over)

Coding: UTF-8

Auteurs: Stefania NOUBOUA - Elise MUSTO
"""

import tkinter as tk
import math
from typing import List
from collections import deque 
import json
import os

C_WIDTH = 800
C_HEIGHT = 600
P_WIDTH = 120
P_HEIGHT = 16
OFFSET = 40
RADIUS = 5
INIT_BALL_SPEED = 5.0
ROWS = 6
COLS = 10
B_WIDTH = C_WIDTH // COLS
B_HEIGHT = 22
LIVES = 3
FPS = 110


class Paddle:
    """
    Classe représentant la raquette du joueur.
    Cette classe gère :
      - sa position et sa vitesse horizontale,
      - le dessin graphique sur le canevas,
      - le déplacement limité aux bords du canevas.
    """
    def __init__(self, canvas):
        """
        -initialise la raquette au centre en bas du canevas.
        """
        self.canvas = canvas
        self.width = P_WIDTH
        self.height = P_HEIGHT
        self.x = C_WIDTH // 2
        self.y = C_HEIGHT - OFFSET
        self.vel = 0
        self.max_speed = 10
        self.id = self.canvas.create_rectangle(0, 0, 1, 1, fill='blue')
        self.draw()

    def draw(self):
        """
        - met à jour la position graphique de la raquette sur le canevas.
        - la raquette est centrée autour de (self.x, self.y).
        """
        #Calcule les coordonnées du coin supérieur gauche du rectangle
        x1 = self.x - self.width // 2
        y1 = self.y - self.height // 2

        #Calcule les coordonnées du coin inférieur droit du rectangle
        x2 = self.x + self.width // 2
        y2 = self.y + self.height // 2

        self.canvas.coords(self.id, x1, y1, x2, y2)

    def move(self):
        """
        - déplace la raquette selon sa vitesse actuelle.
        - si elle touche un bord, on la bloque (elle ne sort pas de la zone de jeu).
        """
        #Nouvelle position calculée
        new_x = self.x + self.vel
        half = self.width // 2
        #Empêche la raquette de dépasser le bord gauche
        if new_x - half < 0:
            new_x = half
        #Empêche la raquette de dépasser le bord droit
        if new_x + half > C_WIDTH:
            new_x = C_WIDTH - half

        self.x = new_x
        self.draw()

    def set_speed(self, v):
        """
        - définit la vitesse de la raquette.
        - utilisée lorsqu'on appuie ou relâche les flèches du clavier.
        - param v: vitesse souhaitée (positive = droite, négative = gauche)
        """
        self.vel = v

class Brick:
    """
    Brique unique définie par:
    - position
    - taille
    - couleur
    """
    def __init__(self, canvas, x, y, w, h, color, value):
        self.canvas = canvas

        #coin supérieur gauche
        self.x = x  
        self.y = y
        #coin inférieur droit
        self.w = w
        self.h = h

        self.color = color
        self.value = value #nombre de points que sa destruction
        self.alive = True
        self.id = self.canvas.create_rectangle(x, y, x + w, y + h, fill=color, outline='black')

    def destroy(self):
        """détruit la brique si elle est encore en vie"""
        if self.alive:
            self.alive = False
            self.canvas.delete(self.id)

class BricksManager:
    """
    - crée la grille de briques
    - détecte collisions balle-brique
    - détruit la brique touchée
    - renvoie True si une brique a été touchée
    """
    def __init__(self, canvas):
        self.canvas = canvas
        self.bricks: List[Brick] = []
        self.create_bricks()

    def create_bricks(self):
        """
        crée le tableau de briques en haut de la fenêtre de jeu
        """

        top_offset = 60  # laisse de la place pour score/vies
        for row in range(ROWS):
            for col in range(COLS):
                x = col * B_WIDTH
                y = row * B_HEIGHT + top_offset
                brick = Brick(self.canvas, x, y, B_WIDTH, B_HEIGHT, color='#9b59b6', value=1)
                self.bricks.append(brick)

    
    def collision(self, ball: 'Ball'):
        """
        - vérifie si collision entre la balle et une des briques.
        - retourne la brique touchée et la détruit, ou None si aucune.
        """
        ball_left = ball.x - ball.radius
        ball_right = ball.x + ball.radius
        ball_top = ball.y - ball.radius
        ball_bottom = ball.y + ball.radius

        for brick in self.bricks:
            if not brick.alive:
                continue

            #Les variables brick_left/right/top/bottom sont les bornes de la brique.
            brick_left = brick.x
            brick_right = brick.x + brick.w
            brick_top = brick.y
            brick_bottom = brick.y + brick.h

            # Vérifie s'il y a chevauchement entre la balle (approximée en carré) et la brique (se chevauchent à la fois sur l'axe x et l'axe y)
            if (ball_right >= brick_left and ball_left <= brick_right and
                ball_bottom >= brick_top and ball_top <= brick_bottom):
                
                #calculer la distance entre les côtés de la balle et de la brique susceptibles de se toucher. La plus petite distance indique quel côté de la brique est touché.
                hit_left = ball_right - brick_left
                hit_right = brick_right - ball_left
                hit_top = ball_bottom - brick_top
                hit_bottom = brick_bottom - ball_top
                min_hit = min(hit_left, hit_right, hit_top, hit_bottom)

                if min_hit == hit_left or min_hit == hit_right:
                    #contact latéral. on inverse la composante selon x.
                    ball.vx = -ball.vx
                else:
                    #contact vertical. on inverse la composante selon y.
                    ball.vy = -ball.vy

                brick.destroy()

                #permet d'actualiser le score en indiquant à la classe Game la valeur de la brique qui vient d'être détruite (hit_brick)
                return brick
        return None

    def count(self):
        """Nombre de briques encore présentes."""
        return sum(1 for b in self.bricks if b.alive)

class Ball:
    """
    - crée la balle sur le canevas Tkinter
    - gère son mouvement (mettre à jour sa position à chaque frame)
    - rebonds sur les murs et la raquette (loi de Descartes)
    """
    def __init__(self, canvas, paddle, radius=RADIUS, color='white', speed=INIT_BALL_SPEED):
        self.canvas = canvas
        self.paddle = paddle
        self.radius = radius
        self.color = color
        self.speed = speed

        #vitesses horizontales et verticales initiales (arbitraire. la trajectoire est ici une diagonale)
        self.vx = speed
        self.vy = -speed

        #création de la balle sur le canevas
        self.id = self.canvas.create_oval(0, 0, 0, 0, fill=color, outline=color)

        #Position et vitesse initiales
        self.set_reset()

    def update(self):
        """Déplace la balle et met à jour sa position sur le canevas."""
        self.x += self.vx
        self.y += self.vy


    def set_reset(self):
        """Place la balle au centre de la raquette et initialise la vitesse."""
        self.x = self.paddle.x
        self.y = self.paddle.y - self.paddle.height // 2 - self.radius
        self.vx = self.speed / math.sqrt(2)
        self.vy = -self.speed / math.sqrt(2)
        self.canvas.coords(self.id, self.x-self.radius, self.y-self.radius, self.x+self.radius, self.y+self.radius)
    
    def handle_collisions(self, brick_manager):
        """
        Gestion des collisions:
        - murs: inversion vx ou vy
        - briques: inversion vx ou vy selon l'axe du contact
        - raquette: inversion de vy
        - paramètres: brick_manager
        """
        #Murs
        if self.x - self.radius <= 0:  #mur gauche
            self.x = self.radius
            self.vx = -self.vx
        elif self.x + self.radius >= C_WIDTH:  #mur droit
            self.x = C_WIDTH - self.radius
            self.vx = -self.vx

        if self.y - self.radius <= 0:  #plafond
            self.y = self.radius
            self.vy = -self.vy

        #Brique
        
        hit_brick = brick_manager.collision(self)

        #Raquette
        px1 = self.paddle.x - self.paddle.width / 2
        px2 = self.paddle.x + self.paddle.width / 2
        py1 = self.paddle.y - self.paddle.height / 2
        py2 = self.paddle.y + self.paddle.height / 2

        if (px1 <= self.x <= px2) and (py1 <= self.y + self.radius <= py2) and self.vy > 0:
            self.y = py1 - self.radius
            self.vy = -self.vy 

        #mise à jour sur le canevas
        self.canvas.coords(self.id, self.x - self.radius, self.y - self.radius, self.x + self.radius, self.y + self.radius)

        return hit_brick
    

class Game:
    """
    Classe principale du jeu:
    - Création et gestion de l'interface Tkinter (fenêtre, canvas, boutons (=QUIT, START NEW...))
    - Création de l'état du jeu (score, vie)
    - Met à jour les élements du jeu : balle, raquette, brique, score et vies
    - Gestion des déplacements de la raquette par le clavier
    - Sauvegarde et restauration des parties (save.json) et gère l'historique des scores (historique.json)
    """
    def __init__(self):
        #charge l'historique (liste) stocké dans historique.json. Si inexistant, on crée une liste vide
        loaded = []
        if os.path.exists("historique.json"):
            with open("historique.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                loaded = data

        #implémentation d'une file deque pour garder automatiquement seulement les 5 derniers scores
        self.historique = deque(loaded, maxlen=5)

        self.window = tk.Tk()
        self.window.title("Casse-Brique")

        self.canvas = tk.Canvas( self.window, width=C_WIDTH, height=C_HEIGHT, bg='black')
        self.canvas.pack()

        #score et vies
        self.score = 0
        self.lives = LIVES
        self.score_text = self.canvas.create_text(10, 10, anchor='nw', fill='white', font=('Arial', 16), text=f"Score: {self.score}")
        self.life_icons = []

        #raquette, balle, briques
        self.paddle = Paddle(self.canvas)
        self.ball = Ball(self.canvas, self.paddle)
        self.bricks = BricksManager(self.canvas)

        #menu

        self.menu_text = self.canvas.create_text(C_WIDTH//2, C_HEIGHT//2, text="Casse-Brique\nChoisissez une option pour jouer pour jouer",
                                                 fill="white", font=('Arial', 24), justify='center')
        
        #boutons
        self.start_btn = tk.Button(self.window, text=" ▶ START NEW", command=self.start, bg = '#BBDDF2', fg = 'darkgreen', font=('Arial',12, 'bold'), relief='raised')
        self.start_btn.pack(side='left')

        self.quit_btn = tk.Button(self.window, text=" ✖ QUIT", command=self.quitter, bg = '#BBDDF2', fg = 'darkred', font=('Arial',12, 'bold'), relief='raised')
        self.quit_btn.pack(side='right')

        self.continue_btn = tk.Button(self.window, text="LAST GAME", command=self.continue_game, bg = '#BBDDF2', fg = "#391369", font=('Arial',12, 'bold'), relief='raised')
        self.continue_btn.pack(side='left', padx=20, pady=10)

        self.pause_btn = tk.Button(self.window, text="⏸️ PAUSE", command=self.press_pause, bg='grey', fg='white', font=('Arial', 12, 'bold'), relief='raised')
        self.pause_btn.pack(side='left')

        self.memory_btn = tk.Button(self.window, text="RECENT SCORES", command=self.show_last_scores, bg='#BBDDF2', fg="#8C0544", font=('Arial', 12, 'bold'), relief='raised')

        self.running = False
        self.paused = False

        #commandes
        self.window.bind("<Left>", self.on_left_press)
        self.window.bind("<Right>", self.on_right_press)
        self.window.bind("<KeyRelease-Left>", self.on_left_release)
        self.window.bind("<KeyRelease-Right>", self.on_right_release)


    #vies avec coeurs
    def update_lives_display(self):
        heart = self.life_icons.pop()   
        self.canvas.delete(heart)
        self.canvas.update_idletasks()  

    #touches
    def on_left_press(self, event): 
        self.paddle.set_speed(-self.paddle.max_speed)
    def on_right_press(self, event): 
        self.paddle.set_speed(self.paddle.max_speed)
    def on_left_release(self, event): 
        if self.paddle.vel < 0: 
            self.paddle.set_speed(0)
    def on_right_release(self, event):
        if self.paddle.vel > 0: 
            self.paddle.set_speed(0)

    def start(self):
        """initialisation et lancement du jeu"""
        self.running = True
        self.canvas.delete(self.menu_text)
        self.start_btn.pack_forget()
        self.continue_btn.pack_forget()
        #initialise le nombre de vies
        for i in range(self.lives):
            heart = self.canvas.create_text(C_WIDTH - 20 - i*20, 10, anchor='ne', fill='#fd3f92', font=('Arial', 16), text='❤')
            self.life_icons.append(heart)   #implémentation d'une pile

        self.update()

    def new_game(self):
        """Commence une nouvelle partie en supprimant la sauvegarde existante."""
        if os.path.exists("save.json"):
            os.remove("save.json")
        self.ball.set_reset()
        self.start()

    def continue_game(self):
        """Continue la partie sauvegardée (si elle existe)."""
        if os.path.exists("save.json"):
            print("Partie reprise.")
            self.load_state()
            self.start()
        else:
            print("Pas de sauvegarde à charger.")
            self.new_game()

    def press_pause(self):
        """run/stop du jeu et change le nom du bouton en fonction"""
        if self.running:
            self.paused, self.running = not self.paused, not self.running
            self.pause_btn.config(text="RESUME")
        else:
            self.paused, self.running = not self.paused, not self.running
            self.pause_btn.config(text="PAUSE")
            self.update()

    def end_game(self):
        """
        - arrête le jeu en cas de victoire/défaite
        - met à jour l'historique des scores
        - efface la dernière sauvegarde car partie achevée
        """
        self.running = False

        self.memory_btn.pack(side='left')
        self.pause_btn.pack_forget()

        self.historique.append(str(self.score))

        # sauvegarde de l'historique en JSON (liste)

        with open("historique.json", 'w', encoding='utf-8') as f:
            # convertir la file deque en liste pour json
            json.dump(list(self.historique), f, ensure_ascii=False)

        if os.path.exists("save.json"):
            os.remove("save.json")

    def show_last_scores(self):
        """Ouvre une petite fenêtre affichant l'historique des scores."""
        self.memory_btn.pack_forget()
        # nouvelle petite fenêtre
        small_window = tk.Toplevel(self.window)
        small_window.title("Historique des 5 derniers scores")
        # taille et position relative à la fenêtre principale
        x = self.window.winfo_x() + 50
        y = self.window.winfo_y() + 50
        small_window.geometry(f"300x240+{x}+{y}")

        # zone de texte non éditable pour afficher l'historique
        text = tk.Text(small_window, wrap='word', height=10, width=36)
        text.pack(fill='both', expand=True, padx=10, pady=(10, 5))

        # afficher l'historique (du plus ancien au plus récent)
        if self.historique:
            lines = list(self.historique)
            #une ligne pour chaque score
            text.insert('end', "\n".join(lines))
        else:
            text.insert('end', "Aucun score enregistré.")
    
        # rendre la zone non-editable
        text.config(state='disabled')

        # met un focus sur la fenêtre (sans bloquer la principale)
        small_window.transient(self.window)
        small_window.focus_force()


    def update(self):
        if not self.running:
            return
        self.paddle.move()
        self.ball.update()
        hit_brick = self.ball.handle_collisions(self.bricks)
        if hit_brick:
            self.score += hit_brick.value
            self.canvas.itemconfigure(self.score_text, text=f"Score: {self.score}")

        #si balle tombée
        if self.ball.y - self.ball.radius > C_HEIGHT:
            self.lives -= 1
            self.update_lives_display()
            if self.lives > 0:
                self.ball.set_reset()
            else:
                self.end_game()
                self.canvas.create_text(C_WIDTH//2, C_HEIGHT//2, text="GAME OVER", fill="red", font=('Arial', 36))

        #victoire
        elif self.bricks.count() == 0:
            self.end_game()
            self.canvas.create_text(C_WIDTH//2, C_HEIGHT//2, text="VICTOIRE!", fill="green",
                                    font=('Arial', 36))

        if self.running:
            self.window.after(int(1000/FPS) #délai en milisecondes
                              , self.update)
            
    def quitter(self):
        """
        - sauvegarde automatique du jeu si la partie n'est pas finie
        - fermeture de la fenêtre
        """
        if self.running or self.paused==True:
            self.save_state()
        self.window.destroy()

    def save_state(self):
        """Sauvegarde l'état actuel du jeu dans un fichier JSON."""
        state = {
            "score": self.score,
            "lives": self.lives,
            "paddle": {"x": self.paddle.x},
            "ball": {
                "x": self.ball.x,
                "y": self.ball.y,
                "vx": self.ball.vx,
                "vy": self.ball.vy

            },
            "bricks": [b.alive for b in self.bricks.bricks]
        }

        with open("save.json", "w") as f:
            json.dump(state, f)
        print("Sauvegarde effectuée.")

    def load_state(self):
        """Charge une sauvegarde si elle existe."""
        with open("save.json", "r") as f:
            state = json.load(f)

        self.score = state["score"]
        self.lives = state["lives"]
        self.canvas.itemconfigure(self.score_text, text=f"Score: {self.score}")

        self.paddle.x = state["paddle"]["x"]
        self.paddle.draw()

        self.ball.x = state["ball"]["x"]
        self.ball.y = state["ball"]["y"]
        self.ball.vx = state["ball"]["vx"]
        self.ball.vy = state["ball"]["vy"]
        self.canvas.coords(self.ball.id, self.ball.x - self.ball.radius, self.ball.y - self.ball.radius,
                            self.ball.x + self.ball.radius, self.ball.y + self.ball.radius)
        
        # Restaure les briques
        for b, alive in zip(self.bricks.bricks, state["bricks"]):
            if not alive:
                b.destroy()

        print("Sauvegarde chargée avec succès.")

    def run(self):
        self.window.mainloop()



#lancer le jeu
if __name__ == "__main__":
    game = Game()
    game.run()