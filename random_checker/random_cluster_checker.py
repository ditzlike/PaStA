#!/usr/bin/env python3

# One-time program for quickly checking the commits of the given projects
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

#projects = {"mediawiki": ["070122e8b93984fe9345fed6eedc195285cc1991", "1d9b3b900c6991c910ab5f54a126eae8d89684e8",
#                          "1eb2307caa0e1a690ab080e5312104b86e2c3b27", "25d75b36b0e0bad3d80eb4dcdda0e0548299a021",
#                          "2f23e714902df2da216fe7b5bd09cb5d455a5020", "4539958087dcd428b720c9d1583d2943dcefb8e2",
#                          "495ec45a8a08d4ce9defc51da690f80f3369185d", "4e6fbd33bc3cec6d7237aa269ff1e1b6623d4825",
#                          "60a11e503590562d433c287e46c0b52fe5df087d", "62dec72993fd6b7fc3919c5b574380f5e013db5f",
#                          "70b000f0fb70d55c3d14125b6224c85bc4908100", "7fddf90b8d6197295265d9ae9f637faa710badbd",
#                          "a0eef4ef0dc0c25c3af7f23cbb252707fccef5be", "a4f99d65dcb0e5e4060f981015e57b97e2278e62",
#                          "a69fb4827409786203ee6f4befc5aa4009d13ef8", "b1b8b431f7785c3224239803b0efa44467bd03d3",
#                          "be57cf05dffc84690f7cea6d5a82e5912aef6566", "d530e2ef66db1de775319f1941e43042affe9df6",
#                          "eb755ddb3c496a922f09020595eac9fcb32814fc", "ef17ffa10c9f60af1b8e3e15f4add0a79f34937d"],
#            "phpbb": ["1042152a55ab2d0764c446949a77f085ab7a77f3", "167ca1f33f8265e5dea6481cc69de16ccfdd0dce",
#                      "215dff4ba8c01fc70c9e6c4589140734bbf7fd41", "23de1b638a32496a7a4bb37ae6ee87f4205b3440",
#                      "2a59e6d4864a993842167a40a9762702ad58db12", "3be239b8643ec5af0a2e03e88f7d419103fed900",
#                      "6601c3d64e7a3a57a6c956ee0eba19523b04e52f", "705d706a7f229857b0627c320b7cfe7f8432b51c",
#                      "7589a3093d95048f5a8cfdc6259501f43fd3fe10", "99b7d18ab2ee1b5b3ead555347b71fcb2de6e308",
#                      "afb69d7cd280df65b22b1a338d3023aebf2e3f0c", "c1531d9925585dbbbaa395ba10f16e7575aa1272",
#                      "c241a4a2b484b561b5515c6f8211a21d39fd8d78", "d10e5bfc1acc671b1028bfaa16b1dee24295a222",
#                      "d7e048da10d17beeda85e67bc6fcf8649716441a", "e523711ec2a8690de44748fc7382b7701f2fa6b1",
#                      "f035f266069d45cce56802224a184bfe66495233", "fb77cdd0513994dca478c06a3c9ac5912da07872",
#                      "fcc3dd996da198a8c659a5bb8bc02b27fa8f0885", "fd9c05309d186332728b533467aaecad5c543c52"],
#            "roundcubemail": ["0768134de16b1c75a1908da09f58cd627f2330b0", "09b0e36b3f453a410b3389b6d95a29605d13bfca",
#                              "188247894f6aff3a11f68bbdf94626b8bf58b852", "2bedfab77a33da76bb450bff20de76c4ecdf9898",
#                              "2e90ff5b62e8d9faaa39e042960c54034fcafa1e", "3e2637351da9559a4aa420004ac90e9fe30477ef",
#                              "51a9dd631f85b6e8ca1f83176d7a4679fdcbcca8", "565c472918e7f9707cd8d7909ad5dbcc5a921fdf",
#                              "58e3602a37cccab55f71fbf839b32fbc4322699c", "6237c947583f96df072b535d9b3c6fd7a79e2921",
#                              "78bee8b8b62f1ab4970c0b2b0265c17073ffb2be", "83370e5ff14f55f6af435807713956160f91abfa",
#                              "977a295eb1e97e0c230063da40b8296fca778814", "a12bbbaf41a200e98e437c2082b9dcc68c5a8f46",
#                              "a35062a1eba5c6c15f703686cd4fecc5536d74df", "b3ce7915610a6d272cc38ecd2a8b61e04ee4aeae",
#                              "ccce87d7ce17588c8f851af102cc35aa3d399fd2", "d7f3d796a240ed830346e74de46e108cc3fb4d3a",
#                              "dc088e25c2e96969705de7424bf18390b1505354", "e49064282339bf08f0dfcce4224a20ec055f32ac"],
#            "pdns": ["152b4591aa242f8fe4cfbedc6d44a30a896e4c11", "2717b8b383de410934faeb497642c9ea41e6ffc9",
#                     "289351c3c632a1f554783a5030a5886dee456ab5", "2d2151720ba8f20f0cd00ddc34d97c76204ae09b",
#                     "2ea3d25e0c9eeefdb6d625bc314ad40a19022e23", "3d766f445aa2819d0de6db2dec245ff87f1ddd5e",
#                     "549d63c9fbddda52010eadd819247dfe7f413514", "672d2e8913bded21ef69c436e3c2d88597a6ec37",
#                     "69821f62141a5b7899c49398bcb3321daffe70b8", "72160d955ab956a3d18c39a89c2e823f07c5d00e",
#                     "78bcb85857b15320e9cd2b28e8b486a667a1d79f", "7cbc52557d42ff64af8d5368ab5df3437e9ceb35",
#                     "8ffb7a9bab0d6adc4879f9cb1ce73ded65fa92be", "914353cadfd178585b98c115a692621d07f49d04",
#                     "c0b8e24a6fc3452b9eb3c0e6202919915bb51b54", "c0f6a1da6320c428e65eb6d6879cca972cd1eb92",
#                     "c4d0cb1bbf084e2f16f78f6b85f06db87e12608b", "cea2635091b7e39891187d52e38cb464bc71283b",
#                     "dd930ede3644c18ba33096f15f74cf2bbb9d9e52", "ef2ea4bfc5f80a8e1de0fb1ec4db33656fb83bf6"],
#            "joomla-cms": ["025ec26f8e9357112a54da6370f3b6caee6b4c4c", "051ff8bceaae4c1284d05d352d1b01f11f94e2fd",
#                           "09aee379bd251a8e4b2929ff2511d1233e286dc6", "493af5bd8f45705747373c8e3d78181237b23a7b",
#                           "54696975eb5d4c72a84a32b388adc1e5ad4b3470", "58c90c81a2a5ec90abf349a5a19d0c6bb67227df",
#                           "630c5fa7868bb3728eb21e8d143cecb4824acd57", "7b1506178660d6797008c1866473f7465785eeb9",
#                           "7fa08788b3a5e52af4e7eebfbe482c58bcd93950", "9dc3118c8a95e4956acc3692f9f431b8f2c26d44",
#                           "a075b73547c3a8226a5023679ca619040528401f", "a6ea290ba856de738578a92f95b061f418b443b5",
#                           "afa37474d78e827aef29631ad79caddcb3c6bf32", "b3e64fbbccd442f6f94a3b7b0b8e90aab0c36999",
#                           "b558b58b6a0cbe0c0239493150d9c4edb6634cde", "b62db9cc290af6e49be0cae9953ca72c4cf3a427",
#                           "bf1020db8ebb785fb825dc6a06bd1972af86d13b", "caf4219cc64c3d8c61b2f58116a550f0d3455170",
#                           "cb91c072c2e9ec98651c751360844a69c398ee20", "f35a1742a0991d36033a3eb8c154a2ef8efbf21b"],
#            "TYPO3.CMS": ["1409cddc8b3b7b7f7e8e9744a26e73e39b9e28b9", "2731b97e81939396040f777b786b38833a8afb98",
#                          "27673d89d96a02fbf142eccfb3bbdae37e3dc635", "279fee3fc25d7e268d3d8b5362cb5a726ec15e30",
#                          "2d7c0bce7aa318b67cfee5346019b67b93157a9a", "4b8f98a9094f8ede54e218a76a731221ed1fd32a",
#                          "50b348155beb15b9f3d4a26467b15f86235e9a5f", "5cf4f3293a1e0dc69fcf48e7bf3b268de65f42ed",
#                          "6aa79bd545865ee37b43acae137021c1131bc7f4", "7e9067163b4d7ecdfd2e2c29089f311a5b634040",
#                          "82e37403de0db177e214374f7c37f271a1134180", "945f3586857b2d6b4e29381ea59e9c252723d4af",
#                          "97b19dc64f64f60fed5878ef965d9b9d345035a0", "9b8cdc28dcf56177c5203ca0c50a1d6d456f3e2b",
#                          "a42a6092d203951614ffa355a190ad45a632bf5e", "a81bfff2277f49e3f71d9fdd063015ce99f6321e",
#                          "b90823c07bb32393320a53d1537f58ae70f33223", "bf9e0ef6f82b7b77abefe3f903df49871625656e",
#                          "d7bea56c387a8080279be3fdf4b7986c513a9fba", "e94b024c9ceb564aacabcec9220c80bb568bf8e8"],
#            "oscar": ["007e0e5df80a103d8a57703089827780aeffa976", "04877c6f1190985bb2cdb22783b330377b73721f",
#                      "4514c3262bcf7b150a711e40ed3273d9400aa1a4", "4dcc82ae0e79e462393ad80997321938936d0814",
#                      "4dd9fa64f3fb57f644a1b43c6c48528a76bd5d3e", "509fae48d3ee37adf4709224503087299a5edf2a",
#                      "58b1fc5116141a8b5ee746bd02b476682ca2a9b5", "6811a55b66e5ccdbf1d2f01c13fc0773c85ab973",
#                      "7cd0deb98e2f8e60d73aa629a8ce985d5062ebd9", "9ae639915140bc62da5e424c7762bdc7a29bc1be",
#                      "a691e3605564eb1511e75fcbf0ece7cd65963f90", "ab82d54b147a7c0cb9a256c6ce5d4bd9d71cd3f5",
#                      "b14952eb448b9e339b3b4246bb62dc1c0f20147b", "b2656bc18bc9f3e9cc8a0376e8147479d78ca50c",
#                      "cf192c258e285a9cf8d191872a7f9ad7f49bef0f", "d9e1d94e56b68feca8a28fa360c52dd6a1c506dc",
#                      "db9f817c08c2e8932e1b17f50a362933ac83df49", "def449c98442521d98077cb68ddd9d036ee9a94b",
#                      "e7b430c23c3d7cb5a3406bf97e393da891e7d52a", "fa0e96c4508139500ba300652082151ab6e90815"],
#            "biblioteq": ["0877d9c375923ce633df6023c37832704bc82bb7", "13fdc511f52d9b2f42895c7a94eba3bb0442538f",
#                          "1edb48cc3699ec0a4c353f7fa0dcb1fb5dede75c", "39dde2a6b41940a7e94aa6a858b1a244fdbdfedf",
#                          "54aee6e2f5183df2295fd4f84e2960acf59ad2a9", "57dfbf913c127faddbc1f03773b36f7ffb88f39f",
#                          "5a5395217fc900633057bea71e31ea9b9c19c578", "666fcf670a53140f5da4e92299dcd7dfab4d62f7",
#                          "6c0988247f5377913350dcd6bb41cfeb67be2607", "6f9fb64f8ff68e178542ecad69933bee1a5d7519",
#                          "72d8cca78e0e36657444eb3228c2b1bbb7b7f28e", "77b82c0b0553b34339f6e4f05593c20fe72b5eb6",
#                          "79ba465ea5f8861f215f80c2783e197f0c3c12c4", "929b7db262b021b15a8428241e7e484b9fcc7435",
#                          "c78c42e2875391d1b697b00d9559bacae6a8d3a3", "d80e45b4df0a96e5b1ed233fe6a51346d6dc2dbb",
#                          "dd4f37f77c5d085760202501a92525a7ed1f04cf", "eddb346ea78575649affde918b7166052ceb9668",
#                          "f0c724d790a78a0ca1c45c50e9b8487f52fdc482", "fdebd40950748b041efc5b090f7245e28191e6a1"]}

