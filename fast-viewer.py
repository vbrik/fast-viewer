#!/usr/bin/env python
"""Fast image viewer"""
from __future__ import division
from __future__ import print_function
import sys
import os
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtGui import *
import time
from collections import namedtuple, OrderedDict
import PIL.Image
import PIL.ImageQt
from multiprocessing import Process, Manager, cpu_count
from std import quick_prop

def is_image(filename):
    return any(filename.lower().endswith(e) 
                for e in ('.jpg', '.png', '.jpeg', '.gif'))

def error_exit(*args):
    print(args)
    sys.exit()

def parse_args(args):
    files = (sys.argv[1:]
                or sorted(f for f in os.listdir('.') if is_image(f)))
    if not files:
         error_exit('Nothing to show.', sys.argv)
    elif not all(os.path.isfile(f) for f in files):
        error_exit("Missing files (Unexpanded glob?)", sys.argv)
    else:
        return files

class ImageViewerX(QMainWindow):
    def __init__(self, filenames, width, height):
        super(ImageViewerX, self).__init__()
        self.filenames = filenames
        self.height = height
        self.label = QLabel()
        self.pixmaps = []
        self.deleted = []
        self.timer = QtCore.QTimer(self)
        self.load_image()
        self.label.setPixmap(self.pixmaps[0])
        self.index = 0
        self.setCentralWidget(self.label)
        self.timer.timeout.connect(self.load_image)
        self.timer.setInterval(10)
        self.timer.start()

    def load_image(self):
        if len(self.pixmaps) < len(self.filenames):
            name = self.filenames[len(self.pixmaps)]
            im = QImage(name)
            im = im.scaledToHeight(self.height, Qt.FastTransformation)
            self.pixmaps.append(QPixmap.fromImage(im))
        else:
            self.timer.stop()
            return
        if len(self.pixmaps) < 100:
            self.timer.setInterval(1)
        elif len(self.pixmaps) < 300:
            self.timer.setInterval(800)
        elif len(self.pixmaps) < 350:
            self.timer.setInterval(1200)
        else:
            self.timer.setInterval(2000)

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key_Escape, Qt.Key_Q):
            self.close()
        else:
            if key == Qt.Key_Delete:
                os.rename(self.filenames[self.index], '_' + self.filenames[self.index])
                self.deleted.append(self.filenames[self.index])
                self.index = min(self.index + 1, len(self.pixmaps) - 1)
                if self.index != 0:
                    self.filenames.pop(self.index - 1)
                    self.pixmaps.pop(self.index - 1)
                    self.index = self.index - 1
                self.timer.setInterval(500)
            if key == Qt.Key_U:
                if len(self.deleted):
                    name = self.deleted.pop()
                    os.rename('_' + name, name)
                    im = QImage(name)
                    im = im.scaledToHeight(self.height, Qt.SmoothTransformation)
                    im = QPixmap.fromImage(im)
                    self.filenames.insert(self.index, name)
                    self.pixmaps.insert(self.index, im)
                else:
                    print('nothing to undo')
            elif key == Qt.Key_Space:
                self.index = min(self.index + 1, len(self.pixmaps) - 1)
                self.timer.setInterval(500)
            elif key == Qt.Key_Backspace:
                self.index = max(0, self.index - 1)
            elif key == Qt.Key_Home:
                self.index = 0
            elif key == Qt.Key_End:
                self.index = max(0, len(self.pixmaps) - 1)
            print('index=%s len=%s tot=%s' % (self.index, len(self.pixmaps), len(self.filenames)))
            self.setWindowTitle(self.filenames[self.index])
            self.label.setPixmap(self.pixmaps[self.index])


def main():
    files = parse_args(sys.argv[1:])
    app = QApplication(sys.argv)
    app.setOverrideCursor(QCursor(Qt.BlankCursor))
    imageViewer = ImageViewerX(files, 
                    QDesktopWidget().screenGeometry().width(),
                    1200)
    imageViewer.show()
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())
