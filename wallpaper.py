import time
import os
import random
import subprocess
import threading

pfad = "/home/noah/.config/backgrounds/"
config_file_path = "/home/noah/.config/hypr/hyprpaper.conf"
sleep_time = 10
timer_old = 0
prozess = ""

FIFO = "/home/noah/.config/hypr/tools/wallpaper_fifo"
run = True
subprocess_alive = False


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
    with open(config_file_path, "w") as config_file:
        config_file.write(f"preload = {pfad}{wallpaper_path}\n")
        config_file.write(f"wallpaper = ,{pfad}{wallpaper_path}\n")


def restart_hyprpaper():
    global subprocess_alive, timer_old, prozess
    if time.time() >= timer_old + sleep_time and subprocess_alive:
        prozess.kill()
        prozess.wait()
        subprocess_alive = False
    if not subprocess_alive:
        prozess = subprocess.Popen(["hyprpaper"])
        subprocess_alive = True
        timer_old = time.time()


def zufall(wallpapers):
    bild = random.choices(wallpapers)[0]
    return bild


def read_pipe():
    global run, timer_old
    while run:
        with open(FIFO, "r",  encoding="utf-8") as fifo:
            for line in fifo:
                line = line.removesuffix("\n")
                if line == "kill":
                    run = False
                    print("Stop thread")
                    break
                if "next" == line:
                    timer_old = timer_old - sleep_time


def main():
    try:
        os.mkfifo(FIFO)
    except FileExistsError:
        pass
    bild_alt = read_file(".config/hypr/hyprpaper.conf")
    wallpapers = os.listdir(pfad)
    bild_neu = zufall(wallpapers)
    global run
    global timer_old
    timer_old = time.time()
    try:
        threading.Thread(target=read_pipe).start()
        while run:
            # print("running ...")
            wallpapers = os.listdir(pfad)
            while bild_alt == bild_neu:
                bild_neu = zufall(wallpapers)

            bild_alt = bild_neu
            update_hyprpaper_config(bild_neu)
            restart_hyprpaper()
            time.sleep(2)
        os.remove(FIFO)
    except KeyboardInterrupt:
        run = False
        os.remove(FIFO)


if __name__ == "__main__":
    main()