output_file = os.path.join(os.getcwd(), "projects_commits_checked.csv")
#projects_lst = list(projects.keys())
projects = ["uboot", "xen", "linux", "qemu"]
curr_project = "uboot"

#repos_path = os.path.join(os.getcwd(), "repos")
clusters_path = os.path.join(os.getcwd(), "clusters")
if not os.path.exists(clusters_path):
    clusters_path = os.path.join(str(Path(os.getcwd()).parent), "clusters")

#repo = git.Repo(os.path.join(clusters_path, curr_project))
#curr_commit = ""
curr_cluster = ""
#pattern = re.compile("^diff\s--git", re.MULTILINE)


def prep_project_commit_info():
    # don't know what to do with the output file
    #if os.path.exists(output_file):
    #    return pd.read_csv(output_file).fillna("").astype('str')
    row_list = list()
    for k in projects:
        project_path = os.path.join(clusters_path, k)
        
        for f in os.listdir(project_path):
            if (f.endswith(".png")) and not (f.startswith("random")):
                row_list.append({"project": k, "cluster": f, "random": ""})
        #for v in projects[k]:
        #    row_list.append({"project": k, "commit": v, "note": ""})
    return pd.DataFrame(row_list, columns=["project", "cluster", "random"], dtype="string")

# this is a dataframe containing the project and clusters
df = prep_project_commit_info()


