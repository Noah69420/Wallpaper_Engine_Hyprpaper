import subprocess
import argparse
import sys
import os
from pathlib import Path

FIFO = f"{Path.home()}/.config/hypr/tools/wallpaper/wallpaper_fifo"
wallpaper_py = f"{Path.home()}/.config/hypr/tools/wallpaper/wallpaper.py"

notification: bool = True
notification_time = 3000        # 3000ms =  3s

def arg_parser():
    parser = argparse.ArgumentParser(
                prog=sys.argv[0],
                description='Wallpaper switcher for hyprpaper',
                epilog='Text at the bottom of help')

    parser.add_argument('-f', '--freeze', required=False, default=False, action="store_true", help='freeze the Wallpaper (to resume run the command again)')
    parser.add_argument('-n', '--next', required=False, default=False, action="store_true", help='skip to the next Wallpaper')
    parser.add_argument('-k', '--kill', required=False, default=False, action="store_true", help='kill the Wallpaper-script')
    parser.add_argument('-r', '--run', required=False, default=False, action="store_true", help='run the Wallpaper-script')
    return vars(parser.parse_args())


def push_notification(msg):
    if notification:
        os.system(f"notify-send -t {notification_time} '{msg}'")


def get_command(args: dict):
    if args["kill"]:
        return "kill"
    elif args["run"]:
        if os.path.exists(FIFO):
            print("Hyprpaper läuft bereits")
            push_notification("Wallpaper_Engine_Hyprpaper is already running")
            exit(1)
        resume_wallpaper()
        push_notification("run Wallpaper_Engine_Hyprpaper :)")
        exit(0)
    elif args["next"]:
        return "next"
    elif args["freeze"]:
        return "freeze"
    else:
        print("Please specify a valid option. Use -h for help.")
        exit(1)


def resume_wallpaper():
    subprocess.Popen(
        ["python3", wallpaper_py], 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL, 
        preexec_fn=os.setpgrp
    )


def write_command(command):
    try:
        with open(FIFO, "w", encoding="utf-8") as pipe:
            pipe.write(command)
    except Exception as e:
        print(f"Failed to write to FIFO: {e}")
        exit(1)


def main():
    args: dict = arg_parser()
    command: str = get_command(args)
    if not os.path.exists(FIFO):
        print(f"The FIFO file {FIFO} does not exist. Please ensure Wallpaper_Engine_Hyprpaper is running.")
        push_notification("Wallpaper_Engine_Hyprpaper is dead :(")
        exit(1)
    write_command(command)


if __name__ == "__main__":
    main()
