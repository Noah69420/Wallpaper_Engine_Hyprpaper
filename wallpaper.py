import time
import os
import random
import subprocess
import threading
import configparser

config = configparser.ConfigParser()
config.read_file(open(os.path.expanduser("~/.config/hypr/tools/wallpaper/wallpaper_fifo")))

# Environment variables
path_backgrounds: str = os.path.expanduser(config["WALLPAPER"]["path_wallpaper"])
path_hyprconf: str = os.path.expanduser(config["DEFAULT"]["path_hyprconf"])
FIFO = os.path.expanduser(config["DEFAULT"]["FIFO"])
sleep_time: int = int(config["DEFAULT"]["sleep_time"])          # 300s =    5min
notification_time: int = int(config["DEFAULT"]["notification_time"])  # 3000ms =  3s
notification: bool = bool(config["DEFAULT"]["notification"])

# Global variables
timer_old: float = 0
prozess = ""
run: bool = True
subprocess_alive: bool = False
wallpaper_change: bool = False

# Modus
freeze: bool = False


def push_notification(msg):
    if notification:
        os.system(f"notify-send -t {notification_time} '{msg}'")


def read_file(file_path):
    with open(file_path, "r") as file:
        for line in file:
            # Nur Zeilen mit '=' beachten
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if key == "preload":
                    return os.path.basename(value)
    return None


def update_hyprpaper_config(wallpaper_path):
    with open(path_hyprconf, "w") as config_file:
        config_file.write(f"preload = {path_backgrounds}{wallpaper_path}\n")
        config_file.write(f"wallpaper = ,{path_backgrounds}{wallpaper_path}\n")


def restart_hyprpaper(timer: float):
    global subprocess_alive, timer_old, prozess
    if timer >= timer_old + sleep_time and subprocess_alive or not run:
        prozess.kill()
        prozess.wait()
        subprocess_alive = False
    if not subprocess_alive and run:
        prozess = subprocess.Popen(["hyprpaper"])
        subprocess_alive = True
        timer_old = timer


def zufall(wallpapers):
    bild = random.choices(wallpapers)[0]
    return bild


def read_pipe():
    global run, timer_old, freeze, sleep_time, wallpaper_change
    while run:
        with open(FIFO, "r",  encoding="utf-8") as fifo:
            for line in fifo:
                line = line.removesuffix("\n")
                if line == "kill":
                    freeze = False
                    wallpaper_change = True
                    run = False
                    push_notification("kill Wallpaper_Engine_Hyprpaper and Hyprpaper :(")
                    print("Stop thread")
                    break
                if "next" == line:
                    timer_old = timer_old - sleep_time
                    push_notification("skip wallpaper")
                    wallpaper_change = True

                if "freeze" == line:
                    if freeze:
                        freeze = False
                        push_notification("un-freeze wallpaper")
                    else:
                        freeze = True
                        push_notification("freeze wallpaper")
                    print("freeze is: ", freeze)

                if "sleep_time" in line:
                    try:
                        sleep_time = int(line.split(" ")[1])
                    except ValueError:
                        print("Value not correct")


def change_wallpaper(bild_alt, bild_neu, timer):
    global timer_old
    wallpapers = os.listdir(path_backgrounds)
    print(f"\nbild_alt: {bild_alt}\n")
    while bild_alt == bild_neu:
        bild_neu = zufall(wallpapers)
        print(f"bild_neu: {bild_neu}\n")

    bild_alt = bild_neu
    update_hyprpaper_config(bild_neu)
    restart_hyprpaper(timer)
    return bild_alt, bild_neu


def main():
    try:
        os.mkfifo(FIFO)
    except FileExistsError:
        pass
    timer = time.time()
    bild_alt = read_file(path_hyprconf)
    wallpapers = os.listdir(path_backgrounds)
    bild_neu = zufall(wallpapers)
    bild_alt, bild_neu = change_wallpaper(bild_alt, bild_neu, timer)

    global run, wallpaper_change
    try:
        threading.Thread(target=read_pipe).start()
        while run:
            timer = time.time()
            print(f"time_now: {timer}")
            print(f"OLD_Timer: {timer_old}")
            if timer >= timer_old + sleep_time:
                wallpaper_change = True
            time.sleep(1)
            if freeze:
                continue
            elif wallpaper_change:
                bild_alt, bild_neu = change_wallpaper(bild_alt, bild_neu, timer)
                wallpaper_change = False
        os.remove(FIFO)
    except KeyboardInterrupt:
        run = False
        os.remove(FIFO)


if __name__ == "__main__":
    main()