#def check_commit_marked(el):
#    return len(df[df['commit'] == el]['note'].to_list()[0]) > 0

def check_cluster_marked(el):
    #return len(df[df['commit'] == el]['note'].to_list()[0]) > 0
    # TODO hier nachschauen, wie man das ding markiert hat, random oder nicht
    return True

#def select_commit(event):
#    selection = event.widget.curselection()
#    if selection:
#        index = selection[0]
#        data = event.widget.get(index)
#
#        global curr_commit
#        curr_commit = data
#
#        # Get a note for the current commit
#        note = df[df["commit"] == curr_commit]["note"].values[0].strip()
#        e_check.delete(0, END)
#        e_check.insert(0, note)
#
#        res = repo.git.execute(['git', 'show', '--oneline', data])
#
#        # Clean Text_1, Text_2
#        t1.delete(1.0, END)
#        t2.delete(1.0, END)
#
#        # Fill Text_1
#        for line in res.splitlines():
#            if line.startswith("--- a/") or line.startswith("--- /dev") or \
        #                    line.startswith("+++ b/") or line.startswith("+++ /dev"):
#                tag = "normal"
#            elif line.startswith("+"):
#                tag = "added"
#            elif line.startswith("-"):
#                tag = "deleted"
#            elif line.startswith("diff --git"):
#                tag = "diff"
#            else:
#                tag = "normal"
#            # To fix the error: character <...> is above the range (U+0000-U+FFFF) allowed by Tcl
#            # (from https://learning-python.com/cgi/showcode.py?name=pymailgui-products%2Funzipped%2FPyMailGui-PP4E%2FfixTkBMP.py&rawmode=view)
#            line = ''.join((ch if ord(ch) <= 0xFFFF else '\uFFFD') for ch in line)
#            t1.insert(END, "{}\n".format(line), tag)
#
#        # Clean ListBox_Files
#        lb_files.delete(0, END)
#
#        changes_x = pattern.split(res)[1:]
#        change_lines = [change.splitlines() for change in changes_x]
#
#        # Fill ListBox_Files
#        for idx, change in enumerate(change_lines):
#            second_path_start_idx = change[0].find(" b/")
#            new_path = change[0][second_path_start_idx:].strip()
#            new_path = new_path[2:]
#            lb_files.insert(END, new_path)


