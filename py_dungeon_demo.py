import math
from tkinter import Tk, Canvas, Button
from py_dungeon_generator import DungeonGenerator, MapPartition

def draw_tile(canvas: Canvas, x: int, y: int, color: str = "#ffffff", tile_size: tuple = (16, 16)):
    width, height = tile_size
    x1, y1, x2, y2 = (x * width, y * height, (x * width) + width, (y * height) + height)
    canvas.create_rectangle(x1, y1, x2, y2, fill = color)

def draw_map_partitions(canvas: Canvas, partition: MapPartition, scale: int = 16):
    if partition.children[0] is not None:
        draw_map_partitions(canvas, partition.children[0], scale)

    if partition.children[1] is not None:
        draw_map_partitions(canvas, partition.children[1], scale)

    canvas.create_rectangle(partition.x * scale, partition.y * scale, (partition.x + partition.width) * scale, (partition.y + partition.height) * scale, fill = "", outline = "#00ff00")

def create_map(width: int, height: int):
    map_width, map_height = (math.trunc(width / 16), math.trunc(height / 16))

    dg = DungeonGenerator()
    dm, mp = dg.generate_map(map_width, map_height, 3)

    return (dm, map_width, mp)

def draw_map(canvas: Canvas, dungeon_map: list, map_width: int, map_partition: MapPartition = None):
    canvas.create_rectangle(0, 0, width, height, fill = "black")

    for i in range(len(dungeon_map)):
        if dungeon_map[i] == 0:
            continue

        map_x, map_y = (i % map_width, math.trunc(i / map_width))

        if dungeon_map[i] == 1:
            draw_tile(canvas, map_x, map_y)

        elif dungeon_map[i] == 2:
            draw_tile(canvas, map_x, map_y, color = "#0000ff")

        if map_partition is not None:
            draw_map_partitions(canvas, map_partition)

def draw_next_map(canvas: Canvas):
    dm, mw, mp = create_map(width, height)
    draw_map(canvas, dm, mw, mp)

width, height = (480, 480)

root = Tk()
root.title("Dungeon Generator")

canvas = Canvas(root, width = width, height = height)
canvas.pack()

reset_button = Button(root, text = "New Map", command = lambda: draw_next_map(canvas))
reset_button.pack()

draw_next_map(canvas)

root.mainloop()
