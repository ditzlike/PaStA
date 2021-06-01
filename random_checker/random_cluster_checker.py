#!/usr/bin/env python3 # One-time program for quickly checking the commits of the given projects
################################################################################

from tkinter import *
from tkinter import font
from PIL import ImageTk, Image
import tkinter as tk
from pathlib import Path
import git
import os
import re
import pandas as pd


output_file = os.path.join(os.getcwd(), "clusters.csv")
# TODO: des automatisch einlesen?
projects = ["uboot", "xen", "linux", "qemu"]
curr_project = "uboot"

clusters_path = os.path.join(os.getcwd(), "clusters")
if not os.path.exists(clusters_path):
    clusters_path = os.path.join(str(Path(os.getcwd()).parent), "clusters")

curr_cluster = ""


def prep_project_cluster_info():
    if os.path.exists(output_file):
        return pd.read_csv(output_file).fillna("").astype('str')
    row_list = list()
    for k in projects:
        project_path = os.path.join(clusters_path, k)
        
        for f in os.listdir(project_path):
            if (f.endswith(".png")) and not (f.startswith("random")):
                row_list.append({"project": k, "cluster": f, "random": ""})
    return pd.DataFrame(row_list, columns=["project", "cluster", "random", "guess"], dtype="string")

# this is a dataframe containing the project, clusters, which one is random and the researcher's guess
df = prep_project_cluster_info()

def check_cluster_marked(el):
    return len(df[df['cluster'] == el]['guess'].to_list()[0]) > 0

def select_cluster(event):
    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        data = event.widget.get(index)

        global curr_cluster
        global curr_project
        curr_cluster = data

        # Get the guess for the current cluster
        note = df[df["cluster"] == curr_cluster]["guess"].values[0].strip()
        e_check.delete(0, END)
        e_check.insert(0, note)

        global curr_project
        global clusters_path
        path1 = os.path.join(clusters_path, curr_project, "random_" + data)
        path2 = os.path.join(clusters_path, curr_project, data)
        random = df[(df['cluster'] == curr_cluster) & (df['project'] == curr_project)]['random'].astype('int')

        if int(random) == 0:
            global image1
            global image2
            image1 = Image.open(path1)
            image2 = Image.open(path2)

            global photo1
            global photo2
            photo1 = ImageTk.PhotoImage(image1)
            photo2 = ImageTk.PhotoImage(image2)
        else:
            image1 = Image.open(path2) # paths are switched
            image2 = Image.open(path1)

            photo1 = ImageTk.PhotoImage(image1)
            photo2 = ImageTk.PhotoImage(image2)
            

        canvas1.itemconfig(image_container1, image=photo1)
        canvas2.itemconfig(image_container2, image=photo2)


def select_project():
    lb.delete(0, END)
    global curr_project
    curr_project = sb.get()
    # Populate the list of cluster files
    project_path = os.path.join(clusters_path, curr_project)
    for f in os.listdir(project_path):
        if (f.endswith(".png")) and not (f.startswith("random")):
            lb.insert(END, f)
            lb.itemconfig(END, fg="green" if check_cluster_marked(f) else "black")


def select_file(event):
    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        data = event.widget.get(index)
        t2.delete(1.0, END)
        try:
            res = repo.git.execute(['git', 'show', "{}:{}".format(curr_cluster, data)])
            # Insert lines and add line numbers
            for idx, line in enumerate(res.splitlines()):
                t2.insert(END, "{} {}\n".format(idx+1, line))
        except Exception:
            # There may be exceptions if the file has been deleted (Ignore: Empty text will be shown)
            pass


def mark_cluster():
    mark = e_check.get()
    df.at[df[df['cluster'] == curr_cluster].index.values[0], 'guess'] = mark.strip()
    df.to_csv(output_file, index=False)

    lb.itemconfigure(lb.curselection(), fg="green" if check_cluster_marked(curr_cluster) else "black")


root = Tk()
root.title("Cluster Checker")

root.grid_rowconfigure(2, weight=7)
#root.grid_columnconfigure((0, 2, 4), weight=4)
root.grid_columnconfigure((0), weight=7)
#root.grid_columnconfigure((2), weight=1)
root.grid_columnconfigure((4), weight=5)

# ##################################### ROW 0
msg = Message(root, text="Left cluster is random: 0\n"
                         "Right cluster is random: 1\n", font=(None, 9), width=250)
