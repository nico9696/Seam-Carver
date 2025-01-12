# to run whole program, run in cmd terminal (inside "seamcarving_files" folder): seamcarvingenv\Scripts\activate 
# to run this file: python gui.py 

#!/usr/bin/env python3

from seamcarver import SeamCarver
from PIL import Image
import sys, os, traceback

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QPushButton, QHBoxLayout,
    QVBoxLayout, QSpinBox, QFileDialog, QGridLayout, QRadioButton
)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal, pyqtSlot

seam = None
is_vertical = True

class WorkerSignals(QObject):
    finished = pyqtSignal()
    update = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    status = pyqtSignal(str)
    repeat = pyqtSignal(int)

def compute_seam(image, signals, count=0):
    global seam, is_vertical
    seam_type = 'vertical' if is_vertical else 'horizontal'
    if seam is None:
        if count:
            signals.status.emit(f'Computing {seam_type} seam {count+1}...')
        else:
            signals.status.emit(f'Computing {seam_type} seam...')
        if is_vertical:
            seam = image.find_vertical_seam()
        else:
            seam = image.find_horizontal_seam()
        if count:
            signals.status.emit(f'Computed {seam_type} seam {count+1}.')
        else:
            signals.status.emit(f'Computed {seam_type} seam.')
    return seam

class ComputeSeamWorker(QRunnable):
    def __init__(self, image):
        super(ComputeSeamWorker, self).__init__()
        self.image = image
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            seam = compute_seam(self.image, self.signals)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(seam)
        finally:
            self.signals.finished.emit()

def remove_seam(image, signals, reps):
    if image is None: return
    global seam, is_vertical
    count = 0
    while True:
        seam = compute_seam(image, signals, count)
        if is_vertical:
            image.remove_vertical_seam(seam)
        else:
            image.remove_horizontal_seam(seam)
        signals.update.emit()
        seam = None
        count += 1

        if reps <= 1: break
        reps -= 1
        signals.repeat.emit(reps)

    signals.repeat.emit(1)
    if count > 1:
        signals.status.emit(f'Removed {count} seams.')
    else:
        signals.status.emit('Removed seam.')

class RemoveSeamWorker(QRunnable):
    def __init__(self, image, reps):
        super(RemoveSeamWorker, self).__init__()
        self.image = image
        self.reps = reps
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            remove_seam(self.image, self.signals, self.reps)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        finally:
            self.signals.finished.emit()


