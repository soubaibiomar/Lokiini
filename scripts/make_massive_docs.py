# -*- coding: utf-8 -*-
import os, subprocess, glob

REPO = 'D:/startup/MatOS'
DOCS = os.path.join(REPO, 'docs')

def compile_doc(folder, tex_name):
    print(f'=== Compiling {tex_name} in {os.path.relpath(folder, REPO)} ===')
    r1 = subprocess.run(['pdflatex', '-interaction=nonstopmode', tex_name], cwd=folder, capture_output=True, text=True)
    r2 = subprocess.run(['pdflatex', '-interaction=nonstopmode', tex_name], cwd=folder, capture_output=True, text=True)
    pdf_name = tex_name.replace('.tex', '.pdf')
    pdf_path = os.path.join(folder, pdf_name)
    if r2.returncode == 0 and os.path.exists(pdf_path):
        size_kb = os.path.getsize(pdf_path) / 1024
        print(f'-> [SUCCESS] {pdf_name} ({size_kb:.1f} KB)')
    else:
        print(f'-> [ERROR] Failed to compile {tex_name}')
        print(r2.stdout[-600:])

