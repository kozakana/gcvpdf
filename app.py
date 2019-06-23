import sys
import os
import json
import requests
import glob
from base64 import b64encode

import gcv2hocr
import hocr_pdf

ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'
LANGUAGE = os.environ.get('LANGUAGE', 'ja')
MAX_RESULTS = os.environ.get('MAX_RESULTS', 2048)
API_KEY = os.environ.get('API_KEY')
PDF_OUTPUT_NAME = os.environ.get('PDF_OUTPUT_NAME')

FILE_DIR = './files'
PDF_DIR = './pdf'

if API_KEY is None:
    print('API key has not been set')
    sys.exit(1)

file_paths = glob.glob(os.path.join(FILE_DIR, '*'))
for file_path in file_paths:
    print(file_path)
    with open(file_path, 'rb') as f:
        b64img = b64encode(f.read()).decode()
        req = {"requests": {'image': {'content': b64img}, 'features': [{'type': 'TEXT_DETECTION', 'maxResults': MAX_RESULTS}], 'imageContext': {'languageHints': LANGUAGE}}}
        response = requests.post(ENDPOINT_URL, data=json.dumps(req).encode(), params={'key': API_KEY}, headers={'Content-Type': 'application/json'}).json()
        resp = response['responses'][0] if 'responses' in response and len(response['responses']) >= 0 and "textAnnotations" in response['responses'][0] else False
        page = gcv2hocr.fromResponse(resp)

        file_name = os.path.splitext(os.path.basename(file_path))[0]
        hocr = os.path.join(FILE_DIR, (file_name + '.hocr'))
        with open(hocr, "wb") as f:
            f.write(page.render().encode('utf-8'))

pdf_name = PDF_OUTPUT_NAME or 'out.pdf'
hocr_pdf.export_pdf(FILE_DIR, 300, pdf_name)
