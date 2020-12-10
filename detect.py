from PIL import Image
import cv2
import json
import pytesseract
import numpy as np


def detect(path_to_image):
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'
    output = []

    # highlight bold parts of image and erase others
    img = Image.open(path_to_image)
    pixdata = img.load()

    # Make the letters bolder for easier recognition
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pixdata[x, y] == (128, 128, 128):
                pixdata[x, y] = (0, 0, 0)

                pixdata[x, y + 1] = (0, 0, 0)
                pixdata[x - 1, y] = (0, 0, 0)
                pixdata[x, y - 1] = (0, 0, 0)
                pixdata[x + 1, y] = (0, 0, 0)
            if pixdata[x, y][2] > 0:
                pixdata[x, y] = (255, 255, 255)


    # change colors to shades of grey
    img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
    height, width = img.shape

    # detect text on reformed image
    config = r'--oem 3 --psm 3'
    data = pytesseract.image_to_data(img, config=config, lang='rus')
    # left	top width	height	text
    blocks = {}

    # receive block with bold text on grey image
    for block in data.splitlines()[1:]:
        block = block.split()
        if len(block) < 12:
            continue

        if block[2] in blocks:
            # top: only if lower
            if blocks[block[2]][1] > int(block[7]):
                blocks[block[2]][1] = int(block[7])
            # width
            blocks[block[2]][2] = (int(block[6]) + int(block[8])) - blocks[block[2]][0]
            # height: only if bigger
            if blocks[block[2]][3] < int(block[9]):
                blocks[block[2]][3] = int(block[9])
            # add part of string
            blocks[block[2]][4] += ' ' + block[11]
        else:
            # init new block
            blocks[block[2]] = [int(i) for i in block[6:10]] + [block[11]]


    # cut block out of image and detect text
    img = cv2.imread(path_to_image)
    for b in list(blocks.values())[::-1]:
        # image[y:y+h, x:x+w] and add 5 pixels for each side
        y1, y2, x1, x2 = b[1] - 5, b[1] + b[3] + 5, b[0] - 5, b[0] + b[2] + 5
        cropped = img[y1:y2, x1:x2]

        # cv2.imshow("cropped", cropped)
        # cv2.waitKey(0)

        # determine window position
        window_coords = [-1, -1, -1, -1]
        # top of window
        for y in range(y1, -1, -1):
            if all(img[y, x1] != img[y - 1, x1]):
                window_coords[0] = y
                break
        # left of window
        for x in range(x1, 0, -1):
            if all(img[window_coords[0], x] != img[window_coords[0], x + 1]):
                window_coords[1] = x
                break
        # bottom of window
        for y in range(y2, height, 1):
            if all(img[y, window_coords[1]] == img[y - 1, window_coords[1]]):
                window_coords[2] = y
            else:
                break
        # right of window
        for x in range(x2, width, 1):
            if all(img[window_coords[0], x] == img[window_coords[0], x - 1]):
                window_coords[3] = x
            else:
                break

        # print(window_coords)

        # show only cropped part of window from the image
        window = img[window_coords[0]:window_coords[2], window_coords[1]:window_coords[3]]
        # cv2.imshow("window", window)
        # cv2.waitKey(0)

        # print titles (this way is not so accurate as below; the first line is title)
        line = pytesseract.image_to_string(cropped, config=config, lang='rus')
        # print(line.strip())
        # output.append(line.strip())

        # print the whole content of the window
        lines = pytesseract.image_to_string(window, config=config, lang='rus').split('\n')
        lines = [l.strip() for l in lines if l.strip()]

        if len(lines) == 0:
            continue

        output.append([line.strip(), lines[1:]])

        # repaint window position to black color
        cv2.rectangle(img, (window_coords[1], window_coords[0]), (window_coords[3], window_coords[2]), (255, 255, 255), -1)


    # refresh initial image
    img = cv2.imread(path_to_image)
    # print all text
    print('\n\nText from the whole image:')
    lines = pytesseract.image_to_string(img, config=config, lang='rus').split('\n')
    print(*[l.strip() for l in lines if l.strip()], sep='\n')

    return json.dumps(output).encode('utf8')

