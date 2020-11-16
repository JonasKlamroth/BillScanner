from google.cloud import vision
import io
import os
import functools
import re
import more_itertools as itertools_more

def get_words(image_file):
    """Returns document bounds given an image."""
    client = vision.ImageAnnotatorClient()

    with io.open(image_file, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.document_text_detection(image=image)
    document = response.full_text_annotation

    words = []
    # Collect specified feature bounds by enumerating all document features
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    words.append(word)
    # The list `bounds` contains the coordinates of the bounding boxes.
    return words

def sort_words(words):
    words = sorted(words, key = lambda x: x.bounding_box.vertices[0].x)
    bounds = []
    lines = [[words[0]]]
    max_y = max([v.y for v in words[0].bounding_box.vertices])
    min_y = min([v.y for v in words[0].bounding_box.vertices])
    bounds = [[min_y, max_y]]
    for word in words[1:]:
        max_y = max([v.y for v in word.bounding_box.vertices])
        min_y = min([v.y for v in word.bounding_box.vertices])
        max_overlap = 0
        max_idx = -1
        for i, bound in enumerate(bounds):
            min_b = max(min_y, bound[0])
            max_b = min(max_y, bound[1])
            overlap = (max_b - min_b) / float(bound[1] - bound[0])
            if max_overlap < overlap:
                max_overlap = overlap
                max_idx = i
        if max_overlap > 0.5:
            lines[max_idx].append(word)
            bounds[max_idx][0] = min(min_b, bounds[max_idx][0])
            bounds[max_idx][1] = max(max_b, bounds[max_idx][1])
        else:
            lines.append([word])
            bounds.append([min_y, max_y])

    lines = sorted(lines, key = lambda x: x[0].bounding_box.vertices[0].y)
    return lines

def toText(word):
    block_text = ''
    for symbol in word.symbols:
        block_text = block_text + symbol.text
    return block_text

def cleanElements(elems, total):
    idx = -1
    for i, e in enumerate(elems):
        if re.search(TOTAL_KEYWORD_REGEX, e[0]):
            idx = i
            break
    elems = elems[:idx]
    total = float(total.replace(",", "."))
    s = 0
    for i, e in enumerate(elems):
        s += float(e[1])
        if s == total:
            return elems[:i]
    
    return elems


words = get_words("test4.gif")
lines = sort_words(words)
text = ''
for line in lines:
    block_text = ''
    for word in line:
        block_text += toText(word)
        block_text += ' '
    text += block_text + '\n'

text = text.lower()
print(text)

DATE_REGEX = "\d\d?\.\d\d?\.\d{4}"
POST_REGEX = "(\d\d?[,\.]\d{2})"
EURO_REGEX = "(eur|euro|€)"
TOTAL_KEYWORD_REGEX = "(total|brutto|gesa[nm]t|saldo|su[nm]{2}e)"
TOTAL_REGEX = TOTAL_KEYWORD_REGEX + " [\w\W]*?" + POST_REGEX + " " 
ELEMENT_REGEX = "^(.*?)\n?" + POST_REGEX + " " 

res = re.search(DATE_REGEX, text)
date = res.group(0)
print(date)

res = re.search(TOTAL_REGEX, text)
total = res.group(2)
print(total)

res = re.compile(ELEMENT_REGEX, re.MULTILINE)
res = res.findall(text)
elems = []
for l in res:
    elementName = l[0]
    price = l[1].replace(",", ".")
    elems.append((elementName, price))

elems = cleanElements(elems, total)
for e in elems:
    print(e[0] + ": " + e[1])