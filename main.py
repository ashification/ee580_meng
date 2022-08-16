# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

#Import the required libraries
from tkinter import *


#Define Canvas Window Values
root = Tk()
root.title('RTLS Simulator')
root.geometry("1340x810")

#Definte Image
bg = PhotoImage(file="C:/images/Floorplan_v3.png")
tag = PhotoImage(file="C:/images/tag.png")

#Define co-ordinates
varwidth=800
varheight=500
x_coord=varwidth//2
y_coord=varheight//2

#create canvas
canvas = Canvas(root, width=varwidth, height=varheight)
canvas.pack(fill="both", expand=True)

#Set canvas Background Image
canvas.create_image(0,0, image=bg, anchor="nw")

# Define Tag
#coordinates_tag = 200, 100, 250, 150  # x1, y1, x2, y2
tag_object = canvas.create_oval(x_coord, y_coord, x_coord+30, y_coord+30, fill="#FFFF00")

def left(event):
    x_coord = -10
    y_coord = 0
    canvas.move(tag_object, x_coord, y_coord)
    # Get and Print the coordinates of the tag
    print("Coordinates of the tag are:", canvas.coords(tag_object))

def right(event):
    x_coord = 10
    y_coord = 0
    canvas.move(tag_object, x_coord, y_coord)
    # Get and Print the coordinates of the tag
    print("Coordinates of the tag are:", canvas.coords(tag_object))


def up(event):
    x_coord = 0
    y_coord = -10
    canvas.move(tag_object, x_coord, y_coord)
    # Get and Print the coordinates of the tag
    print("Coordinates of the tag are:", canvas.coords(tag_object))


def down(event):
    x_coord = 0
    y_coord = 10
    canvas.move(tag_object, x_coord, y_coord)
    #Get and Print the coordinates of the tag
    print("Coordinates of the tag are:", canvas.coords(tag_object))

root.bind("<Left>", left)
root.bind("<Right>", right)
root.bind("<Up>", up)
root.bind("<Down>", down)
#print("X coord = ", x_coord, " y coord = ", y_coord)

## Anchor co-ords
#1_anchor = (60, 230)
#2_anchor = (60, 590)
#3_anchor = (1140, 420)

#Run Window
root.mainloop()
