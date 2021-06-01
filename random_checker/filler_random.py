import os
import pandas as pd
import random

print("Starting now...")
output_file = os.path.join(os.getcwd(), "projects_clusters_checked.csv")
projects = ["uboot", "xen", "linux", "qemu"]
curr_project = "uboot"

clusters_path = os.path.join(os.getcwd(), "clusters")

def fill_csv():
    row_list = list()
    for k in projects:
        project_path = os.path.join(clusters_path, k)

        for f in os.listdir(project_path):
            if (f.endswith(".png")) and not (f.startswith("random")):
                r = random.randint(0, 1)
                row_list.append({"project": k, "cluster": f, "random": r, "guess": ""})
        #for v in projects[k]:
        #    row_list.append({"project": k, "commit": v, "note": ""})
    #return pd.DataFrame(row_list, columns=["project", "cluster", "random"], dtype="string")
    df = pd.DataFrame(row_list, columns=["project", "cluster", "random", "guess"], dtype="string")
    df.to_csv('clusters.csv')

fill_csv()
