# encoding: utf-8

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
from xp3 import HardDrive
from xp3_ui_comp import AllocationTableModel, FileTableModel


class XP3(QDialog, object):
    def __init__(self, hard_drive):
        super(XP3, self).__init__(None)

        self.hard_drive = hard_drive

        self.filename_le = QLineEdit()
        filename_label = QLabel(u'文件名')
        filename_label.setBuddy(self.filename_le)

        self.size_le = QLineEdit()
        size_label = QLabel(u'大小 (块)')
        size_label.setBuddy(self.size_le)

        self.add_button = QPushButton(u'添加')
        self.add_button.setSizePolicy(QSizePolicy.Preferred,
                                      QSizePolicy.Preferred)
        self.recycle_button = QPushButton(u'回收文件')
        self.recycle_button.setSizePolicy(QSizePolicy.Preferred,
                                          QSizePolicy.Preferred)

        self.message_label = QLabel(u'实验三，我是信息条')
        self.message_label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

        ctrl_panel = QGridLayout()
        ctrl_panel.addWidget(filename_label, 0, 0)
        ctrl_panel.addWidget(self.filename_le, 0, 1)
        ctrl_panel.addWidget(size_label, 1, 0)
        ctrl_panel.addWidget(self.size_le, 1, 1)
        ctrl_panel.addWidget(self.add_button, 0, 2, 2, 1)
        ctrl_panel.addWidget(self.recycle_button, 0, 3, 2, 1)
        ctrl_panel.addWidget(self.message_label, 2, 0, 1, 4)

        self.alloc_table_model = AllocationTableModel(self)
        self.alloc_table_view = QTreeView()
        self.alloc_table_view.setModel(self.alloc_table_model)
        self.alloc_table_view.setRootIsDecorated(False)
        self.alloc_table_view.setItemsExpandable(False)
        self.alloc_table_view.setMaximumWidth(250)
        for i in [0, 1]:
            self.alloc_table_view.setColumnWidth(i, 57)

        self.file_table_model = FileTableModel(self)
        self.file_table_view = QTreeView()
        self.file_table_view.setModel(self.file_table_model)
        self.file_table_view.setRootIsDecorated(False)
        self.file_table_view.setItemsExpandable(False)
        for i in range(1, 5):
            self.file_table_view.setColumnWidth(i, 57)

        main_layout = QGridLayout()
        main_layout.addWidget(self.alloc_table_view, 0, 0)
        main_layout.addWidget(self.file_table_view, 0, 1)
        main_layout.addLayout(ctrl_panel, 1, 0, 1, 2)

        self.setLayout(main_layout)
        self.resize(630, 370)

        self.connect(self.add_button,
                     SIGNAL('clicked()'),
                     self.alloc_file)
        self.connect(self.recycle_button,
                     SIGNAL('clicked()'),
                     self.recycle_file)


    def alloc_file(self):
        filename = unicode(self.filename_le.text())
        if not filename:
            return
        else:
            self.filename_le.setText('')

        size = int(self.size_le.text())
        if not size:
            return
        else:
            self.size_le.setText('')

        self.file_table_model.beginInsertRows(QModelIndex(), 0, 0)
        self.alloc_table_model.beginInsertColumns(QModelIndex(), 0, 0)
        status, ext = self.hard_drive.allocate(filename, size)
        self.alloc_table_model.endInsertRows()
        self.file_table_model.endInsertRows()
        # self.file_table_model.refresh()

        msg = QString(u'分配<font color="%1"><b>%2</b></font>，%3。')
        if not status:
            msg = msg.arg(u'red').arg(u'失败')
            if ext == -1:
                msg = msg.arg(u'原因：文件分配表中已存在改文件名')
            elif ext == 0:
                msg = msg.arg(u'原因：不能在空闲区表中找到满足要求的区')
        else:
            msg = msg.arg(u'green')\
                     .arg(u'成功')\
                     .arg(u'空闲区号%s' % self.hard_drive.physical_to_logical(ext))
        self.message_label.setText(msg)


    def recycle_file(self):
        selected_indices = self.file_table_view.selectedIndexes()
        if selected_indices:
            selected_filename = unicode(selected_indices[0].data().toPyObject())
        else:
            return

        s = self.hard_drive._file_table[selected_filename]
        self.alloc_table_model.beginInsertRows(QModelIndex(), 0, 0)
        status = self.hard_drive.recycle(selected_filename)
        self.alloc_table_model.endInsertRows()
        msg = QString(u'回收<font color="%1"><b>%2</b></font>，%3。')
        if status:
            self.file_table_model.refresh()
            self.alloc_table_model.refresh()

            msg = msg.arg('green').arg(u'成功').arg(u'起始空闲块号%s' % s.start)
        else:
            msg = msg.arg('red').arg(u'失败').arg(u'原因未知')
        self.message_label.setText(msg)






if __name__ == '__main__':
    app = QApplication(sys.argv)

    dialog = XP3(HardDrive())
    dialog.show()

    app.exec_()


