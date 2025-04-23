#!/usr/bin/env python
import re
import string
import argparse
from functools import reduce
from pypdf import PdfReader

def count_page(pwords, word):
    indices = [i+1 for i in range(len(pwords)) if word in pwords[i]]
    return indices

def word_checker(word):
    has_letter = re.compile('[a-zA-Z]')
    if has_letter.match(word) is None:
        return False
    return True

def split_words(text):
    text = re.sub(r'\s+', ' ', text).strip() # remove extra spaces
    text = re.sub(r'- ', '', text).strip() # merge hyphenated line-broken words
    text = text.translate(str.maketrans('', '', string.punctuation)) # remove punctuation
    text = re.sub(r'([a-zA-Z])[0-9]', r'\1', text) # remove trailing numbers
    return text.split(' ')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog='indexer.py',
            description='Generate an index from a PDF proof'
            )
    parser.add_argument('filename')
    parser.add_argument('-s', '--skip', type=int, default=0,
            help='Skip the first N pages')
    args = parser.parse_args()

    reader = PdfReader(args.filename)
    page_words = []
    for page in reader.pages[args.skip:]:
        words = split_words(page.extract_text())
        page_words.append(set(filter(word_checker, words)))
    all_words = reduce(lambda x,y: x|y, page_words)
    index = {w:count_page(page_words, w) for w in all_words}
    for w in all_words:
        print(w, index[w])
