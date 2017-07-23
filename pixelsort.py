
# coding: utf-8

# In[1]:

from PIL import Image, ImageChops, ImageOps
import random
from collections import deque
from glob import glob
from os.path import join
import hashlib


def randimage(path):
    print("Path:", path)
    images = glob(join(path, "*"))
    print("images:", images)
    img = random.choice(images)
    image = Image.open(img)
    return image

def imagehash(image):
    imghash = hashlib.sha1(image.tobytes()).hexdigest()
    return imghash


def to1bit(image):
    image = image.convert("1")
    return image.convert("RGB")

def togrey(image):
    image = image.convert("L")
    return image.convert("RGB")

def quarter(image):
    image.thumbnail((image.size[0]//4, image.size[1]//4))
    return image

def half(image):
    image.thumbnail((image.size[0]//2, image.size[1]//2))
    return image

def rotate90(image):
    return image.rotate(90)


def selfmodulo(image):
    # Testing Imagechops module

    return ImageChops.add_modulo(image, image)


def sortimage(image):
    """Sort whole image."""

    fdata = list(image.getdata())
    newdata = sorted(fdata)
    new = Image.new(image.mode, image.size)
    new.putdata(newdata)

    return new



def sortlines(image):
    """sort individual lines"""

    fdata = list(image.getdata())
    newdata = []

    for x in range(0, len(fdata), image.size[0]):
        temp = fdata[x:x+image.size[0]]
        newdata.extend(sorted(temp, reverse=True))

    new = Image.new(image.mode, image.size)
    new.putdata(newdata)

    return new

def sortrandomchunks(image):
    """sort in random chunks"""

    fdata = list(image.getdata())
    newdata = []
    done = 0
    while done < len(fdata):
        n = random.randint(1, 200)
        r = random.randint(0, 1)

        temp = fdata[done:done+n]
        newdata.extend(sorted(temp, reverse=r))
        done += n

    new = Image.new(image.mode, image.size)
    new.putdata(newdata)

    return new


def funky(image):
    """Rotate red and switch channels."""
    red, green, blue = image.split()

    red = red.rotate(180)

    new = Image.merge(image.mode, (blue, red, green))
    return new


def rotatesort(image):
    """rotate and sort"""

    red, green, blue = image.split()

    red = red.rotate(180)
    bluedata = sorted(blue.getdata())
    greendata = sorted(green.getdata(), reverse=True)

    newblue = Image.new("L", image.size)
    newblue.putdata(bluedata)

    newgreen = Image.new("L", image.size)
    newgreen.putdata(greendata)

    new = Image.merge(image.mode, (newblue, red, newgreen))

    return new

# rotate a line by a random number

def rotate(line, number=None):
    """Rotate a single line <number> of steps."""
    if not number:
        number = random.randint(1, len(line))

    line = deque(line)
    line.rotate(number)

    return list(line)

def rotateall(image):
    """Rotate every single line of an image."""

    data = list(image.getdata())
    res = []
    new = Image.new(image.mode, image.size)

    for x in range(0, len(data), image.size[0]):
        temp = data[x:x+image.size[0]]
        res.extend(rotate(temp))

    new.putdata(res)

    return new

def chunk_iter(image, size=200):
    """Iterate over an images pixel data in random chunks."""
    data = list(image.getdata())
    done = 0
    while done < len(data):
        chunksize = random.randint(1, size)
        yield data[done:done+chunksize]
        done += chunksize

def average_pixels(chunk):
    """Average the pixel values of a list of pixels."""

    red = [pix[0] for pix in chunk]
    green = [pix[1] for pix in chunk]
    blue = [pix[2] for pix in chunk]

    red = sum(red) // len(red)
    green = sum(green) // len(green)
    blue = sum(blue) // len(blue)

    return [(red, green, blue)] * len(chunk)

def avg_chunks(image):
    """Iterate over image in random chunks and average values."""

    newdata = []
    for chunk in chunk_iter(image, 10):
        newdata.extend(average_pixels(chunk))

    new = Image.new(image.mode, image.size)
    new.putdata(newdata)
    return new

def all_random(image, n=3):
    funcs = [avg_chunks, rotate90, rotateall, rotatesort, funky, sortrandomchunks, sortlines, sortimage, selfmodulo, to1bit, togrey]

    for x in range(n):
        func = random.choice(funcs)
        image = func(image)
    return image

def writeimage(image, target):
    image.save(target)





