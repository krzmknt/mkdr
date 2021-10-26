# mkdr
`mkdr` is a DaC(Directories as Code) tool by which you can generate, export and reorganize direcotory structure based on a YAML format.


## Install
Supported only on Mac OS. Installed via homebrew.

```
brew tap krzmknt/mkdr
brew install mkdr
```


## Example
1. Create the base file `mkdrcompose.yml`. For example:
```yaml
- README.md
# - .git
- App:
  -
- Infra:
  - Nginx:
    - Dockerfile
    - work:
      - nginx.conf
  - Python:
    - Dockerfile
    - work:
      - requirements.txt
      - uwsgi.ini
  - MySQL:
- docker-compose.yml
- log:
  - access.log
  - app.log
  - error.log
```
2. Run `mkdr` in the same directory where the base file `mkdrcompose.yml` placesd. The specified objects are generated.


## Specification

### Summary
| Mode\Option | Feature(No option)  | `--force` | `--name` | '--nut'            |
|-------------|---------------------|-----------|----------|--------------------|
| Compose     | Make objects        | Enable    | Enable   | Make empty objects |
| Export      | Make a base file    | Enable    | Enable   | x                  |
| Delete      | Remove objects      | Enable    | Enable   | x                  |
| Reorg       | Resorganize objects | x         | Enable   | x                  |


### Modes
- Compose: It is executed by specifying the `-c|--compose` mode option, or by not specifying any mode option. Extract the directory structure described in `mkdrcompose.yml` to the current directory. If `mkdrcompose.yml` does not exist, an error occurs. The index at the end of the file name of `mkdrcompose.yml` is treated as metadata and is truncated from the file name. When creating a file with the extension `<ext>`, if the template file `template.<ext>` exists in the mkdr configuration folder, a copy of it will be created. If the template file does not exist, an empty file will be created. If one of the files you try to extract already exists, none of the files will be extracted. To force the expansion, specify the `--force` option.
- Export: This mode is enabled by specifying the `-e|--export` option. Export the organization of the current directory to `mkdrcompose.yml`. If there are multiple files with the same file name, they will be output indexed.
- Delete: Performed by specifying the `-d|--delete` option. It deletes the objects listed in `mkdrcompose.yml`. Because the objects are deleted from the top-level folder, the entire folder is deleted even if the objects contained in the folder are not listed in `mkdrcomopse.yml`. You will be asked to comfirm before deleting. The index at the end of the file name in `mkdrcompose.yml` is treated as metadata and ignored. If you execute the delete mode immediately after the compose mode, all generated files will be deleted. If you run execute the delete mode immediately after the export mode, all files in the current directory will be deleted.
- Reorg: Performed by the `-r|--reorg` mode option. Reorganize files in the existing directory according to `mkdrcompose.yml`. You can assign a index to an objext to specify files with the same name. The indexes of existing files can be checked by the configuration file output by export mode.
- Config: Show the mkdr config path.


### Options
- `-f|--force`
  - If this option specified, `mkdr` overwrite the objects even if they are alredy exists or do not confirm the deletion.
- `-n|--name`
  - You can specify the base file name with this option. (default: `mkdrcompose.yml`)
- `--nut|--not-use-template`
  - When `-nut|--not-use-template` is specified, templates in neither the current directory nor config directory should be used.


### Configuration
- The path set in the environment variable `MKDR_CONFIG_PATH` is assumed to be the configuration directory. If `.mkdr` directory exists in the current directory, it will be preferred as the configuration folder.
- You can check the configuration file path with `--config`.


### mkdrcompose.yml
- Follow the syntanx of YAML.
- File name is a string type. Directory name is a key of a dictionary, and its contents are represented by a list of directories and files as the value of the dictionary.
- The naming rules for files and directories are the same as those of the operating system, up to 255 characters.
- Multiple objects with the same path cannot exist in a single `mkdrcompose.yml` file.
- The file name can be changed by setting the value of the `MKDR_BASE_FILENAME` environment variable.
- You can disable the line of `mkdrcompose.yml` by commenting it out or putting it in `.mkdrignore`.


### .mkdrignore
- `.mkdrignore` is implemeted in the future version.


