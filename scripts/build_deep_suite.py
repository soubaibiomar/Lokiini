# -*- coding: utf-8 -*-
import os, subprocess

REPO = 'D:/startup/MatOS'
DOCS = os.path.join(REPO, 'docs')

def compile_pdf(folder, filename):
    r1 = subprocess.run(['pdflatex', '-interaction=nonstopmode', filename], cwd=folder, capture_output=True, text=True)
    r2 = subprocess.run(['pdflatex', '-interaction=nonstopmode', filename], cwd=folder, capture_output=True, text=True)
    pdf_name = filename.replace('.tex', '.pdf')
    pdf_path = os.path.join(folder, pdf_name)
    if r2.returncode == 0 and os.path.exists(pdf_path):
        size_kb = os.path.getsize(pdf_path) / 1024
        print(f'-> [SUCCESS] {pdf_name} ({size_kb:.1f} KB)')
    else:
        print(f'-> [ERROR] Failed to compile {filename}')
        print(r2.stdout[-600:])

print('Initialized build_deep_suite.py')
