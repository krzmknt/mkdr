import yaml
import pathlib
import os
from collections import namedtuple
import argparse
import shutil

Path = namedtuple("Path", ["type", "path"])


sign_dir = "d"
sign_file = "f"


parser = argparse.ArgumentParser()
parser.add_argument(
    "-f", "--force", action="store_true", help="Overwrite the existing objects"
)
parser.add_argument(
    "-e", "--export", action="store_true", help="Generate <timestamp>.yml"
)
parser.add_argument("-r", "--reorg", action="store_true", help="")
arg = parser.parse_args()


def loadOrganization():
    # Load organization.yml
    file_dir = "./organization.yml"
    with open(file_dir) as f:
        paths_yml = yaml.load(f, Loader=yaml.SafeLoader)
    return paths_yml


def isDirectory(d):
    if isinstance(d, dict):
        return True
    return False


def getDirName(d):
    return list(d.keys())[0]


def getDirContents(d):
    return d[getDirName(d)]


def getPaths(paths_yml):
    path = ["."]
    paths = []

    def recursiveMkdir(paths_yml, path):
        for d in paths_yml:
            if isDirectory(d):
                path.append(getDirName(d))
                paths.append(Path(sign_dir, "/".join(path)))
                recursiveMkdir(getDirContents(d), path)
            elif d is not None:
                paths.append(Path(sign_file, "/".join(path) + "/" + d))
        path.pop()

    recursiveMkdir(paths_yml, path)
    return paths


def checkExistence(paths):
    paths_exist = [p.path for p in paths if os.path.exists(p.path)]
    if paths_exist:
        print(
            "Error: The object(s) already exist(s). If you overwrite, please specify `--force` option."
        )
        for p in paths_exist:
            print(p)
        return True
    return False


def deleteObjects(paths):
    paths_exist = [p.path for p in paths if os.path.exists(p.path)]
    for p in paths_exist:
        if os.path.exists(p):
            shutil.rmtree(p)


def makeObject(p):
    if p.type == sign_dir:
        os.makedirs(p.path)
    else:
        pathlib.Path(p.path).touch()


def main():
    paths_yml = loadOrganization()
    paths = getPaths(paths_yml)

    if arg.force:
        deleteObjects(paths)
    elif checkExistence(paths):
        return

    print("%d directories/files are successfully created!" % len(paths))
    for p in paths:
        print("", p.path)
        makeObject(p)


if __name__ == "__main__":
    main()
