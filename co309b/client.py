import pygame
from network import Network
import pickle
pygame.font.init()
pygame.mixer.init()  # Initialize the mixer for music

# Window settings
width = 630
height = 600
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Client")

# Load and play background music
pygame.mixer.music.load("background_music.mp3")  # Replace with your music file
pygame.mixer.music.set_volume(0.5)  # Adjust volume (0.0 to 1.0)
pygame.mixer.music.play(-1)  # Play music in a loop

# Button class remains the same
class Button:
    def __init__(self, text, x, y, color):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.width = 150
        self.height = 150

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        font = pygame.font.SysFont("comicsans", 40)
        text = font.render(self.text, 1, (255, 255, 255))
        win.blit(
            text,
            (
                self.x + round(self.width / 2) - round(text.get_width() / 2),
                self.y + round(self.height / 2) - round(text.get_height() / 2),
            ),
        )

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        return False

# The rest of your code remains unchanged...

# Redraw window function with score tracking
def redrawWindow(win, game, p, scores):
    win.fill((128, 128, 128))

    if not game.connected():
        font = pygame.font.SysFont("comicsans", 50)
        text = font.render("Waiting for Player", 1, (255, 0, 0), True)
        win.blit(text, (width / 2 - text.get_width() / 2, height / 2 - text.get_height() / 2))
    else:
        # Display scores
        font = pygame.font.SysFont("comicsans", 40)
        score_text = f"Player 1: {scores[0]}  |  Player 2: {scores[1]}"
        text = font.render(score_text, 1, (0, 255, 0))
        win.blit(text, (width / 2 - text.get_width() / 2, 50))

        font = pygame.font.SysFont("comicsans", 40)
        s_text = f"Your Move"
        text = font.render(s_text, 1, (0, 255, 255))
        win.blit(text, (50, 280))

        s_text = f"Opponent's Move"
        text = font.render(s_text, 1, (0, 255, 255))
        win.blit(text, (300, 280))

        move1 = game.get_player_move(0)
        move2 = game.get_player_move(1)
        if game.bothWent():
            text1 = font.render(move1, 1, (0, 0, 0))
            text2 = font.render(move2, 1, (0, 0, 0))
        else:
            if game.p1Went and p == 0:
                text1 = font.render(move1, 1, (0, 0, 0))
            elif game.p1Went:
                text1 = font.render("Locked In", 1, (0, 0, 0))
            else:
                text1 = font.render("Waiting...", 1, (0, 0, 0))

            if game.p2Went and p == 1:
                text2 = font.render(move2, 1, (0, 0, 0))
            elif game.p2Went:
                text2 = font.render("Locked In", 1, (0, 0, 0))
            else:
                text2 = font.render("Waiting...", 1, (0, 0, 0))

        if p == 1:
            win.blit(text2, (65, 350))
            win.blit(text1, (375, 350))
        else:
            win.blit(text1, (65, 350))
            win.blit(text2, (375, 350))

        for btn in btns:
            btn.draw(win)
    pygame.display.update()


btns = [
    Button("Rock", 50, 450, (0, 0, 0)),
    Button("Scissors", 250, 450, (255, 0, 0)),
    Button("Paper", 450, 450, (0, 255, 0)),
]

# Main function with score tracking

# Main function with score tracking and series reset
def main():
    run = True
    clock = pygame.time.Clock()
    n = Network()
    player = int(n.getP())
    print("You are player", player)

    scores = [0, 0]  # Track scores for both players

    while run:
        clock.tick(60)
        try:
            game = n.send("get")
        except:
            run = False
            print("Couldn't get game")
            break

        if game.bothWent():
            redrawWindow(window, game, player, scores)
            pygame.time.delay(200)
            try:
                game = n.send("reset")
            except:
                run = False
                print("Couldn't get game")
                break

            # Update scores
            if (game.winner() == 1 and player == 1) or (game.winner() == 0 and player == 0):
                scores[player] += 1
            elif game.winner() != -1:
                scores[1 - player] += 1

            # Check if any player has won the series
            if scores[player] == 5 or scores[1 - player] == 5:
                series_winner = "You" if scores[player] == 5 else "Opponent"
                font = pygame.font.SysFont("comicsans", 30)
                text = font.render(f"{series_winner} Won the Series!", 1, (255, 0, 0))
                window.blit(text, (width / 2 - text.get_width() / 2, 170))
                pygame.display.update()
                pygame.time.delay(3000)

                # Reset scores
                scores = [0, 0]

            font = pygame.font.SysFont("comicsans", 90)
            if (game.winner() == 1 and player == 1) or (game.winner() == 0 and player == 0):
                text = font.render("You Won!", 1, (255, 0, 0))
            elif game.winner() == -1:
                text = font.render("Tie Game!", 1, (255, 0, 0))
            else:
                text = font.render("You Lost...", 1, (255, 0, 0))

            window.blit(text, (width / 2 - text.get_width() / 2, 170))
            pygame.display.update()
            pygame.time.delay(2000)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for btn in btns:
                    if btn.click(pos) and game.connected():
                        if player == 0:
                            if not game.p1Went:
                                n.send(btn.text)
                        else:
                            if not game.p2Went:
                                n.send(btn.text)
        redrawWindow(window, game, player, scores)
        
# Menu screen with instructions and music
def menu_screen():
    run = True
    clock = pygame.time.Clock()
    exit_button = Button("Exit", width // 2 - 75, height // 2 + 100, (255, 0, 0))  # Exit button

    while run:
        clock.tick(60)
        window.fill((128, 128, 128))
        font = pygame.font.SysFont("comicsans", 60)
        text = font.render("Click to Play!", 1, (255, 0, 0))
        instructions = pygame.font.SysFont("comicsans", 25).render(
            "Instructions: Choose Rock, Paper, or Scissors.", 1, (0, 0, 0)
        )

        window.blit(text, (width / 2 - text.get_width() / 2, height / 3))
        window.blit(instructions, (width / 2 - instructions.get_width() / 2, height / 2))

        # Draw the Exit button
        exit_button.draw(window)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
                return  # Exit the function
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if exit_button.click(pos):
                    pygame.quit()
                    run = False
                    return  # Exit the function
                else:
                    run = False  # Start the game
    main()

while True:
    menu_screen()
