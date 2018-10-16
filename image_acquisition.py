import os
import sys
import json
import urllib.request
from PyQt5.QtWidgets import QLabel, QRubberBand, QWidget, QLineEdit, \
    QPushButton, QHBoxLayout, QComboBox, QVBoxLayout, QApplication, QCompleter
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QRect, QSize, Qt, QStringListModel


GENDER = {
    'female': 'f',
    'male': 'm'
}
ETHNICITY = {
    "white": '1',
    "asian": '2',
    "south asian": '3',
    "black": '4',
    "middle eastern": '5',
    "south american": '6',
    "other": '99'
}
DEFAULT = {
    "name": '',
    "dir_name": '',
    "ethnicity": '1',
    "gender": 'm',
    "max_id": 0
}


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
        if self.rubberBand is not None:
            self.rubberBand.deleteLater()
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
                self.rubberBand_offset = \
                    self.originPoint - self.rubberBand.pos()
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
            self.rubberBand.move(newPoint - self.rubberBand_offset)
        else:
            self.rubberBand.setGeometry(
                QRect(self.originPoint, newPoint).normalized())

    def mouseReleaseEvent (self, event):
        self.move_rubberBand = False


class QMain(QWidget):
    def __init__(self, *args, bitbucket_name='name', **kwargs):
        super(QMain, self).__init__(*args, **kwargs)
        self.bitbucket_name = bitbucket_name
        self.info_file = os.path.join('data', self.bitbucket_name + '-info.csv')
        self.known_subjects = {}
        self.current_subject = {}
        self.max_subject_id = 0
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
        self.subject_completer = QCompleter(
            QStringListModel(),
            self.subject_name,
            caseSensitivity=Qt.CaseInsensitive,
            filterMode=Qt.MatchContains)
        self.subject_completer.setModel(
            QStringListModel(self.known_subjects.keys(),
                             self.subject_completer))
        self.subject_name.setCompleter(self.subject_completer)
        self.subject_name.editingFinished.connect(self.load_subject)

        subject_hbox = QHBoxLayout()
        subject_hbox.addWidget(name_label)
        subject_hbox.addWidget(self.subject_name)

        gender_label = QLabel('Subject gender: ')
        self.genderComboBox = QComboBox()
        self.genderComboBox.addItems(GENDER.keys())
        ethnicity_label = QLabel('Subject ethnicity: ')
        self.ethnicityComboBox = QComboBox()
        self.ethnicityComboBox.addItems(ETHNICITY.keys())

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

        if image.size().width() > 1000 or image.size().height() > 1000:
            image = image.scaled(1000, 1000, Qt.KeepAspectRatio)

        self.imageEdit.setImage(QPixmap(image))

    def save_image(self):
        image = self.imageEdit.getImage()
        if image is not None:
            self.save_subject()
            new_image_file = self.get_output_file()
            image.save(new_image_file)
        self.clear()

    def clear(self):
        self.imageEdit.clear()
        self.source_url.clear()
        self.subject_name.clear()

    def load_subject(self):
        subject = self.subject_name.text()
        if not subject:
            return

        if subject not in self.known_subjects.keys():
            self.known_subjects[subject] = DEFAULT.copy()

        self.current_subject = self.known_subjects[subject]
        self.current_subject.update({'name': subject})
        self.update_fields()

    def update_fields(self):
        reverse_g = dict(map(reversed, GENDER.items()))
        reverse_e = dict(map(reversed, ETHNICITY.items()))
        self.genderComboBox.setCurrentText(
            reverse_g[self.current_subject['gender']])
        self.ethnicityComboBox.setCurrentText(
            reverse_e[self.current_subject['ethnicity']])

        self.subject_completer.setModel(
            QStringListModel(self.known_subjects.keys(),
                             self.subject_completer))

    def save_subject(self):
        self.current_subject['gender'] = \
            GENDER[self.genderComboBox.currentText()]
        self.current_subject['ethnicity'] = \
            ETHNICITY[self.ethnicityComboBox.currentText()]

        if not self.current_subject['dir_name']:
            self.max_subject_id += 1
            dir_name = os.path.join('data',
                                    self.bitbucket_name +
                                    '-{:02}'.format(self.max_subject_id))
            if not os.path.isdir(dir_name):
                os.mkdir(dir_name)
            self.current_subject['dir_name'] = \
                self.bitbucket_name + '-{:02}'.format(self.max_subject_id)

        annot_file = os.path.join('data', self.current_subject['dir_name'],
                                  'annotations.json')
        with open(annot_file, 'w') as f:
            json.dump({
                'gender': self.current_subject['gender'],
                'ethnicity': self.current_subject['ethnicity']
            }, f)

    def get_output_file(self):
        self.current_subject['max_id'] += 1
        file_name = os.path.join(self.current_subject['dir_name'],
                                 '{:02}.png'.format(
                                     self.current_subject['max_id']))
        new_info = ';'.join([file_name,
                             '"' + self.current_subject['name'] + '"',
                             self.source_url.text()])
        with open(self.info_file, 'a') as f:
            f.write(new_info + '\n')

        return os.path.join('data', file_name)

    def initFolders(self):
        if not os.path.exists('data/'):
            os.mkdir('data/')
        else:
            if os.path.isfile(self.info_file):
                with open(self.info_file) as info_f:
                    idata = info_f.readlines()
                for f, n, _ in map(lambda x: x.split(';'), idata):
                    name = n[1:-1]
                    if n not in self.known_subjects:
                        self.known_subjects[name] = DEFAULT.copy()
                        self.known_subjects[name]['name'] = name
                        self.known_subjects[name]['dir_name'] = f[:f.find('/')]
                        self.known_subjects[name]['max_id'] = \
                            int(f[f.find('/') + 1:f.rfind('.')])

                        annot_file = os.path.join('data', f[:f.find('/')],
                                                  'annotations.json')
                        if os.path.isfile(annot_file):
                            with open(annot_file) as ann_f:
                                adata = json.load(ann_f)
                            self.known_subjects[name].update(adata)

                        num = int(f[f.find('/') - 2:f.find('/')])
                        self.max_subject_id = max(self.max_subject_id, num)
                    else:
                        self.known_subjects[name]['max_id'] = \
                            max(self.known_subjects[name]['max_id'],
                                int(f[f.find('/') + 1:f.rfind('.')]))


if __name__ == '__main__':
    BITBUCKET_NAME = "filaniOslic"
    myQApplication = QApplication(sys.argv)
    myQMain = QMain(bitbucket_name=BITBUCKET_NAME)
    myQMain.show()
    sys.exit(myQApplication.exec_())