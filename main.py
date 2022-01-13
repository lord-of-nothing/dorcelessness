from run_level import *
import start_menu


def main():
    start_menu.main()
    res = run_level(0)
    while not res:
        res = run_level(0)

    res = run_level(1)
    while not res:
        res = run_level(1)


if __name__ == '__main__':
    main()