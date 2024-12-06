import subprocess
import argparse
import sys
import os
import configparser


def init_conf():
    config = configparser.ConfigParser()
    try:
        config.read_file(open(os.path.expanduser("~/.config/Wallpaper_Engine_Hyprpaper.ini")))
    except FileNotFoundError:
        config["DEFAULT"] = {"FIFO": "~/.config/hypr/tools/wallpaper/wallpaper_fifo",
                             "wallpaper_py": "~/.config/hypr/tools/wallpaper/wallpaper.py",
                             "notification": "True",
                             "notification_time": "3000",
                             "sleep_time": "300",
                             "path_hyprconf": "~/.config/hypr/hyprpaper.conf"}
        config["WALLPAPER"] = {"path_wallpapers": "~/.config/backgrounds/"}
        with open(os.path.expanduser("~/.config/Wallpaper_Engine_Hyprpaper.ini"), 'w') as configfile:
            config.write(configfile)

    return config


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


def push_notification(msg, config):
    if config["DEFAULT"]["notification"]:
        os.system(f"notify-send -t {config["DEFAULT"]["notification_time"]} '{msg}'")


def get_command(args: dict, config):
    if args["kill"]:
        return "kill"
    elif args["run"]:
        if os.path.exists(config["DEFAULT"]["FIFO"]):
            print("Hyprpaper läuft bereits")
            push_notification("Wallpaper_Engine_Hyprpaper is already running", config)
            exit(1)
        resume_wallpaper(config["DEFAULT"]["wallpaper_py"])
        push_notification("run Wallpaper_Engine_Hyprpaper :)", config)
        exit(0)
    elif args["next"]:
        return "next"
    elif args["freeze"]:
        return "freeze"
    else:
        print("Please specify a valid option. Use -h for help.")
        exit(1)


def resume_wallpaper(wallpaper_py: str):
    subprocess.Popen(
        ["python3", wallpaper_py],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setpgrp
    )


def write_command(command, FIFO: str):
    try:
        with open(os.path.expanduser(FIFO), "w", encoding="utf-8") as pipe:
            pipe.write(command)
    except Exception as e:
        print(f"Failed to write to FIFO: {e}")
        exit(1)


def main():
    config = init_conf()
    args: dict = arg_parser()
    command: str = get_command(args, config)
    if not os.path.exists(config["DEFAULT"]["FIFO"]):
        print(f"The FIFO file {config["DEFAULT"]["FIFO"]} does not exist. Please ensure Wallpaper_Engine_Hyprpaper is running.")
        push_notification("Wallpaper_Engine_Hyprpaper is dead :(", config)
        exit(1)
    write_command(command, config["DEFAULT"]["FIFO"])


if __name__ == "__main__":
    main()
