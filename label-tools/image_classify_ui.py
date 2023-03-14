import os
import random
import shutil

import click
import gradio as gr
from PIL import Image

# requirements: pillow, gradio, click


def is_image_file(filename: str) -> bool:
    filename = filename.lower()
    for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
        if filename.endswith(ext):
            return True
    return False


def get_image_files_recursively(dir_path: str) -> list[str]:
    result = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if not is_image_file(file):
                continue
            result.append(os.path.join(root, file))
    return result


def read_label_file(filename: str) -> list[str]:
    with open(filename, 'r') as fp:
        lines = [line.strip() for line in fp.readlines()]
    return [line for line in lines if len(line) > 0 and line[0] != '#']


def make_classify_fn(files: list[str], label_dir: str):
    def fn(idx: int):
        if idx is None:
            next_idx = 0
            next_img = Image.open(files[next_idx])
            return next_img, next_idx, None

        file = files[idx]
        dst_file = os.path.join(label_dir, os.path.basename(file))
        os.makedirs(label_dir, exist_ok=True)
        shutil.copy(file, dst_file)
        print(file, '==>', dst_file)

        next_idx = idx + 1
        next_file = files[next_idx]
        next_img = Image.open(next_file)
        return next_img, next_idx, None

    return fn


def init_app(input_dir: str, output_dir: str, label_file: str, shuffle: bool = False) -> gr.Blocks:
    files = get_image_files_recursively(input_dir)
    labels = read_label_file(label_file)
    if shuffle:
        random.shuffle(files)

    with gr.Blocks() as app:
        g_idx = gr.State(value=None)
        with gr.Row():
            with gr.Column(scale=2):
                g_img = gr.Image()
                g_txt = gr.Textbox()
            with gr.Column(scale=1):
                for label in labels:
                    btn = gr.Button(label)
                    label_dir = os.path.join(output_dir, label)
                    fn = make_classify_fn(files, label_dir)
                    btn.click(fn=fn, inputs=[g_idx], outputs=[g_img, g_idx, g_txt])
    return app


@click.command()
@click.option('--input', required=True)
@click.option('--output', required=True)
@click.option('--labels', required=True)
@click.option('--shuffle', default=False, show_default=True)
def main(input: str, output: str, labels: str, shuffle: bool):
    app = init_app(input, output, labels, shuffle)
    app.launch()


if __name__ == '__main__':
    main()
