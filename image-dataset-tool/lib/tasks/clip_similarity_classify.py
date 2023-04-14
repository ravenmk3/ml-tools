import os
import shutil
import sys

import clip
import numpy as np
import torch
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

from lib.common.file import scan_image_files


class ClipSimilarityClassifier:

    # https://github.com/openai/clip

    def __init__(self, sample_root: str):
        model, preprocess = clip.load("ViT-B/32", device='cpu')
        self.model = model
        self.preprocess = preprocess
        self.sample_features = self._load_samples(sample_root)

    def _extract_feature(self, file: str) -> np.ndarray:
        image = self.preprocess(Image.open(file).convert('RGB')).unsqueeze(0)
        with torch.no_grad():
            image_features = self.model.encode_image(image)
        return image_features[0].detach().numpy()

    def _load_samples(self, sample_root: str):
        sample_features = {}
        for name in os.listdir(sample_root):
            item_path = os.path.join(sample_root, name)
            if not os.path.isdir(item_path):
                continue
            features = []
            for file in os.listdir(item_path):
                file_path = os.path.join(item_path, file)
                if not os.path.isfile(file_path):
                    continue
                feature = self._extract_feature(file_path)
                features.append(feature)
            sample_features[name] = features
        return sample_features

    def predict(self, input_file: any) -> list[tuple[str, float]]:
        feature = self._extract_feature(input_file)
        preds = []
        for name, features in self.sample_features.items():
            sim = cosine_similarity(features, [feature]).reshape((-1,)).mean()
            preds.append((name, sim))
        return sorted(preds, key=lambda x: x[1], reverse=True)


def run_clip_similarity_classify(sample_root: str, input_dir: str, output_dir: str, move_file: bool = False):
    print('loading CLIP model')
    clf = ClipSimilarityClassifier(sample_root)
    files = scan_image_files(input_dir)

    if move_file:
        handle_fn = shutil.move
    else:
        handle_fn = shutil.copy

    pbar = tqdm(files, file=sys.stdout, desc='processing')
    for file in pbar:
        preds = clf.predict(file)
        pred_name, pred_sim = preds[0]
        dst_dir = os.path.join(output_dir, pred_name)
        dst_path = os.path.join(dst_dir, os.path.basename(file))
        handle_fn(file, dst_path)
