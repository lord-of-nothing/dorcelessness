import fullscreens
from run_level import *


def main():
    fullscore = 0
    pygame.init()

    fullscreens.show_start_menu()
    for level_num in range(2):
        res = run_level(level_num)
        while res is None:
            res = run_level(level_num)
        fullscore += res
        fullscreens.show_level_completed(level_num, res, fullscore)


if __name__ == '__main__':
    main()