# passiert, wenn man oben einen Commit auswaehlt
def select_cluster(event):
    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        data = event.widget.get(index)

        global curr_cluster
        curr_cluster = data

        # Get a note for the current cluster
        # TODO; wtf does this do
        note = df[df["cluster"] == curr_cluster]["random"].values[0].strip()
        e_check.delete(0, END)
        e_check.insert(0, note)

        #res = repo.git.execute(['git', 'show', '--oneline', data])

        # Clean Text_1, Text_2
        # TODO: statt Texten hier die beiden Bilder
        t1.delete(1.0, END)
        t2.delete(1.0, END)

        # Fill Text_1
        # TODO: hier die png's reinholen I guess
        for line in res.splitlines():
            if line.startswith("--- a/") or line.startswith("--- /dev") or \
                    line.startswith("+++ b/") or line.startswith("+++ /dev"):
                        tag = "normal"
            elif line.startswith("+"):
                tag = "added"
            elif line.startswith("-"):
                tag = "deleted"
            elif line.startswith("diff --git"):
                tag = "diff"
            else:
                tag = "normal"
            # To fix the error: character <...> is above the range (U+0000-U+FFFF) allowed by Tcl
            # (from https://learning-python.com/cgi/showcode.py?name=pymailgui-products%2Funzipped%2FPyMailGui-PP4E%2FfixTkBMP.py&rawmode=view)
            line = ''.join((ch if ord(ch) <= 0xFFFF else '\uFFFD') for ch in line)
            t1.insert(END, "{}\n".format(line), tag)

        # Clean ListBox_Files
        lb_files.delete(0, END)

        changes_x = pattern.split(res)[1:]
        change_lines = [change.splitlines() for change in changes_x]

        # Fill ListBox_Files
        for idx, change in enumerate(change_lines):
            second_path_start_idx = change[0].find(" b/")
            new_path = change[0][second_path_start_idx:].strip()
            new_path = new_path[2:]
            lb_files.insert(END, new_path)


