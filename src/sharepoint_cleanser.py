import os
import sys
import json
import requests
import time
import json
import datetime
from typing import List, Text
from salure_helpers import TaskScheduler, GetConnector

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(basedir)
import config


class CleanSharepoint():

    def __init__(self):
        self.data_output_folder = '{}{}'.format(basedir, config.data_dir['output_dir_logging'])
        if not os.path.isdir(self.data_output_folder):
            os.makedirs(self.data_output_folder)
        self.site = config.sharepoint['site']
        self.sharepoint_directory = self.data_output_folder
        self.token_directory = f'{basedir}{config.data_dir["tokens"]}'
        self.document_library = config.sharepoint['document_library']
        self.tenantid = config.sharepoint['tenant_id']
        self.clientid = config.sharepoint['client_id']
        self.clientsecret = config.sharepoint['client_secret']
        self.json_subset = config.sharepoint['json_subset']
        self.folder_list = []
        self.file_list = []

    def get_access_token(self):
        if not os.path.exists(self.token_directory):
            os.makedirs(self.token_directory)
        if not os.path.exists(f'{self.token_directory}/tokens_sharepoint.json'):
            refresh_token = input('refresh_token: ')
        else:
            with open(f'{self.token_directory}/tokens_sharepoint.json', 'r') as file:
                tokens = file.read()
                tokens = json.loads(tokens)
                refresh_token = tokens['refresh_token']
        url_tokens = f'https://login.microsoftonline.com/{self.tenantid}/oauth2/token'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        body = {
                "grant_type": "refresh_token",
                "client_id": self.clientid,
                "client_secret": self.clientsecret,
                "refresh_token": refresh_token
                }
        response = requests.post(url=url_tokens, headers=headers, data=body)
        token = response.json()
        if 200 <= response.status_code < 300:
            with open(f'{self.token_directory}/tokens_sharepoint.json', 'w') as f:
                json.dump(token, f)
        else:
            raise Exception(f'Got status_code {response.status_code} with {response.text} from sharepoint')
        return token['access_token']

    def run_all(self):
        site = config.sharepoint['site']
        site_name = config.sharepoint['site_name']
        site_ids = self.fetch_site_id(site, site_name)
        drive_id = self.fetch_drive(site_ids)
        self._fetch_drive_folder(site_ids, drive_id)
        self.delete_stale_files(site_ids, drive_id)
        if len(self.file_list) > 0:
            self.upload_log(site_ids, drive_id)
        else:
            print (f"There's no stale files now!")
        # self.finish_task()

    def fetch_site_id(self, site, site_name):
        access_token = self.get_access_token()
        headers = {'Authorization': f'Bearer {access_token}'}
        is_read = requests.get(
            f"https://graph.microsoft.com/v1.0/sites/{site}:/sites/{site_name}",
            headers=headers)
        messages = is_read.json()
        site_ids = messages['id']
        return site_ids

    def fetch_drive(self, site_ids):
        access_token = self.get_access_token()
        headers = {'Authorization': f'Bearer {access_token}'}
        is_read = requests.get(
            f"https://graph.microsoft.com/v1.0/sites/{site_ids}/drives",
            headers=headers)

        messages = is_read.json()['value']
        for message in messages:
            if message['name'] == 'Documents':
                drive_id = message['id']
        return drive_id

current_time = datetime.datetime.now()
print (f"starting from {current_time}")
cleanser = CleanSharepoint()
cleanser.run_all()
print (f"End the process at {(datetime.datetime.now() - current_time).total_seconds()/60} minutes")
