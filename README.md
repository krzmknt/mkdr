# mkdr
`mkdr` organize/reorganize files and directories according to a yaml file `organization.yml`

```yaml
- README.md
- Dockerfile
- src:
  - static:
    - index.html
    - style.css
  - js:
    - common.js
  - log:
    - access.log
    - error.log
```

[option]
  --force | -f : If the designated objects are already exist, first remove it and then newly remake the objects.
  --export | -e : Generate an `organization.yml` file according to the existing current directory.


