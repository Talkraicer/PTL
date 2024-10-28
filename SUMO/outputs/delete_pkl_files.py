import os
path_to_delete_from = "network_toy"
paths = [path_to_delete_from]
while os.path.isdir(paths[0]):
    new_paths = []
    for directory in paths:
        files = os.listdir(directory)
        dir_paths = [os.path.join(directory, file) for file in files if not file.endswith(".net.xml")]
        new_paths += dir_paths
    paths = new_paths

for path in paths:
    if path.endswith(".pkl"):
        os.remove(path)

