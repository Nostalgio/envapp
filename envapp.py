import sys, json
import spur, requests


def get_env_vars(username=None, password=None):
    """
    Will connect to envapp.win with credentials.
    And will download the env variables.
    """
    return {
        'ENV_FILE': '/home/web/envapp/env/bin/activate',
        'RESTART_SCRIPT': 'sudo service apache2 restart',
    }


def add_env_vars(shell, env_file, env_dict):
    with shell.open(env_file, "a") as file:
        for key, value in env_dict.items():
            env_line = "export {0}={1}\n".format(key, value)
            file.write(env_line)


def set_env_vars(shell=None, env_vars={}):
    """
    Updates the env vars by modifying the file based on key 'ENV_FILE'.
    """
    print("Setting environment for {}".format(shell._hostname))
    print(env_vars.get('ENV_FILE'))
    with shell.open(env_vars.pop('ENV_FILE', '.env'), "a") as file:
        for key, value in env_vars.items():
            env_line = "export {0}={1}\n".format(key, value)
            file.write(env_line)


script_location = sys.argv[0]
env = str(sys.argv[1])
config_file = str(sys.argv[2])

print("Please enter your EnvApp.WIN credentials")
username = input("Username: ")
password = input("Password: ")

print("Please wait...connecting to servers.")

env_vars = get_env_vars(username=username, password=password)

# Set host list
host_list = []
with open(config_file, 'r') as config_content:
    data = json.loads(config_content.read())
    host_list = data[env]

for host in host_list:
    hostname = host.get('hostname', None)
    username = host.get('username', None)
    private_key_file = host.get('private_key_file', None)
    restart_script = env_vars.pop('RESTART_SCRIPT', None)

    shell = spur.SshShell(hostname=hostname, username=username,
            private_key_file=private_key_file,
            missing_host_key=spur.ssh.MissingHostKey.accept)

    set_env_vars(shell=shell, env_vars=env_vars)

    if restart_script is not None:
        restart_args = restart_script.split(' ')
        shell.run(restart_args)
