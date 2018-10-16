import os
import sys
import json
import urllib.request
from PyQt5.QtWidgets import QLabel, QRubberBand, QWidget, QLineEdit, \
    QPushButton, QHBoxLayout, QComboBox, QVBoxLayout, QApplication
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QRect, QSize


class QImageEdit(QLabel):
    def __init__(self, parentQWidget = None):
        super(QImageEdit, self).__init__(parentQWidget)
        self.rubberBand = None
        self.move_rubberBand = False
        self.rubberBand_offset = None
        self.originPoint = None

    def setImage(self, image: QPixmap):
        self.setPixmap(image)

    def getImage(self) -> QPixmap:
        if self.rubberBand is not None:
            currentRect = self.rubberBand.geometry()
            return self.pixmap().copy(currentRect)
        else:
            return self.pixmap()

    def clear(self):
        super(QImageEdit, self).clear()
        self.rubberBand = None
        self.move_rubberBand = False
        self.rubberBand_offset = None
        self.originPoint = None

    def mousePressEvent(self, event):
        self.originPoint = event.pos()

        if self.rubberBand is None:
            self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
            self.rubberBand.setGeometry(QRect(self.originPoint, QSize()))
            self.rubberBand.show()
        else:
            if self.rubberBand.geometry().contains(self.originPoint):
                self.rubberBand_offset = self.originPoint - self.rubberBand.pos()
                self.move_rubberBand = True
            else:
                self.rubberBand.hide()
                self.rubberBand.deleteLater()
                self.rubberBand = None
                self.move_rubberBand = False
                self.rubberBand_offset = None
                self.mousePressEvent(event)

    def mouseMoveEvent (self, event):
        newPoint = event.pos()
        if self.move_rubberBand:
            self.rubberBand.move(newPoint - self.rubberband_offset)
        else:
            self.rubberBand.setGeometry(
                QRect(self.originPoint, newPoint).normalized())

    def mouseReleaseEvent (self, eventQMouseEvent):
        self.move_rubberBand = False


class QMain(QWidget):
    def __init__(self, *args, bitbucket_name='name', **kwargs):
        super(QMain, self).__init__(*args, **kwargs)
        self.bitbucket_name = bitbucket_name
        self.info_file = os.path.join('data', self.bitbucket_name + '-info.csv')
        self.known_subjects = {}
        self.initFolders()
        self.initUI()

    def initUI(self):
        input_label = QLabel('Input url: ')
        self.source_url = QLineEdit('')
        self.loadButton = QPushButton("Load")
        self.loadButton.clicked.connect(self.load_image)

        input_hbox = QHBoxLayout()
        input_hbox.addWidget(input_label)
        input_hbox.addWidget(self.source_url)
        input_hbox.addWidget(self.loadButton)

        name_label = QLabel('Subject name: ')
        self.subject_name = QLineEdit('')

        subject_hbox = QHBoxLayout()
        subject_hbox.addWidget(name_label)
        subject_hbox.addWidget(self.subject_name)

        gender_label = QLabel('Subject gender: ')
        self.genderComboBox = QComboBox()
        self.genderComboBox.addItem("female")
        self.genderComboBox.addItem("male")
        ethnicity_label = QLabel('Subject ethnicity: ')
        self.ethnicityComboBox = QComboBox()
        self.ethnicityComboBox.addItem("white")
        self.ethnicityComboBox.addItem("asian")
        self.ethnicityComboBox.addItem("south asian")
        self.ethnicityComboBox.addItem("black")
        self.ethnicityComboBox.addItem("middle eastern")
        self.ethnicityComboBox.addItem("south american")
        self.ethnicityComboBox.addItem("other")

        annotations_hbox = QHBoxLayout()
        annotations_hbox.addWidget(gender_label)
        annotations_hbox.addWidget(self.genderComboBox)
        annotations_hbox.addWidget(ethnicity_label)
        annotations_hbox.addWidget(self.ethnicityComboBox)

        self.imageEdit = QImageEdit()

        self.saveButton = QPushButton("Save")
        self.saveButton.clicked.connect(self.save_image)

        main_vbox = QVBoxLayout()
        main_vbox.addLayout(input_hbox)
        main_vbox.addLayout(subject_hbox)
        main_vbox.addLayout(annotations_hbox)
        main_vbox.addStretch(1)
        main_vbox.addWidget(self.imageEdit)
        main_vbox.addStretch(1)
        main_vbox.addWidget(self.saveButton)
        self.setLayout(main_vbox)

    def load_image(self):
        try:
            data = urllib.request.urlopen(self.source_url.text()).read()
        except:
            return

        image = QImage()
        image.loadFromData(data)

        self.imageEdit.setImage(QPixmap(image))

    def save_image(self):
        image = self.imageEdit.getImage()
        new_image_file = self.get_new_image_file()
        image.save(new_image_file)
        self.imageEdit.clear()

    def get_new_image_file(self):
        return 'out.png'

    def initFolders(self):
        if not os.path.exists('data/'):
            os.mkdir('data/')
        else:
            if os.path.isfile(self.info_file):
                with open(self.info_file) as info_f:
                    idata = info_f.readlines()
                for f, n, _ in map(lambda x: x.split(';'), idata):
                    if n not in self.subject_name:
                        self.subject_name[n] = {}
                        self.subject_name[n]['dir_name'] = f[:f.find('/')]
                        self.subject_name[n]['max_id'] = \
                            int(f[f.find('/'):f.rfind('.')])

                        annot_file = os.path.join(
                            os.path.join('data', f[:f.find('/')]),
                            'annotations.json')
                        if os.path.isfile(annot_file):
                            with open(annot_file) as ann_f:
                                adata = json.load(ann_f)
                            self.subject_name[n].update(adata)
                    else:
                        self.subject_name[n]['max_id'] = \
                            max(self.subject_name[n]['max_id'],
                                int(f[f.find('/'):f.rfind('.')]))


if __name__ == '__main__':
    BITBUCKET_NAME = "filaniOslic"
    myQApplication = QApplication(sys.argv)
    myQMain = QMain(bitbucket_name=BITBUCKET_NAME)
    myQMain.show()
    sys.exit(myQApplication.exec_())