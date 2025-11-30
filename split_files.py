import os

# Specify the path where you want to create the folders
path = ''

# Create 40 folders
for counter in range(1, 41):
    folder_name = f'output{counter}'
    folder_path = os.path.join(path, folder_name)
    os.makedirs(folder_path)