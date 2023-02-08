import json

def readJson(file_name=None):
    """
    Read a json format file

    Parameters
    ----------
    file_name: string name with path of the file

    Returns
    -------
    data dictionary with the information included in the file
    """
    with open(file_name, "r") as file:
        data = json.load(file)
    return data

def write_json(file_path=None, data=None):
    json_object = json.dumps(data, indent=4)
    with open(file_path, "w") as outfile:
        outfile.write(json_object)
    outfile.close()