#def select_project():
#    lb.delete(0, END)
#    global curr_project
#    curr_project = sb.get()
#    # Populate the list of commit-hashes
#    for el in projects[curr_project]:
#        lb.insert(END, el)
#        lb.itemconfig(END, fg="green" if check_commit_marked(el) else "black")
#    global repo
#    repo = git.Repo(os.path.join(repos_path, curr_project))
#
#    # When selecting another project, clear file list and text boxes
#    lb_files.delete(0, END)
#    t1.delete(1.0, END)
#    t2.delete(1.0, END)


def select_project():
    lb.delete(0, END)
    global curr_project
    curr_project = sb.get()
    # Populate the list of cluster files
    project_path = os.path.join(clusters_path, curr_project)
    for f in os.listdir(project_path):
        if (f.endswith(".png")) and not (f.startswith("random")):
            lb.insert(END, f)
            lb.itemconfig(END, fg="green" if check_cluster_marked else "black")


    # When selecting another project, clear file list and text boxes
    lb_files.delete(0, END)
    t1.delete(1.0, END)
    t2.delete(1.0, END)


def select_file(event):
    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        data = event.widget.get(index)
        t2.delete(1.0, END)
        try:
            res = repo.git.execute(['git', 'show', "{}:{}".format(curr_commit, data)])
            # Insert lines and add line numbers
            for idx, line in enumerate(res.splitlines()):
                t2.insert(END, "{} {}\n".format(idx+1, line))
        except Exception:
            # There may be exceptions if the file has been deleted (Ignore: Empty text will be shown)
            pass


def mark_commit():
    mark = e_check.get()
    df.at[df[df['commit'] == curr_commit].index.values[0], 'note'] = mark.strip()
    df.to_csv(output_file, index=False)

    lb.itemconfigure(lb.curselection(), fg="green" if check_commit_marked(curr_commit) else "black")


root = Tk()
root.title("Cluster Checker")

root.grid_rowconfigure(2, weight=7)
root.grid_columnconfigure((0, 2, 4), weight=4)

# ##################################### ROW 0
msg = Message(root, text="No schema/no db-relevant code: 0\n"
                         "No schema/db-relevant code: 1\n"
                         "Schema/no db-relevant code: 2\n"
                         "Schema/db-relevant code: 3\n"
                         "Unsure: ? (Prefix all comments by '?')", font=(None, 9), width=250)
msg.grid(row=0, column=3, padx=13, pady=5, sticky=N+W, columnspan=2)

#sb = Spinbox(root, values=projects_lst, bd=1, width=30, state="readonly", command=select_project)
sb = Spinbox(root, values=projects, bd=1, width=30, state="readonly", command=select_project)
sb.grid(row=0, column=0, padx=5, sticky=W+E+S, rowspan=1, columnspan=2)
sb.bind('<<SpinboxSelect>>', select_project)

ffs = font.Font(family='Courier', size=10)

lb = Listbox(root, width=30, bd=1, selectmode='single', font=ffs, exportselection=False)
lb.grid(row=0, column=2, padx=5, pady=5, sticky=W+E+S, columnspan=1, rowspan=2)
#lb.bind('<<ListboxSelect>>', select_commit)
lb.bind('<<ListboxSelect>>', select_cluster)

