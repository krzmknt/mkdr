# mkdr
`mkdr` is a DaC(Directories as Code) tool by which you can generate, export and reorganize direcotory structure based on a yaml format configuration file.


## Install
Supported only on Mac OS. Installed via homebrew.

```
brew tap krzmknt/mkdr
brew install mkdr
```


## Example
1. Create the configuration file `mkdr-config.yml`. For example:
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
2. Run `mkdr` in the same directory where the configuration file `mkdr-config.yml` created. Then, the specified (empty) objects are generated.


## Specification

### Function Summary
| Mode\Option               | Feature(No option) | `--force` | `--name` |
|---------------------------|--------------------|-----------|----------|
| Organize                  | Make Objects       | Enable    | Enable   |
| Save                      | Make a Config      | Enable    | Enable   |
| Remove                    | Remove Objects     | Enable    | Enable   |
| Reorg(Not implemeted yet) | Sort Objects       | Disable   | Enable   |


### Modes
- Organize(default):
  - The objects are created in the current directory based on the configuration file.
  - If a part of the configuration file already exists, an error will occur and no processing will be performed.
- Save(`-s|--save`):
  - A configuration file will be created based on the configuration of the current directory.
  - If the configuration file already exists, you will be asked if you overwrite it.
- Remove(`-r|--remove`):
  - All objects in the configuration file will be removed.
  - Confirm before removing.
- Reorg(`-o|--reorg`) (Not implemented yet):
  - Existing directory structure will be reorganized based on the configuration file.
  - If an object that does not exist in the current directory is included in the configuration file, an error will occur and no processing will be performed.


### Options
- Force(`-f|--force`): Execute the command without confirmation.
  - For make mode: Overwrite the object in the configuration file with an empty object even if it already exists in the current directory.
  - For save mode: Overwrite the saving file, even if it already exists.
  - For remove mode: Remove the objects without confirmation.
  - For reorg mode: The option is disabled.
- Name(`-n|--name <filename>`): Specifiy the configuration file name. (Defulat:`mkdr-config.yml`)


### .mkdrignore
`.mkdrignore` functionality will be implemented in the future virsion. Stay tune!


### Errors
- UserError: Running mkdr as root is not supported.
- ModeError: Only one mode can be specified.
- OptionError: Reorg mode does not suppourt `--force` option.
- FileNotFoundError: The existing configuration file must be specified.
- CannotOverwriteError: Without `--force` option, make mode cannot overwrite the existing objects.


