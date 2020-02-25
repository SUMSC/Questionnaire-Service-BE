import yaml

with open('./router.yaml') as yaml_fd:
    router = yaml.load(yaml_fd.read())
print(router)
