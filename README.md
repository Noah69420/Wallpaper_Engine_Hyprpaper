# wallpaper
Automatic wallpaper changer for hyprpaper

To change to the next wallpaper:
```sh
echo "next" >> path/to/wallpaper_fifo
```
To kill the python script:
```sh
echo "kill" >> path/to/wallpaper_fifo
```
