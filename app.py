import sys
import os
import shutil
import json
import requests
import glob
from base64 import b64encode
from pdf2image import convert_from_path

import gcv2hocr
import hocr_pdf

ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'
LANGUAGE = os.environ.get('LANGUAGE', 'ja')
MAX_RESULTS = os.environ.get('MAX_RESULTS', 2048)
API_KEY = os.environ.get('API_KEY')
PDF_OUTPUT_NAME = os.environ.get('PDF_OUTPUT_NAME')

TMP_DIR = './tmp'
INPUT_DIR = './input'
OUTPUT_DIR = './output'

if API_KEY is None:
    print('API key has not been set')
    sys.exit(1)

def input_files_and_dirs(paths):
    origin_pdfs = []
    images_dirs = []
    for path in paths:
        if os.path.isfile(path):
            _, ext = os.path.splitext(path)
            if ext.lower() == '.pdf':
              origin_pdfs.append(path)
        elif os.path.isdir(path):
            images_dirs.append(path)
    return origin_pdfs, images_dirs

def get_images_path(images_dir):
    files = glob.glob(os.path.join(images_dir, '*'))
    files.sort()
    return files

def ocr_images(images_paths, output_name):
    path = os.path.dirname(images_paths[0])
    for images_path in images_paths:
        with open(images_path, 'rb') as f:
            b64img = b64encode(f.read()).decode()
            req = {'requests': {'image': {'content': b64img}, 'features': [{'type': 'TEXT_DETECTION', 'maxResults': MAX_RESULTS}], 'imageContext': {'languageHints': LANGUAGE}}}
            response = requests.post(ENDPOINT_URL, data=json.dumps(req).encode(), params={'key': API_KEY}, headers={'Content-Type': 'application/json'}).json()
            resp = response['responses'][0] if 'responses' in response and len(response['responses']) >= 0 and 'textAnnotations' in response['responses'][0] else False
            page = gcv2hocr.fromResponse(resp)

            file_name = os.path.splitext(os.path.basename(images_path))[0]
            #hocr = os.path.join(INPUT_DIR, (file_name + '.hocr'))
            hocr = os.path.join(path, (file_name + '.hocr'))
            with open(hocr, "wb") as f:
                f.write(page.render().encode('utf-8'))

    pdf_name = PDF_OUTPUT_NAME or output_name
    hocr_pdf.export_pdf(path, 300, pdf_name)

def convert_pdf_to_images(pdf_path):
    tmp_paths = glob.glob(os.path.join(TMP_DIR, '*.jpg'))
    for tmp_path in tmp_paths:
        os.remove(tmp_path)
    images = convert_from_path(pdf_path)
    for idx, image in enumerate(images):
        image.save((TMP_DIR + '/tmp{}.jpg').format(idx), 'JPEG')
    return glob.glob(os.path.join(TMP_DIR, '*.jpg'))

input_paths = glob.glob(os.path.join(INPUT_DIR, '*'))
pdf_files, images_dirs = input_files_and_dirs(input_paths)

for pdf_file in pdf_files:
    images_paths = convert_pdf_to_images(pdf_file)
    ocr_images(images_paths, 'tmp.pdf')

for images_dir in images_dirs:
    output_name = os.path.basename(images_dir) + '.pdf'
