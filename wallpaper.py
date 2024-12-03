import time
import os
import random
import subprocess
import threading
from pathlib import Path

path_backgrounds: str = f"{Path.home()}/.config/backgrounds/"
print(f"--------------------------{path_backgrounds}")
path_config_file: str = f"{Path.home()}/.config/hypr/hyprpaper.conf"
path_hyprconf: str = f"{Path.home()}/.config/hypr/hyprpaper.conf"
sleep_time: int = 300
timer_old: float = 0
prozess = ""

FIFO = f"{Path.home()}/.config/hypr/tools/wallpaper/wallpaper_fifo"

run = True
subprocess_alive = False

run: bool = True
subprocess_alive: bool = False

# Modus
freeze: bool = False


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


def restart_hyprpaper(timer: float):
    global subprocess_alive, timer_old, prozess
    if timer >= timer_old + sleep_time and subprocess_alive:
        prozess.kill()
        prozess.wait()
        subprocess_alive = False
    if not subprocess_alive:
        prozess = subprocess.Popen(["hyprpaper"])
        subprocess_alive = True
        timer_old = timer


def zufall(wallpapers):
    bild = random.choices(wallpapers)[0]
    return bild


def read_pipe():
    global run, timer_old, freeze, sleep_time
    while run:
        with open(FIFO, "r",  encoding="utf-8") as fifo:
            for line in fifo:
                line = line.removesuffix("\n")
                if line == "kill":
                    freeze = False
                    run = False
                    print("Stop thread")
                    break
                if "next" == line:
                    timer_old = timer_old - sleep_time

                if "freeze" == line:
                    if freeze:
                        freeze = False
                    else:
                        freeze = True
                    print("freeze is: ",freeze)

                if "sleep_time" in line:
                    try:
                        sleep_time = int(line.split(" ")[1])
                    except ValueError:
                        print("Value not correct")


def main():
    try:
        os.mkfifo(FIFO)
    except FileExistsError:
        pass
    bild_alt = read_file(path_hyprconf)
    wallpapers = os.listdir(path_backgrounds)
    bild_neu = zufall(wallpapers)
    global run
    global timer_old
    try:
        threading.Thread(target=read_pipe).start()
        while run:
            timer = time.time()
            time.sleep(2)
            if freeze:
                continue
            wallpapers = os.listdir(path_backgrounds)
            while bild_alt == bild_neu:
                bild_neu = zufall(wallpapers)

            bild_alt = bild_neu
            update_hyprpaper_config(bild_neu)
            restart_hyprpaper(timer)
        os.remove(FIFO)
    except KeyboardInterrupt:
        run = False
        os.remove(FIFO)


if __name__ == "__main__":
    main()
