# text_detection
Text detection on screenshots for 1C app.

Step by step guide to deploy the application
-----------------------------------
1. Open cmd/terminal in forlder and execute: git clone https://github.com/Ugggl/text_detection.git
1. Move to 'text_detection' folder
1. Donwload and install tesseract
    * For Windows:<br />
    https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-v4.1.0.20190314.exe<br />
    During the installation check ‘Additional language data’ and ‘Additional script data’
    * For macOs:<br />
    Execute in terminal: brew install tesseract --all-languages
1. Activate virtualenv in cmd/terminal
    * For Windows:<br />
    venv\Scripts\activate
    * For macOs:<br />
    . ./venv/bin/activate
1. Install required modules via pip
    pip install -r requirements.txt
1. Check ip and host of local server in app.py
    * For Windows:<br />
    127.0.0.1:30
    * For macOs:<br />
    0.0.0.0:5000
1. Only for windows: uncomment the first line of detect functioin of detect.py and change to where tesseract is installed
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'.
1. Execute: python app.py
