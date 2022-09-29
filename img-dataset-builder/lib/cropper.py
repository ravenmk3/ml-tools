import logging
import os
from typing import List

import requests
from PIL import Image


class ImageCropper:

    def __init__(self,
                 desired_classes: List[int] = None,
                 src_dir: str = '.data/images',
                 dst_dir: str = '.data/images-cropped'):
        self.desired_classes = desired_classes
        self.src_dir = src_dir
        self.dst_dir = dst_dir

    def det_objects(self, filepath: str) -> dict:
        with open(filepath, 'rb') as f:
            data = f.read()
        form_data = [
            ('file', ('image.jpg', data, 'image/jpeg'))
        ]
        url = 'http://localhost:8001/infer/file'
        resp = requests.post(url, files=form_data)
        return resp.json()

    def run(self):
        for cls_name in os.listdir(self.src_dir):
            cls_src_dir = os.path.join(self.src_dir, cls_name)
            cls_dst_dir = os.path.join(self.dst_dir, cls_name)
            os.makedirs(cls_dst_dir, exist_ok=True)
            for file_name in os.listdir(cls_src_dir):
                src_file_path = os.path.join(cls_src_dir, file_name)
                resp = self.det_objects(src_file_path)
                if resp['code'] != 'ok':
                    continue
                name, ext = os.path.splitext(file_name)
                objects = resp['data'][0]['objects']
                img = Image.open(src_file_path)
                n = 0
                for i, obj in enumerate(objects):
                    obj_cls = obj['class']
                    if self.desired_classes and obj_cls not in self.desired_classes:
                        continue
                    n += 1
                    obj_num = str(n).rjust(2, '0')
                    cls_num = str(obj_cls).rjust(2, '0')
                    dst_file_name = f'{name}_{obj_num}_{cls_num}{ext}'
                    dst_file_path = os.path.join(cls_dst_dir, dst_file_name)
                    obj_box = (obj['xmin'], obj['ymin'], obj['xmax'], obj['ymax'])
                    obj_img = img.crop(obj_box)
                    obj_img.save(dst_file_path, 'png')
                    logging.info('save: %s', dst_file_path)
