import csv
import fullscreens
from run_level import *


def main():
    fullscore = 0
    pygame.init()

    while True:
        fullscreens.show_start_menu()
        username = fullscreens.get_username()
        for level_num in range(0):
            res = run_level(level_num)
            while res is None:
                res = run_level(level_num)
            fullscore += res
            fullscreens.show_level_completed(level_num, res, fullscore)
        fullscreens.show_game_final(fullscore)

        with open('records.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='"',
                                quoting=csv.QUOTE_MINIMAL)
            writer.writerow([username, str(fullscore)])


if __name__ == '__main__':
    main()