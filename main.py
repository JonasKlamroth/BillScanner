from google.cloud import vision
import io
import os
import functools
import re
import itertools


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
    total = total.replace(",", ".")
    total = float(total)

    idx = -1
    minprice = 2000000000.0
    for i, e in enumerate(elems):
        if float(e[1]) > 0:
            minprice = min(minprice, float(e[1]))
        if re.search(TOTAL_KEYWORD_REGEX, e[0]):
            idx = i
            break

    elems = elems[:idx]
    sumPrice = round(sum([float(y[1]) for y in elems]), 2)
    if sumPrice <= total:
        if sumPrice < total:
            print("could not figure out correct list of elements")
        return elems
    diff = round(sumPrice - total, 2)
    upperBound = int(max(min(int(sumPrice/minprice), len(elems)/3), 5))

    for i in range(upperBound):
        powset = itertools.combinations(elems, i)
        elems1 = list(filter(lambda x: round(sum([float(y[1]) for y in x]), 2) == diff, powset))
        if len(elems1) == 1:
            for e in elems1[0]:
                elems.remove(e)
            return elems
    print("couldt not figure out correct elemnt list")
    return elems

words = get_words("test6.jpg")
lines = sort_words(words)
textLines = []
for line in lines:
    block_text = ''
    for word in line:
        block_text += toText(word)
        block_text += ' '
    textLines.append(block_text.lower())

DATE_REGEX = "\d\d?\.\d\d?\.\d{2}(\d{2})?"
POST_REGEX = "(-?\d\d?[,\.]\d{2})"
EURO_REGEX = "(eur|euro|€)"
TOTAL_KEYWORD_REGEX = "(total|brutto|gesa[nm]t|saldo|su[nm]{2}e)"
TOTAL_REGEX = TOTAL_KEYWORD_REGEX + " [\w\W]*?" + POST_REGEX
ELEMENT_REGEX = "([\w\W]*?)" + POST_REGEX + "(?!" + POST_REGEX + ").*?"

elems = []
date = None
total = None
for text in textLines:
    print(text)
    res = re.search(DATE_REGEX, text)
    if res and not date:
        date = res.group(0)

    res = re.search(TOTAL_REGEX, text)
    if res and not total:
        total = res.group(2)


    res = re.compile(POST_REGEX)
    res = res.findall(text)
    if res:
        price = res[-1]
        elementName = text[:text.rfind(price)]
        price = float(price.replace(",", "."))
        elems.append((elementName, price))

store = textLines[0]

print("")
print(date)
print(store)
print(total)
elems = cleanElements(elems, total)
for e in elems:
    print(e[0] + ": " + str(e[1]))