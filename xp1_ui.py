# encoding: utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys

from xp1 import *

class ProcessListModel(QAbstractTableModel, object):
    def __init__(self, parent):
        super(ProcessListModel, self).__init__(parent)
        self._queue = PriorityQueue()
        self._queue.put((65535, IdleProcess()))
        self.headers = [u'进程名', u'剩余时间', u'优先级']
        self.parent = parent


    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        return self._queue.qsize()


    def columnCount(self, parent=QModelIndex(), *args, **kwargs):
        return 3


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]


    def data(self, index, role=Qt.DisplayRole):
        row, col = index.row(), index.column()

        if not index.isValid()\
            or not (0 <= row < self.rowCount())\
            or not (0 <= col < self.columnCount()):
            return QVariant()

        prior, pcb = self._queue.queue[row]
        if role == Qt.TextAlignmentRole:
            if col == 0:
                return Qt.AlignLeft | Qt.AlignVCenter
            else:
                return Qt.AlignRight | Qt.AlignVCenter
        elif role == Qt.DisplayRole:
            if col == 0:
                return QString(pcb.proc_name)
            elif col == 1:
                return QVariant(pcb.time_demand)
            elif col == 2:
                return QVariant(pcb.priority)
        elif role == Qt.ForegroundRole:
            if pcb == self.parent.last_run_proc:
                return QBrush(Qt.blue)

        return QVariant()



class XP1(QDialog, object):
    def __init__(self, parent=None):
        super(XP1, self).__init__(parent)
        self.last_run_proc = None

        g_layout = QGridLayout()

        self.process_name_le = QLineEdit()
        label = QLabel(u'进程名')
        label.setBuddy(self.process_name_le)
        g_layout.addWidget(self.process_name_le, 0, 1)
        g_layout.addWidget(label, 0, 0)

        self.time_le = QLineEdit()
        label = QLabel(u'时间')
        label.setBuddy(self.time_le)
        g_layout.addWidget(self.time_le, 1, 1)
        g_layout.addWidget(label, 1, 0)

        self.prior_le = QLineEdit()
        label = QLabel(u'优先级')
        g_layout.addWidget(self.prior_le, 2, 1)
        g_layout.addWidget(label, 2, 0)

        self.add_button = QPushButton(u'添加进程')
        g_layout.addWidget(self.add_button, 3, 0, 1, 2)

        _l = QHBoxLayout()
        self.continue_le = QLineEdit('1')
        self.continue_button = QPushButton(u'继续')
        _l.addWidget(self.continue_button)
        _l.addWidget(self.continue_le)
        _l.addWidget(QLabel(u'次'))

        self.logger = QTextBrowser()

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.logger)
        right_layout.addLayout(_l)

        self.process_list_view = QTreeView()
        self.process_list_view.setMinimumWidth(310)
        self.process_list_view.setItemsExpandable(False)
        self.process_list_view.setRootIsDecorated(False)
        self.model = ProcessListModel(self)
        self.process_list_view.setModel(self.model)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.process_list_view)
        left_layout.addLayout(g_layout)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)

        self.connect(self.add_button,
                     SIGNAL('clicked()'),
                     self.add_process)
        self.connect(self.continue_button,
                     SIGNAL('clicked()'),
                     self.continue_process)

        self.setTabOrder(self.continue_button, self.process_name_le)
        self.setTabOrder(self.process_name_le, self.time_le)
        self.setTabOrder(self.time_le, self.prior_le)
        self.setTabOrder(self.prior_le, self.continue_button)


    def add_process(self):
        pcb = ProcessControlBlock(self.process_name_le.text(),
                                  int(self.time_le.text()),
                                  int(self.prior_le.text()))
        self.model.beginInsertRows(QModelIndex(), 0, 0)
        self.model._queue.put((pcb.priority, pcb))
        self.model.endInsertRows()

        self.process_name_le.setText('')
        self.time_le.setText('')
        self.prior_le.setText('')


    def continue_process(self):
        cnt = int(self.continue_le.text())
        for _ in range(cnt):
            self.model.beginRemoveRows(QModelIndex(), 0, 0)
            _, pcb = self.model._queue.get()
            self.model.endRemoveRows()

            pcb.run_once()
            self.last_run_proc = pcb
            self.logger.append(u'%s运行了一个时间单位' % pcb.proc_name)

            if not pcb.is_finished():
                self.model.beginInsertRows(QModelIndex(), 0, 0)
                self.model._queue.put((pcb.priority, pcb))
                self.logger.append(u'将%s放回优先队列' % pcb.proc_name)
                self.model.endInsertRows()
            else:
                self.logger.append(u'%s完成作业，移出队列' % pcb.proc_name)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = XP1()
    dialog.show()

    app.exec_()


