import sys
import zlevel
import start_menu


def main():
    start_menu.main()
    res = zlevel.main()
    while not res:
        res = zlevel.main()


if __name__ == '__main__':
    main()