yscroll0 = Scrollbar(command=lb.yview, orient=VERTICAL)
yscroll0.grid(row=0, column=3, sticky=N+S+W, rowspan=2)
lb.configure(yscrollcommand=yscroll0.set)

e_check = Entry(root, width=35, bd=1, )
e_check.grid(row=0, column=4, padx=5, sticky=W+E+S)

# ##################################### ROW 1
l = Label(root, text="Path to the clusters: (../<Curr_dir>|<Curr_dir>)/clusters/<project_name>")
l.grid(row=1, column=0, sticky=N+W+E, columnspan=2)

b1 = Button(root, text="Mark", command=mark_commit)
b1.grid(row=1, column=4, padx=5, sticky=N+W)

# ##################################### ROW 2
#t1 = Text(width=70)
#t1.grid(row=2, column=0, padx=5, sticky=N+S+W+E)
#t1.tag_config("deleted", background="white", foreground="red")
#t1.tag_config("added", background="white", foreground="green")
#t1.tag_config("normal", background="white", foreground="black")
#t1.tag_config("diff", background="lightgrey", foreground="black")
#t1.configure(font=("Courier", 10))

img1 = ImageTk.PhotoImage(Image.open(os.path.join(clusters_path, "uboot", "reapersax.jpg")))
#img1 = img1._PhotoImage__photo.zoom(1)
#panel1 = tk.Label(root, image = img1)
#panel1.grid(row=2, column=0, padx=5, sticky=N+S+W+E)

#copied from https://stackoverflow.com/questions/41656176/tkinter-canvas-zoom-move-pan#60149696
def do_zoom(event):
    factor = 1.001 ** event.delta
    is_shift = event.state & (1 << 0) != 0
    is_ctrl = event.state & (1 << 2) != 0
    canvas.scale(ALL, event.x, event.y,
                 factor if not is_shift else 1.0,
                 factor if not is_ctrl else 1.0)

canvas1 = Canvas(root)
#canvas1.pack()

# copied from above
canvas1.bind('<ButtonPress-1>', lambda event: canvas1.scan_mark(event.x, event.y))
canvas1.bind("<B1-Motion>", lambda event: canvas1.scan_dragto(event.x, event.y, gain=1))

canvas1.create_image(0, 0, anchor=NW, image=img1)
canvas1.grid(row=2, column=0, sticky=N+S+W+E)
#canvas1.bind("<MouseWheel>", do_zoom)
#canvas1.bind('<Button-5>',   wheel)  # only with Linux, wheel scroll down
#canvas1.bind('<Button-4>',   wheel)  # only with Linux, wheel scroll up


#xsb = tk.Scrollbar(orient="horizontal", command=canvas1.xview)
#ysb = tk.Scrollbar(orient="vertical", command=canvas1.yview)
#canvas1.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
#canvas1.configure(scrollregion=(0,0,1000,1000))

#yscroll1 = Scrollbar(command=t1.yview, orient=VERTICAL)
#yscroll1 = Scrollbar(command=panel1.yview, orient=VERTICAL)
#yscroll1.grid(row=2, column=1, sticky=N+S+W)
#t1.configure(yscrollcommand=yscroll1.set)
#panel1.configure(yscrollcommand=yscroll1.set)

t2 = Text(width=70)
t2.grid(row=2, column=2, padx=5, sticky=N+S+W+E)
t2.configure(font=("Courier", 10))

yscroll2 = Scrollbar(command=t2.yview, orient=VERTICAL)
yscroll2.grid(row=2, column=3, sticky=N+S+W)
t2.configure(yscrollcommand=yscroll2.set)

lb_files = Listbox(root, width=45, bd=1, selectmode='single', font=ffs, exportselection=False)
lb_files.grid(row=2, column=4, padx=5, sticky=N+S+E+W)
lb_files.bind('<<ListboxSelect>>', select_file)

yscroll3 = Scrollbar(command=lb_files.yview, orient=VERTICAL)
yscroll3.grid(row=2, column=5, sticky=N+S+W)
lb_files.configure(yscrollcommand=yscroll3.set)

# ##################################### ROW 3
yscroll4 = Scrollbar(command=lb_files.xview, orient=HORIZONTAL)
yscroll4.grid(row=3, column=4, sticky=W+E, columnspan=2)
lb_files.configure(xscrollcommand=yscroll4.set)


mainloop()
