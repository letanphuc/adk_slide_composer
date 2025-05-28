import os

import owncloud
import six
from owncloud import HTTPResponseError, ShareInfo
import xml.etree.ElementTree as ET


class _Client(owncloud.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def share_file_with_link(self, path, **kwargs):
        perms = kwargs.get('perms', None)
        public_upload = kwargs.get('public_upload', 'false')
        password = kwargs.get('password', None)
        name = kwargs.get('name', None)

        path = self._normalize_path(path)
        post_data = {
            'shareType': self.OCS_SHARE_TYPE_LINK,
            'path': self._encode_string(path),
        }
        if (public_upload is not None) and (isinstance(public_upload, bool)):
            post_data['publicUpload'] = str(public_upload).lower()
        if isinstance(password, six.string_types):
            post_data['password'] = password
        if name is not None:
            post_data['name'] = self._encode_string(name)
        if perms:
            post_data['permissions'] = perms

        res = self._make_ocs_request(
            'POST',
            self.OCS_SERVICE_SHARE,
            'shares',
            data=post_data
        )
        if res.status_code == 200:
            tree = ET.fromstring(res.content)
            self._check_ocs_status(tree)
            data_el = tree.find('data')
            return ShareInfo(
                {
                    'id': data_el.find('id').text,
                    'path': path,
                    'url': data_el.find('url').text,
                    'token': data_el.find('token').text
                }
            )
        raise HTTPResponseError(res)


def upload_file(file_path):
    file_name = os.path.basename(file_path)
    oc = _Client('https://files.hocai.space')
    oc.login('admin', '?c<@`-DmuP[FtY.\m]U[`56$')
    oc.put_file(f'/Slides/{file_name}', file_path)
    link_info = oc.share_file_with_link(f'/Slides/{file_name}')
    return link_info.get_link()
