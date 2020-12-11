from PIL import Image
import cv2
import json
import pytesseract
import numpy as np


def detect(path_to_image):
    # pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    output = []

    # highlight bold parts of image and erase others
    # выделяем жирные и большие шрифты и стираем тонкие и мелкие
    img = Image.open(path_to_image)
    pixdata = img.load()

    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pixdata[x, y] == (128, 128, 128, 255) or pixdata[x, y] == (128, 128, 128):
                pixdata[x, y] = (0, 0, 0)

                pixdata[x + 1, y] = (0, 0, 0)
                pixdata[x, y + 1] = (0, 0, 0)
                pixdata[x - 1, y] = (0, 0, 0)
                pixdata[x, y - 1] = (0, 0, 0)
            elif pixdata[x, y][2] > 0:
                pixdata[x, y] = (255, 255, 255)

    # change colors to shades of grey
    # меняем цветовую палитру на серую
    img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
    height, width = img.shape

    # detect text on processed image
    # распознаем текст на обработанном изображении
    config = r'--oem 3 --psm 3'
    data = pytesseract.image_to_data(img, config=config, lang='rus')

    # receive block with bold text on grey image
    # собираем блоки оставшшегося жирного текста на черно-белом изображении
    blocks = {}
    for block in data.splitlines()[1:]:
        block = block.split()
        if len(block) < 12:
            continue

        # добавляем содержимое в блок и корректируем координаты
        if block[2] in blocks:
            # top: only if lower
            # верх: только если координата ниже занесенной
            if blocks[block[2]][1] > int(block[7]):
                blocks[block[2]][1] = int(block[7])

            # width
            # ширина
            blocks[block[2]][2] = (int(block[6]) + int(block[8])) - blocks[block[2]][0]

            # height: only if bigger
            # высота: только если координата больше занесенной
            if blocks[block[2]][3] < int(block[9]):
                blocks[block[2]][3] = int(block[9])

            # add part of string
            # добавляем часть строки в блок
            blocks[block[2]][4] += ' ' + block[11]
        else:
            # init new block
            # добавляем новый блок в массив блоков, если его там еще не было
            blocks[block[2]] = [int(i) for i in block[6:10]] + [block[11]]

    # detect text and cut block out of image
    # распознаем текст и вырезаем уже распознанные блоки с изображения
    img = cv2.imread(path_to_image)
    for b in list(blocks.values())[::-1]:
        # image[y:y+h, x:x+w] and add 5 pixels for left, right, and bottom side
        # image[y:y+h, x:x+w] и добавлеям по 5 пискелей сверху, снизу и справа
        y1, y2, x1, x2 = b[1] - 5, b[1] + 30 - 5, b[0], b[0] + b[2] + 5

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

        # crop window
        # вырезаем окно
        window = img[window_coords[0]:window_coords[2], window_coords[1]:window_coords[3]]

        if len(blocks) == 1:
            # cut title of big window
            # вырезаем заголовок большого окна
            cropped = img[y1:y2, x1:x2]
        else:
            # cut title of small windows and big ones
            # вырезаем заголовки больших и маленьких окон
            cropped = img[window_coords[0]:y2,
                      min(x1, window_coords[1] + 20 + (60 * int(bool(output)))):window_coords[3] - 120]

        # detect text on title and print it
        # распознаем текст на заголовке и выводим его в консоль
        line = pytesseract.image_to_string(cropped, config=config, lang='rus')
        print(line.strip())

        # detect the whole content of the window
        # распознаем все содержимое окна
        lines = pytesseract.image_to_string(window, config=config, lang='rus').split('\n')
        lines = [l.strip() for l in lines if l.strip()]

        # if there is no content, continue looking for windows
        # если содержимое пусто то ничего не выводим, ищем окна дальше
        if len(lines) == 0:
            continue

        # add window content to output
        # добавляем содержимое окна в вывод
        output.append([line.strip(), lines[1:]])

        # repaint window position with white rectangle
        # замазываем место окна белым прямоугольником
        cv2.rectangle(img, (window_coords[1], window_coords[0]), (window_coords[3], window_coords[2]), (255, 255, 255), -1)

    # print content of the whole image once
    # выводим содержимое всего изображения один разом
    # img = cv2.imread(path_to_image)
    # print('\n\nText from the whole image:')
    # lines = pytesseract.image_to_string(img, config=config, lang='rus').split('\n')
    # print(*[l.strip() for l in lines if l.strip()], sep='\n')

    # return content of windows in json
    # возвращаем содержимое окон через json
    return json.dumps(output).encode('utf8')


