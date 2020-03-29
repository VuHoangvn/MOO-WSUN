import yaml

def read_yaml(filepath):
    '''
        Input a string filepath,
        output a `dict` containing the contents of the yaml file
    '''
    with open(filepath, 'r') as stream:
        data_loaded = yaml.safe_load(stream)
    return data_loaded