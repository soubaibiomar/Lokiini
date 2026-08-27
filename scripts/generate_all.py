# -*- coding: utf-8 -*-
import os, subprocess, glob

REPO_ROOT = 'D:/startup/MatOS'
DOCS_DIR = os.path.join(REPO_ROOT, 'docs')

def write_and_compile(folder, filename, content):
    path = os.path.join(folder, filename)
    os.makedirs(folder, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Wrote: {filename}')
    r1 = subprocess.run(['pdflatex', '-interaction=nonstopmode', filename], cwd=folder, capture_output=True, text=True)
    r2 = subprocess.run(['pdflatex', '-interaction=nonstopmode', filename], cwd=folder, capture_output=True, text=True)
    if r2.returncode == 0:
        pdf_name = filename.replace('.tex', '.pdf')
        print(f'-> [SUCCESS] {pdf_name} compiled cleanly ({os.path.getsize(os.path.join(folder, pdf_name))/1024:.1f} KB)')
    else:
        print(f'-> [ERROR] Failed to compile {filename}')
        print(r2.stdout[-500:])

