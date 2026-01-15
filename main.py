import pygame
import pygame_manager as pm


class Main:
    def __init__(self):
        pm.init()
        self.closed = False
        self.opened = False

    def update(self):
        print(pygame.time.get_ticks())
        if pygame.time.get_ticks() >= 5000 and not self.closed:
            pm.screen.close()
            self.closed = True
        if pygame.time.get_ticks() >= 10000 and not self.opened:
            pm.screen.create()
            self.opened = True

if __name__ == '__main__':
    main = Main()
    pm.run(main.update)
