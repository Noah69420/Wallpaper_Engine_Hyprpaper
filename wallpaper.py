import time
import os
import random
import subprocess
import threading
from pathlib import Path

# Environment variables
path_backgrounds: str = f"{Path.home()}/.config/backgrounds/"
path_config_file: str = f"{Path.home()}/.config/hypr/hyprpaper.conf"
path_hyprconf: str = f"{Path.home()}/.config/hypr/hyprpaper.conf"
FIFO = f"{Path.home()}/.config/hypr/tools/wallpaper/wallpaper_fifo"
sleep_time: int = 300           # 300s =    5min
notification_time = 3000        # 3000ms =  3s
notification: bool = True

# Global variables
timer_old: float = 0
prozess = ""
run: bool = True
subprocess_alive: bool = False

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
    with open(path_config_file, "w") as config_file:
        config_file.write(f"preload = {path_backgrounds}{wallpaper_path}\n")
        config_file.write(f"wallpaper = ,{path_backgrounds}{wallpaper_path}\n")



def restart_hyprpaper():
    global subprocess_alive, prozess
    if subprocess_alive or not run:
        prozess.kill()
        prozess.wait()
        subprocess_alive = False

    if not subprocess_alive and run:
        prozess = subprocess.Popen(["hyprpaper"])
        subprocess_alive = True


def zufall(wallpapers):
    bild = random.choices(wallpapers)[0]
    return bild


def change_wallpaper(wallpaper_old):
    wallpapers = os.listdir(path_backgrounds)
    print(f"\nwallpaper_old: {wallpaper_old}\n")
    wallpaper_new = zufall(wallpapers)
    while wallpaper_old == wallpaper_new:
        wallpaper_new = zufall(wallpapers)
        print(f"wallpaper_new: {wallpaper_new}\n")

    wallpaper_old = wallpaper_new
    update_hyprpaper_config(wallpaper_new)
    restart_hyprpaper()
    return wallpaper_old


def read_pipe():
    global run, timer_old, freeze, sleep_time

    while run:
        with open(FIFO, "r",  encoding="utf-8") as fifo:
            for line in fifo:
                line = line.removesuffix("\n")
                if line == "kill":
                    run = False
                    push_notification("kill Wallpaper_Engine_Hyprpaper and Hyprpaper :(")
                    print("Stop thread")
                    break

                if "next" == line:
                    timer_old = timer_old - sleep_time
                    push_notification("skip wallpaper")

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
    global run, timer_old

    try:
        os.mkfifo(FIFO)
    except FileExistsError:
        pass

    wallpaper_old = read_file(path_hyprconf)
    wallpaper_old = change_wallpaper(wallpaper_old)

    try:
        threading.Thread(target=read_pipe).start()
        while run:
            timer_now = time.time()

            time.sleep(1)
            if freeze and run:
                continue
            if timer_now <= timer_old + sleep_time and run:
                continue

            wallpaper_old = change_wallpaper(wallpaper_old)
            timer_old = timer_now

        os.remove(FIFO)
    except KeyboardInterrupt:
        run = False
        os.remove(FIFO)


if __name__ == "__main__":
    main()