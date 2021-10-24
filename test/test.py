ijk;mport yaml

with open('mkdrcompose.yml') as f:
    yml = yaml.load(f, Loader=yaml.SafeLoader)

print(isinstance(yml,list))