msg.grid(row=0, column=3, padx=13, pady=5, sticky=N+W, columnspan=2)

sb = Spinbox(root, values=projects, bd=1, width=30, state="readonly", command=select_project)
sb.grid(row=0, column=0, padx=5, sticky=W+E+S, rowspan=1, columnspan=2)
sb.bind('<<SpinboxSelect>>', select_project)

ffs = font.Font(family='Courier', size=10)

lb = Listbox(root, width=30, bd=1, selectmode='single', font=ffs, exportselection=False)
lb.grid(row=0, column=2, padx=5, pady=5, sticky=W+E+S, columnspan=1, rowspan=2)
lb.bind('<<ListboxSelect>>', select_cluster)

yscroll0 = Scrollbar(command=lb.yview, orient=VERTICAL)
yscroll0.grid(row=0, column=3, sticky=N+S+W, rowspan=2)
lb.configure(yscrollcommand=yscroll0.set)

e_check = Entry(root, width=35, bd=1, )
e_check.grid(row=0, column=4, padx=5, sticky=W+E+S)

# ##################################### ROW 1
l = Label(root, text="Path to the clusters: (../<Curr_dir>|<Curr_dir>)/clusters/<project_name>")
l.grid(row=1, column=0, sticky=N+W+E, columnspan=2)

b1 = Button(root, text="Mark", command=mark_cluster)
b1.grid(row=1, column=4, padx=5, sticky=N+W)


def zoom_in():
    global photo1
    global image1
    new_size = (int(image1.size[0] * 1.1), int(image1.size[1] * 1.1))

    image1 = image1.resize(new_size, Image.ANTIALIAS)
    photo1 = ImageTk.PhotoImage(image1)
    canvas1.itemconfigure(image_container1, image=photo1)  # update image


def zoom_out():
    global photo1
    global image1
    new_size = (int(image1.size[0] * 0.9), int(image1.size[1] * 0.9))

    image1 = image1.resize(new_size, Image.ANTIALIAS)
    photo1 = ImageTk.PhotoImage(image1)
    canvas1.itemconfigure(image_container1, image=photo1)  # update image


canvas1 = Canvas(root)

image1 = Image.open(os.path.join(clusters_path, "uboot", "cluster_1.png"))
photo1 = ImageTk.PhotoImage(image1)
image_container1 = canvas1.create_image((0, 0), anchor=NW, image=photo1)

canvas1.bind('<ButtonPress-1>', lambda event: canvas1.scan_mark(event.x, event.y))
canvas1.bind("<B1-Motion>", lambda event: canvas1.scan_dragto(event.x, event.y, gain=1))

canvas1.grid(row=2, column=0, sticky=N+S+W+E, columnspan=1)

Button(root, text='+', command=zoom_in).grid(row=3, column=0, sticky='nwe')
Button(root, text='-', command=zoom_out).grid(row=4, column=0, sticky='nwe')


def zoom_in2():
    global photo2
    global image2
    new_size = (int(image2.size[0] * 1.1), int(image2.size[1] * 1.1))
    image2 = image2.resize(new_size, Image.ANTIALIAS)
    photo2 = ImageTk.PhotoImage(image2)
    canvas2.itemconfigure(image_container2, image=photo2)  # update image

def zoom_out2():
    global photo2
    global image2
    new_size = (int(image2.size[0] * 0.9), int(image2.size[1] * 0.9))
    image2 = image2.resize(new_size, Image.ANTIALIAS)
    photo2 = ImageTk.PhotoImage(image2)
    canvas2.itemconfigure(image_container2, image=photo2)  # update image

canvas2 = Canvas(root)

image2 = Image.open(os.path.join(clusters_path, "uboot", "random_cluster_1.png"))
photo2 = ImageTk.PhotoImage(image2)
image_container2 = canvas2.create_image(0, 0, anchor=NW, image=photo2)

canvas2.bind('<ButtonPress-1>', lambda event: canvas2.scan_mark(event.x, event.y))
canvas2.bind("<B1-Motion>", lambda event: canvas2.scan_dragto(event.x, event.y, gain=1))
canvas2.grid(row=2, column=2, sticky=N+S+W+E, columnspan=3)

Button(root, text='+', command=zoom_in2).grid(row=3, column=2, columnspan=3, sticky='nwe')
Button(root, text='-', command=zoom_out2).grid(row=4, column=2, columnspan=3, sticky='nwe')

mainloop()
