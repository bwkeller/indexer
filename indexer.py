#!/usr/bin/env python
import re
import string
import argparse
from functools import reduce
from pypdf import PdfReader

def count_page(pwords, word):
    indices = [i+1 for i in range(len(pwords)) if word in pwords[i]]
    return sorted(indices)

def split_words(text):
    text = re.sub(r'\s+', ' ', text).strip() # remove extra spaces
    text = re.sub(r'-\s', '', text).strip() # merge hyphenated line-broken words
    text = re.sub(r'\W|\d', ' ', text)
    return list(filter(lambda x: len(x) > 1, text.split(' ')))

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

def parse_skipstr(skipstr):
    skiplist = []
    for s in skipstr.split(','):
        if '-' in s:
            start, end = s.split('-')
            start = int(start)
            end = int(end)
            skiplist += list(range(start, end+1))
        else:
            skiplist.append(int(s))
    return skiplist

def pretty_index(pagelist):
    def counter(left, right):
        leftmost = left.split(',')[-1]
        rangecount = str.count(leftmost, '.')
        leftint = int(leftmost.split('.')[0])
        rightint = int(right)
        if leftint+1+rangecount == rightint:
            return f'{left}.{right}'
        else:
            return f'{left},{right}'
    idxstr = ''
    for c in reduce(counter, map(str, pagelist)).split(','):
        splitted = c.split('.')
        if splitted[0] == splitted[-1]:
            idxstr += f'{splitted[0]},'
        else:
            idxstr += f'{splitted[0]}-{splitted[-1]},'
    return idxstr[:-1]

def write_docx(index):
    from docx import Document
    doc = Document()
    for w in sorted(index.keys(), key=str.casefold):
        doc.add_paragraph(f'{w}: {pretty_index(index[w])}')
    doc.save('index.docx')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog='indexer.py',
            description='Generate an index from a PDF proof'
            )
    parser.add_argument('filename')
    parser.add_argument('-s', '--skip', type=str, default='0',
            help='Skip the first N pages')
    parser.add_argument('-c', '--count', action='store_true',
            help="Don't generate an index, instead list all words with the number of pages they appear on")
    parser.add_argument('-d', '--docx', action='store_true',
            help="Generate a MS word .docx file with the index")
    parser.add_argument('-l', '--list', type=str,
            help='List of words to include in the index (otherwise include everything)')
    args = parser.parse_args()

    reader = PdfReader(args.filename)
    page_words = []
    cap_words = set()
    if args.skip:
        skiplist = parse_skipstr(args.skip)
    else:
        skiplist = []
    for page in reader.pages:
        if page.page_number in skiplist:
            continue
        words = split_words(page.extract_text())
        page_words.append(set([w.lower() for w in words]))
        cap_words |= set(words)
    all_words = reduce(lambda x,y: x|y, page_words)
    page_words, all_words = merge_words(page_words, all_words)
    if args.list:
        list_words = set(open(args.list).read().splitlines())
        all_words = all_words & list_words
    index = {w:count_page(page_words, w.lower()) for w in all_words}
    for w in cap_words:
        if w.lower() not in cap_words and w.lower() in index.keys():
            index[w] = index[w.lower()]
            del index[w.lower()]
    if args.count:
        counts = {}
        for w in sorted(index.keys()):
            counts[w] = len(index[w])
        for w in sorted(counts, key=counts.get, reverse=True):
            print(f'{counts[w]} {w}')
    elif args.docx:
        write_docx(index)
    else:
        for w in sorted(index.keys(), key=str.casefold):
            print(f'{w}: {pretty_index(index[w])}')