class SeamCarverGui(QMainWindow):
    image = None

    def __init__(self):
        global seam, is_vertical
        super().__init__()
        self.threadpool = QThreadPool()

        self.setWindowTitle('CSCI 30 Seam Carving')
        self.setFixedSize(540, 150)
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        self.generalLayout = QVBoxLayout()

        self.btns = QGridLayout()
        open = QPushButton('Open image')
        open.clicked.connect(self.open_image)
        self.btns.addWidget(open, 0, 0)
        save = QPushButton('Save image')
        save.clicked.connect(self.save_image)
        self.btns.addWidget(save, 1, 0)

        self.show_seam_btn = QPushButton('Show seam')
        self.show_seam_btn.clicked.connect(self.show_seam)
        self.btns.addWidget(self.show_seam_btn, 0, 1)
        self.remove_seam_btn = QPushButton('Remove seam')
        self.remove_seam_btn.clicked.connect(self.remove_seam)
        self.btns.addWidget(self.remove_seam_btn, 1, 1)

        orient = QHBoxLayout()
        orient.addWidget(QLabel('Seam:'))
        self.toggle_v = QRadioButton('&Vertical', self)
        self.toggle_v.toggle()
        self.toggle_v.toggled.connect(self.toggle_orientation)
        orient.addWidget(self.toggle_v)
        self.toggle_h = QRadioButton('&Horizontal', self)
        self.toggle_h.toggled.connect(self.toggle_orientation)
        orient.addWidget(self.toggle_h)
        self.btns.addLayout(orient, 0, 2)

        rep_grp = QHBoxLayout()
        rep_grp.addWidget(QLabel('Repeat:'))

        self.repeat = QSpinBox()
        self.repeat.setMinimum(1)
        self.repeat.setMaximum(100)
        rep_grp.addWidget(self.repeat)
        self.btns.addLayout(rep_grp, 1, 2)

        self.imgview = QLabel()
        #self.imgview.setScaledContents(True)

        self.status = QLabel('Please open an image.')

        self.generalLayout.addLayout(self.btns)
        self.generalLayout.addWidget(self.imgview)
        self.generalLayout.addWidget(self.status)
        centralWidget.setLayout(self.generalLayout)

    def open_image(self):
        global seam
        fname = QFileDialog.getOpenFileName(self, 'Open image', '.', 'Image files (*.jpg *.png)')[0]
        if not fname or fname[0] is None: return
        self.update_status(f'Loading {os.path.basename(fname)}...')
        try:
            self.image = SeamCarver(Image.open(fname))
            self.update_display()
        except:
            self.update_status(f'Error loading {os.path.basename(fname)}!')
            raise
        seam = None
        self.update_status(f'Loaded {os.path.basename(fname)}. Now compute or remove seam.')
        self._enable_buttons()

    def save_image(self):
        global seam
        if self.image is None: return
        fname = QFileDialog.getSaveFileName(self, 'Save image', '.', 'Image files (*.jpg *.png)')[0]
        if not fname or fname[0] is None: return
        self.update_status(f'Saving {os.path.basename(fname)}...')
        try:
            self.image.picture().save(fname)
        except:
            self.update_status(f'Error saving {os.path.basename(fname)}!')
            raise
        seam = None
        self.update_status(f'Saved {os.path.basename(fname)}.')

    def _color_seam(self):
        seam_type = 'vertical' if is_vertical else 'horizontal'
        if is_vertical:
            self.image.color_seam(seam)
        else:
            self.image.color_seam(seam, False)
        self.update_display()
        self.update_status(f'Computed {seam_type} seam, as shown in pink.')
        self.show_seam_btn.setEnabled(False)
        self.toggle_v.setEnabled(False)
        self.toggle_h.setEnabled(False)

    def _update_seam(self, x):
        global seam
        seam = x

    def show_seam(self):
        if self.image is None: return
        worker = ComputeSeamWorker(self.image)
        worker.signals.result.connect(self._update_seam)
        worker.signals.finished.connect(self._color_seam)
        worker.signals.status.connect(self.update_status)
        self.threadpool.start(worker)

    def _disable_buttons(self):
        self.show_seam_btn.setEnabled(False)
        self.remove_seam_btn.setEnabled(False)
        self.toggle_v.setEnabled(False)
        self.toggle_h.setEnabled(False)

    def _enable_buttons(self):
        self.show_seam_btn.setEnabled(True)
        self.remove_seam_btn.setEnabled(True)
        self.toggle_v.setEnabled(True)
        self.toggle_h.setEnabled(True)

    def remove_seam(self):
        if self.image is None: return
        worker = RemoveSeamWorker(self.image, int(self.repeat.value()))
        worker.signals.repeat.connect(self.repeat.setValue)
        worker.signals.update.connect(self.update_display)
        worker.signals.status.connect(self.update_status)
        worker.signals.finished.connect(self._enable_buttons)
        self._disable_buttons()
        self.threadpool.start(worker)

    def toggle_orientation(self):
        global is_vertical
        if self.toggle_v.isChecked():
            is_vertical = True
        elif self.toggle_h.isChecked():
            is_vertical = False
        else:
            raise AssertionError('something went horribly wrong!')

    def update_display(self):
        self.imgview.setPixmap(self.image._to_pixmap())
        btns_h = self.btns.geometry().height()
        new_w = max(self.image.width(), 540)
        new_h = max(self.image.height() + btns_h + self.status.height() + 20, 150)
        self.setFixedSize(new_w, new_h)

    def update_status(self, msg):
        self.status.setText(msg)

if __name__ == '__main__':
    app = QApplication([])
    window = SeamCarverGui()
    window.show()
    sys.exit(app.exec())
