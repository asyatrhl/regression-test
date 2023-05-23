###################################################################################################
#
# Copyright (C) 2020-2022 Maxim Integrated Products, Inc. All Rights Reserved.
#
# Maxim Integrated Products, Inc. Default Copyright Notice:
# https://www.maximintegrated.com/en/aboutus/legal/copyrights.html
#
###################################################################################################
"""
Create the last developed code logs for base testing source
"""
import argparse
import datetime
import git
import os
import subprocess
import yaml


def joining(lst):
    """
      Join based on the ' ' delimiter
    """
    join_str = ' '.join(lst)
    return join_str

parser = argparse.ArgumentParser()
parser.add_argument('--testconf', help='Enter the config file for the test', required=True)
args = parser.parse_args()
yaml_path = args.testconf

# Open the YAML file
with open(yaml_path, 'r') as file:
    # Load the YAML content into a Python dictionary
    config = yaml.safe_load(file)

# Folder containing the files to be concatenated
# script_path = r"/home/asyaturhal/desktop/ai/last_developed/ai8x-training/scripts_test"
script_path = r"/home/asyaturhal/desktop/ai/last_developed/last_dev_source/scripts"

# Output file name and path
output_file_path = r"/home/asyaturhal/desktop/ai/last_developed/dev_scripts/last_dev_train.sh"

# global log_file_names
log_file_names = []


def dev_scripts(script_pth, output_file_pth):
    """
    Create training scripts for the last developed code
    """                                  
    with open(output_file_path, "w", encoding='utf-8') as output_file:
        for filename in os.listdir(script_path):
            # Check if the file is a text file
            if filename.startswith("train"):
                # Open the file and read its contents
                with open(os.path.join(script_path, filename), encoding='utf-8') as input_file:
                    contents = input_file.read()

                    temp = contents.split()
                    temp.insert(1, "\n")
                    i = temp.index('--epochs')
                    j = temp.index('--model')
                    k = temp.index('--dataset')

                    if '--qat-policy' in temp:
                        x = temp.index('--qat-policy')
                        temp[x+1] = "policies/qat_policy.yaml"
                    else:
                        temp.insert(-1, ' --qat-policy policies/qat_policy.yaml')

                    log_model = temp[j+1]
                    log_data = temp[k+1]

                    if log_model == "ai87imageneteffnetv2" :
                        num = temp.index("--batch-size")
                        temp[num+1] = "128"
                        
                    log_name = temp[j+1] + '-' + temp[k+1]
                    log_file_names.append(filename[:-3])

                    if log_data == "FaceID":
                        continue
                    if log_data == "VGGFace2_FaceDetection":
                        continue
                    if log_data == "ai85tinierssdface":
                        continue

                    temp[i+1] = str(config[log_data][log_model]["epoch"])

                    if '--deterministic' not in temp:
                        temp.insert(-1, '--deterministic')

                    temp.insert(-1, '--name ' + log_name)

                    data_name = temp[k+1]
                    if data_name in config and "datapath" in config[data_name]:
                        path_data = config[log_data]["datapath"]
                        temp.insert(-1, '--data ' + path_data)

                    temp.append("\n")
                    contents = joining(temp)
                    output_file.write(contents)


def dev_checkout():
    """
    Checkout the last developed code
    """
    repo_url = "https://github.com/MaximIntegratedAI/ai8x-training.git"
    local_path = r'/home/asyaturhal/desktop/ai/last_developed/last_dev_source/'

    try:
        repo = git.Repo(local_path)
    except git.exc.InvalidGitRepositoryError:
        repo = git.Repo.clone_from(repo_url, local_path, branch="develop", recursive=True)

    commit_hash = repo.heads.develop.object.hexsha
    commit_num_path = r"/home/asyaturhal/desktop/ai/last_developed/commit_number.txt"

    try:
        with open(commit_num_path, "r", encoding='utf-8') as file:
            saved_commit_hash = file.read().strip()
    except FileNotFoundError:
        saved_commit_hash = ""

    if commit_hash != saved_commit_hash:
        with open(commit_num_path, "w", encoding='utf-8') as file:
            file.write(commit_hash)
            repo.remotes.origin.pull("develop")

            dev_scripts(script_path, output_file_path)
            cmd_command = (
                "bash /home/asyaturhal/desktop/ai/"
                "last_developed/dev_scripts/last_dev_train.sh"
            )
            subprocess.run(cmd_command, shell=True, check=True)

            path_command = ("cd  /home/asyaturhal/desktop/ai/last_developed/last_dev_source/")
            subprocess.run(path_command, shell=True, check=True)

            source_path = "/home/asyaturhal/actions-runner/_work/ai8x-training/ai8x-training/logs/"
            destination_path = (
                "/home/asyaturhal/desktop/ai/last_developed/dev_logs/"
                + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            )
            subprocess.run(['mv', source_path, destination_path], check=True)

            
dev_checkout() 
