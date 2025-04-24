#!/usr/bin/env python
import re
import string
import argparse
from functools import reduce
from pypdf import PdfReader

def count_page(pwords, word):
    indices = [i+1 for i in range(len(pwords)) if word in pwords[i]]
    return indices

def split_words(text):
    text = text.lower() # make everything lower-case
    text = re.sub(r'\s+', ' ', text).strip() # remove extra spaces
    text = re.sub(r'-\s', '', text).strip() # merge hyphenated line-broken words
    text = re.sub(r'\W|\d', ' ', text)
    return filter(lambda x: len(x) > 1, text.split(' '))

def merge_words(pwords, awords):
    new_awords = awords.copy()
    for w in awords:
        # check if the word is a plural
        if w[-1] == 's' and w[:-1] in awords:
            new_awords.discard(w)
            for p in pwords:
                if w in p:
                    p.discard(w)
                    p.add(w[:-1])
        if w[-3:] == 'ies' and w[:-3]+'y' in awords:
            new_awords.discard(w)
            for p in pwords:
                if w in p:
                    p.discard(w)
                    p.add(w[:-3]+'y')
        if w[-2:] == 'es' and w[:-2] in awords:
            new_awords.discard(w)
            for p in pwords:
                if w in p:
                    p.discard(w)
                    p.add(w[:-2])
        # check if the word is a past tense
        if w[-2:] == 'ed' and w[:-2] in awords:
            new_awords.discard(w)
            for p in pwords:
                if w in p:
                    p.discard(w)
                    p.add(w[:-2])
        if w[-1:] == 'ed' and w[:-1] in awords:
            new_awords.discard(w)
            for p in pwords:
                if w in p:
                    p.discard(w)
                    p.add(w[:-1])
        # check if the word is a gerund
        if w[-3:] == 'ing' and w[:-3] in awords:
            new_awords.discard(w)
            for p in pwords:
                if w in p:
                    p.discard(w)
                    p.add(w[:-3])
        # check if the word is a superlative
        if w[-2:] == 'er' and w[:-2] in awords:
            new_awords.discard(w)
            for p in pwords:
                if w in p:
                    p.discard(w)
                    p.add(w[:-2])
        # check if the word is a comparative
        if w[-3:] == 'est' and w[:-3] in awords:
            new_awords.discard(w)
            for p in pwords:
                if w in p:
                    p.discard(w)
                    p.add(w[:-3])
        # check if the word is an adverb
        if w[-2:] == 'ly' and w[:-2] in awords:
            new_awords.discard(w)
            for p in pwords:
                if w in p:
                    p.discard(w)
                    p.add(w[:-2])
    return pwords, new_awords

def print_pages(pagelist):
    past_page = pagelist[0]
    pstring = str(pagelist[0])
    for p in pagelist[1:]:
        if p-1 == past_page and pstring[-1] != '-':
            pstring +=  '-'
        else:
            pstring += ','
            pstring += str(p)
        past_page = p
    return pstring

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
        page_words.append(set(words))
    all_words = reduce(lambda x,y: x|y, page_words)
    page_words, all_words = merge_words(page_words, all_words)
    index = {w:count_page(page_words, w) for w in all_words}
    for w in sorted(all_words):
        print(len(index[w]), w)
