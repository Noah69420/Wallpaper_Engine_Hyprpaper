import argparse
import sys
import os
from pathlib import Path

FIFO = f"{Path.home()}/.config/hypr/tools/wallpaper_fifo"


def arg_parser():
    parser = argparse.ArgumentParser(
                prog=sys.argv[0],
                description='Wallpaper switcher for hyprpaper',
                epilog='Text at the bottom of help')

    parser.add_argument('-f', '--freeze', required=False, default=False, action="store_true", help='freeze the Wallpaper (to resume run the command again)')
    parser.add_argument('-n', '--next', required=False, default=False, action="store_true", help='skip to the next Wallpaper')
    parser.add_argument('-k', '--kill', required=False, default=False, action="store_true", help='kill the Wallpaper-script')
    return vars(parser.parse_args())


def get_command(args: dict):
    if args["kill"]:
        return "kill"
    elif args["next"]:
        return "next"
    elif args["frezze"]:
        return "frezze"
    else:
        exit(0)


def write_command(command):
    with open(FIFO, "w", encoding="utf-8") as pipe:
        pipe.write(command)


def main():
    if not os.path.isfile(FIFO):
        print("Wallpaper_Engine_Hyprpaper is not running!")
        args: dict = arg_parser()
        command: str = get_command(args)
        write_command(command)


if __name__ == "__main__":
    main()
