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
import ipfshttpclient

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

class IpfsFileObject(file):
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


class IpfsIterator(object):
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


class IpfsStorageDriver(StorageDriver):
    """
    Ipfs Storage driver.

    >>> from libcloud.storage.drivers.dummy import DummyStorageDriver
    >>> driver = DummyStorageDriver('key', 'secret')
    >>> container = driver.create_container(container_name='test container')
    >>> container
    <Container: name=test container, provider=Dummy Storage Provider>
    >>> container.name
    'test container'
    >>> container.extra['object_count']
    0
    """

    name = "Ipfs Storage Provider"
    website = "https://ipfs.tech/"

    #def __init__(self):
    #    self._containers = {}

    def get_container(container_name=None):
        if container_name is None:
            return ipfshttpclient.connect()
        return ipfshttpclient.connect(container_name)

    def get_object(container, object_name):
        container.get(object_name)
        file = container.cat(object_name)
        return file

    def upload_object(
        object,
        container,
        object_name=None,
        extra=None,
        verify_hash=True,
        headers=None,
    ):
        return container.add_json(object)

    def upload_object_via_stream(iterator, container, object_name=None, extra=None, headers=None):
        res = container.add(iterator)
        return(res["Hash"])

    def delete_object(self, obj):
        container_name = obj.container.name
        object_name = obj.name
        obj = self.get_object(container_name=container_name, object_name=object_name)

        del self._containers[container_name]["objects"][object_name]
        return True

if __name__ == "__main__":
    import doctest

    doctest.testmod()
