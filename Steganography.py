#  This is a Python Program whose objective is to encode and decode text in/from an image

import PIL.Image
import os
import shutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                            QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
import sys


# Converting text into 8-bit binary from using ASCII value of characters
def genBinary(data):
    # Function generates binary codes
    list = []
    for i in data:
        list.append(format(ord(i), '08b'))
    return list


def modPixel(pix, data):
    #pixels are modified according to the binary list version of the encoded text/data
    datalist = genBinary(data)
    lengthdata = len(datalist)
    imgdata = iter(pix)

    for i in range(lengthdata):
        # Taking 3 pixels at a time
        pix = [value for value in imgdata.__next__()[:3] +
               imgdata.__next__()[:3] +
               imgdata.__next__()[:3]]

        # Pixel value are made odd for 1 and even for 0
        for j in range(0, 8):
            if (datalist[i][j] == '0') and (pix[j] % 2 != 0):
                if (pix[j] % 2 != 0):
                    pix[j] -= 1
            elif (datalist[i][j] == '1') and (pix[j] % 2 == 0):
                pix[j] -= 1

        # Eighth pixel is used to check whether the generated encoded data needs to be read or not
        if (i == lengthdata - 1):
            if (pix[-1] % 2 == 0):
                pix[-1] -= 1
        else:
            if (pix[-1] % 2 != 0):
                pix[-1] -= 1

        pix = tuple(pix)
        yield pix[0:3]
        yield pix[3:6]
        yield pix[6:9]


def encoder(newimg, data):
    w = newimg.size[0]
    (x, y) = (0, 0)

    for pixel in modPixel(newimg.getdata(), data):
        # Inserting modified pixels in the new image
        newimg.putpixel((x, y), pixel)
        if (x == w - 1):
            x = 0
            y += 1
        else:
            x += 1


# Encoding data/text into image
def encode(data):
    if not data:
        raise ValueError('Data is empty')
        
    file_path, _ = QFileDialog.getOpenFileName(
        None,
        "Select Image File",
        "",
        "Image Files (*.png *.jpg);;All Files (*.*)"
    )
    
    if not file_path:
        return
        
    file_name = os.path.basename(file_path)
    file_ext = os.path.splitext(file_name)[1]
    
    image = PIL.Image.open(file_path, 'r')
    newimg = image.copy()
    encoder(newimg, data)
    
    new_img_name = os.path.splitext(file_name)[0] + "-encoded.png"
    newimg.save(new_img_name, "PNG")
    return new_img_name


# Decoding the data from given image from file explorer
def decode():
    file_path, _ = QFileDialog.getOpenFileName(
        None,
        "Select Encoded Image",
        "",
        "PNG Files (*.png);;All Files (*.*)"
    )
    
    if not file_path:
        return None
        
    image = PIL.Image.open(file_path, 'r')
    data = ''
    imgdata = iter(image.getdata())

    while True:
        pixels = [value for value in imgdata.__next__()[:3] +
                 imgdata.__next__()[:3] +
                 imgdata.__next__()[:3]]
        # string of binary data
        binstr = ''

        for i in pixels[:8]:
            if (i % 2 == 0):
                binstr += '0'
            else:
                binstr += '1'

        data += chr(int(binstr, 2))
        if (pixels[-1] % 2 != 0):
            return data


class SteganographyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Steganography Tool")
        self.setMinimumSize(600, 400)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
        """)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Steganography Tool")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Encode section
        encode_label = QLabel("Enter text to encode:")
        layout.addWidget(encode_label)
        
        self.encode_text = QTextEdit()
        self.encode_text.setPlaceholderText("Enter your message here...")
        self.encode_text.setMaximumHeight(100)
        layout.addWidget(self.encode_text)
        
        encode_btn = QPushButton("Encode Message")
        encode_btn.clicked.connect(self.encode_message)
        layout.addWidget(encode_btn)

        # Separator
        separator = QLabel("")
        separator.setStyleSheet("background-color: #ccc; min-height: 1px;")
        layout.addWidget(separator)

        # Decode section
        decode_label = QLabel("Decode message from image:")
        layout.addWidget(decode_label)
        
        decode_btn = QPushButton("Decode Image")
        decode_btn.clicked.connect(self.decode_message)
        layout.addWidget(decode_btn)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

    def encode_message(self):
        text = self.encode_text.toPlainText()
        if not text:
            QMessageBox.warning(self, "Error", "Please enter text to encode")
            return
            
        try:
            new_img_name = encode(text)
            if new_img_name:
                self.status_label.setText(f"Message encoded successfully! Saved as: {new_img_name}")
                self.status_label.setStyleSheet("color: green;")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.status_label.setText("Encoding failed!")
            self.status_label.setStyleSheet("color: red;")

    def decode_message(self):
        try:
            decoded_text = decode()
            if decoded_text:
                msg = QMessageBox()
                msg.setWindowTitle("Decoded Message")
                msg.setText(decoded_text)
                msg.setStyleSheet("QLabel{min-width: 400px;}")
                msg.exec()
                self.status_label.setText("Message decoded successfully!")
                self.status_label.setStyleSheet("color: green;")
            else:
                self.status_label.setText("No message found in image")
                self.status_label.setStyleSheet("color: orange;")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.status_label.setText("Decoding failed!")
            self.status_label.setStyleSheet("color: red;")


def main():
    app = QApplication(sys.argv)
    window = SteganographyApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()