# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os.path
import random
import hashlib
import io

from libcloud.utils.py3 import PY3
from libcloud.utils.py3 import b

if PY3:
    from io import FileIO as file

from libcloud.common.types import LibcloudError

from libcloud.storage.base import Object, Container, StorageDriver
from libcloud.storage.types import ContainerAlreadyExistsError
from libcloud.storage.types import ContainerDoesNotExistError
from libcloud.storage.types import ContainerIsNotEmptyError
from libcloud.storage.types import ObjectDoesNotExistError

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload
from google.oauth2.service_account import Credentials as ServiceAccountCredentials


class GoogleDriveFileObject(file):
    def __init__(self, yield_count=5, chunk_len=10):
        self._yield_count = yield_count
        self._chunk_len = chunk_len

    def read(self, size):
        i = 0

        while i < self._yield_count:
            yield self._get_chunk(self._chunk_len)
            i += 1

    def _get_chunk(self, chunk_len):
        chunk = [str(x) for x in random.randint(97, 120)]
        return chunk

    def __len__(self):
        return self._yield_count * self._chunk_len


class GoogleDriveIterator(object):
    def __init__(self, data=None):
        self.hash = hashlib.md5()
        self._data = data or []
        self._current_item = 0

    def get_md5_hash(self):
        return self.hash.hexdigest()

    def next(self):
        if self._current_item == len(self._data):
            raise StopIteration

        value = self._data[self._current_item]
        self.hash.update(b(value))
        self._current_item += 1
        return value

    def __next__(self):
        return self.next()

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass


class GoogleDriveStorageDriver(StorageDriver):
    """
    Google Drive Storage driver.
    """
    name = "Google Drive Storage Provider"
    website = "https://drive.google.com/"

    #def __init__(self):
    #    self._containers = {}

    def get_container(credentials=None):
        SCOPES = ['https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_service_account_info(credentials)
        try:
            return build('drive', 'v3', credentials=credentials)
        except HttpError as error:
            print(f'An error occurred: {error}')

    def get_object(container, object_name):
        file_id = ''
        query =  f"name='{object_name}'"

        results = container.files().list(q=query,fields="nextPageToken, files(id, name)").execute()
        items = results.get("files", [])

        for item in items:
            if item['name'] == object_name:
                print(item['id'])
                file_id = item['id']
        
        if file_id == '':
            raise ObjectDoesNotExistError(
                driver=container, value=object_name, object_name=object_name
            )
                
        return {'id': file_id, 'name': object_name, 'container': container}

    def download_object(
        obj, destination_path, overwrite_existing=False, delete_on_failure=True
    ):
        request = obj['container'].files().get_media(fileId=obj['id'])
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False

        while done is False:
            status, done = downloader.next_chunk()
            print(F'Download {int(status.progress() * 100)}.')

        with open(f"{destination_path}/{obj['name']}", "wb") as f:
            fh.seek(0)
            f.write(fh.read())

    def download_object_as_stream(obj, chunk_size=None):
        request = obj['container'].files().get_media(fileId=obj['id'])
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(F'Download {int(status.progress() * 100)}.')
        fh.seek(0)
        return fh

    def upload_object(
        #self,
        file_path,
        container,
        extra,
        object_name=None,
        verify_hash=True,
        headers=None,
    ):
        file = open(file_path, 'rb')

        if(object_name is None):
            object_name = file_path.split("/")[-1]

        media = MediaFileUpload(object_name, mimetype=extra['content_type'])

        file_metadata = {'name': object_name, 'parents':None}
        file = container.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(F'Uploaded Succesfully! File ID: {file.get("id")}')

    def upload_object_via_stream(
        iterator,
        container,
        object_name,
        extra=None,
        headers=None,
        ex_storage_class=None,
    ):
        media = MediaIoBaseUpload(fd=iterator, mimetype="application/octet-stream", resumable=True)

        file_metadata = {'name': object_name, 'parents':None}
        file = container.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(F'Uploaded Succesfully! File ID: {file.get("id")}')

        

    def delete_object(
        #self, 
        obj
    ):
        file_id = obj['id']
        obj['container'].files().delete(fileId=file_id).execute()
        print(f'File with ID: {file_id} was deleted successfully')


if __name__ == "__main__":
    import doctest

    doctest.testmod()
