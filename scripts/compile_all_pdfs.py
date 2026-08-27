# -*- coding: utf-8 -*-
import os, subprocess, glob

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(REPO_ROOT, 'docs')

print('=== Compilation automatisee de tous les PDFs MatOS ===')
tex_files = glob.glob(os.path.join(DOCS_DIR, '**', '*.tex'), recursive=True)

success_count = 0
for tex in sorted(tex_files):
    folder = os.path.dirname(tex)
    filename = os.path.basename(tex)
    print(f'-> Compilation de : {filename}...')
    r1 = subprocess.run(['pdflatex', '-interaction=nonstopmode', filename], cwd=folder, capture_output=True, text=True)
    r2 = subprocess.run(['pdflatex', '-interaction=nonstopmode', filename], cwd=folder, capture_output=True, text=True)
    if r2.returncode == 0:
        pdf_name = filename.replace('.tex', '.pdf')
        pdf_path = os.path.join(folder, pdf_name)
        size_kb = os.path.getsize(pdf_path) / 1024
        print(f'   [OK] {pdf_name} genere ({size_kb:.1f} KB)')
        success_count += 1
    else:
        print(f'   [ERREUR] Echec pour {filename}')

print(f'=== Bilan : {success_count}/{len(tex_files)} documents compiles avec succes ===')
