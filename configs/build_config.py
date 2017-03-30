from configparser import RawConfigParser
from os import path

conf_file_name = 'config.ini'

# Check if there is already a configuration file
if path.isfile(conf_file_name):
    # Create the configuration file as it does not exist yet
    cfgfile = open(conf_file_name, 'w')

    # Add content to the file
    Config = RawConfigParser()

    # Add Google Admin Credentials Section
    Config.add_section('google_admin_creds')
    # Define SCOPES group, user and drive give you most access to the user
    Config.set('google_admin_creds', 'scopes', 'https://www.googleapis.com/auth/admin.directory.group,'
                                               'https://www.googleapis.com/auth/admin.directory.user,'
                                               'https://www.googleapis.com/auth/drive')
    Config.set('google_admin_creds', 'secret', 'PATH_TO_THE_SECRETS_FILE')

    # Add the File Path Section
    Config.add_section('file_path')
    # Define a FILE_PATH
    Config.set('files_path', 'file', 'PATH_TO_FILE')
    
    # Define Groups
    Config.add_section('groups')
    Config.set('groups', 'sales', 'all@example.com,sales@example.com,employees@example.com')
    Config.set('groups', 'eng', 'all@example.com,eng@example.com,us-employees@example.com')
    Config.set('groups', 'catch_all', 'all@example.com,employees@example.com')

    Config.write(cfgfile)
    cfgfile.close()
