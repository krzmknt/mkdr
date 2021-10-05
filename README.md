# mkdr

RaC(Repositories as Code):`mkdr` (re)organizes direcotries and files according to a configuration file.

## Install
```
brew tap krzmknt/mkdr
brew install mkdr
```

#Usage
1. Make `organization.yml`.
```yaml
- README.md
# - Dockerfile
- src:
  - static:
    - index.html
    - style.css
  - images:
    -
  - js:
    - common.js
- log:
  - access.log
  - error.log
```
2. Run `mkdr` command at the same directory where you placed file `organization.yml`
3. `src/` and `log/` directory are generated at the current direcotry.


## option
- `--force` | `-f` : If the designated objects are already exist, first remove it and then newly remake the objects.
- `--export` | `-e` : Generate an `organization.yml` file according to the existing current directory.


