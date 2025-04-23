#!/usr/bin/env python3
import argparse
from functools import reduce
from pypdf import PdfReader

def count_page(pwords, word):
    indices = [i for i in range(len(pwords)) if word in pwords[i]]
    return indices

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog='indexer.py',
            description='Generate an index from a PDF proof'
            )
    parser.add_argument('filename')
    args = parser.parse_args()

    reader = PdfReader(args.filename)
    N_page = len(reader.pages)
    page_words = []
    for page in reader.pages:
        text = page.extract_text()
        page_words.append(set(text.replace(r'\n', ' ').split(' ')))
    all_words = reduce(lambda x,y: x|y, page_words)
    index = {w:count_page(page_words, w) for w in all_words}
    for w in all_words:
        print(w, index[w])
