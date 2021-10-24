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
| Mode\Option | Feature(No option)                    | `--force` | `--name` | '--nut'            |
|-------------|---------------------------------------|-----------|----------|--------------------|
| Compose     | Make objects acc. config and template | Enable    | Enable   | Make empty objects |
| Export      | Make a config                         | Enable    | Enable   | x                  |
| Delete      | Remove objects acc. config            | Enable    | Enable   | x                  |
| Reorg       | Resorganize objects acc. config       | x         | Enable   | x                  |


### mkdrcompose.yml
- YAML の文法に従う
- 同一のパスを持つ複数のオブジェクトは１つの yml には存在できない
- 255文字以内
- ディレクトリは辞書、ファイルは文字列で表す。ディレクトリの中身はディレクトリかファイルのリストで表す。カレントディレクトリで含まれる


### Modes
- Compose `-c|--compose` (default):
  - The objects are created in the current directory based on the configuration file.
  - If a part of the configuration file already exists, an error will occur and no processing will be performed.
- Export `-e|--export`:
  - A configuration file will be created based on the configuration of the current directory.
  - If the configuration file already exists, you will be asked if you overwrite it.
- Delete `-d|--delete`:
  - All objects in the configuration file will be removed.
  - Confirm before removing.
- Reorg `-r|--reorg`:
  - Existing directory structure will be reorganized based on the configuration file.
  - If an object that does not exist in the current directory is included in the configuration file, an error will occur and no processing will be performed.
- Config `--config`
  - 設定フォルダのパスを表示する

#### Compose
`-c|--compose` のモードオプションを指定、またはモードオプションを何も指定しないことによって実行される。`mkdrcompose.yml` に記載したディレクトリ構成をカレントディレクトリに展開する。 `mkdrcompose.yml` が存在しない場合はエラーとなる。`mkdrcompose.yml` のファイル名末尾に記載した添字はメタデータとして扱われ無視される。拡張子 `<ext>` のファイルを作成する場合、mkdr の設定フォルダにテンプレートファイル `template.<ext>` が存在するならそのコピーを作成する。存在しない場合は通常通り空のファイルを作成する。展開しようとしたファイルのうち１つでも既に存在している場合、展開は行われない。強制的に展開する場合は `--force` オプションを指定する。

##### Options
- `-f|--force` 指定時には composeファイルに記載のオブジェクトが既に存在していたとしてもエラーとならずファイルが上書きされる
- `-n|--name` によって読み込むファイル名が指定可能
- `-nut|--not-use-template` 指定時には、configもcdのtemplateも利用されないこと


#### Export
`-e|--export` のモードオプションを指定することによって実行される。カレントディレクトリの構成を構成ファイル `mkdrcompose.yml` にエクスポートする。同一名のファイルが複数存在する場合は添字付けられて出力される。Compose の直後に Export を実施た場合は、compose の内容がエクスポートされたファイルに含まれる。

##### Options
- `-f|--force` を指定することにより出力ファイルが既に存在する場にも確認無しで上書き作成される
- `-n|--name <filename>` により出力ファイルの名前が選択可能


#### Delete
`-d|--delete` オプションを指定することにより実行される。構成ファイルに記載されたオブジェクトを削除する。トップレベルフォルダから削除するため、フォルダに含まれるオブジェクトが構成ファイルに記載されていなくともフォルダごと削除される。削除前に確認が行われる。`mkdrcompose.yml` のファイル名末尾に記載した添字はメタデータとして扱われ無視される。
Compose の直後に delete を実行すると展開したすべてのファイルが削除される。Export の直後に delete を実行するとすべてのカレントディレクトリの全てのファイルが削除される。

##### Options
- `-f|--force` 確認無しでオブジェクトが削除される
- `-n|--name <filename>` 構成ファイルの名前を指定する


#### Reorganization
`-r|--reorg` モードオプションによって実行される。既存のディレクトリのファイルを `mkdrcompose.yml` の構成に従って再構成する。同一名ファイルの指定には添字を用いる。既存ファイルの添字は export モードによって出力された構成ファイルによって確認することができる。

##### Options
- `-n|--name <filename>` 構成ファイルの名前を指定する



### Configuration
- 環境変数 `MKDR_CONFIG_PATH` に設定されたパスを設定フォルダとする。カレントディレクトリに `.mkdr` ディレクトリが存在する場合はそこを設定フォルダとする。
- `--config` によって設定ファイルのパスを確認できる


### .mkdrignore
- `.mkdrignore` is implemeted in the future version.




