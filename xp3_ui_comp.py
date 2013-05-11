# encoding: utf-8

from PyQt4.QtCore import *


class FileTableModel(QAbstractTableModel, object):
    def __init__(self, parent):
        super(FileTableModel, self).__init__(parent)

        self._parent = parent
        self._file_table = self._parent.hard_drive._file_table

        self.headers = [u'文件名', u'起始柱面', u'起始扇区', u'起始磁道', u'块数']


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]


    def rowCount(self, index=None, *args, **kwargs):
        return len(self._file_table)


    def columnCount(self, index=None, *args, **kwargs):
        return 5


    def data(self, index, role=Qt.DisplayRole):
        row, col = index.row(), index.column()

        if not index.isValid() \
            or not (0 <= row < self.rowCount()) \
            or not (0 <= col < self.columnCount()):
            return QVariant()

        filename = self._file_table.keys()[row]
        item = self._file_table[filename]
        if role == Qt.TextAlignmentRole:
            return Qt.AlignLeft | Qt.AlignVCenter
        elif role == Qt.DisplayRole:
            p = self._parent.hard_drive.logical_to_physical(item.start)
            if col == 0:
                return QString(filename)
            elif col == 1:
                return QVariant(p['cylinder'])
            elif col == 2:
                return QVariant(p['sector'])
            elif col == 3:
                return QVariant(p['track'])
            elif col == 4:
                return QVariant(item.n)
        elif role == Qt.ForegroundRole:
            # if proc_name == self._parent.last_alloc:
            #     return QBrush(Qt.blue)
            pass

        return QVariant()


    def refresh(self):
        self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'),
                  QModelIndex(), QModelIndex())



class AllocationTableModel(QAbstractTableModel, object):
    def __init__(self, parent):
        super(AllocationTableModel, self).__init__(parent)

        self._parent = parent
        self._alloc_table = self._parent.hard_drive._allocation_table

        self.headers = [u'表目号', u'起始块号', u'块数']


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]


    def rowCount(self, index=None, *args, **kwargs):
        return len(self._alloc_table)


    def columnCount(self, index=None, *args, **kwargs):
        return 3


    def data(self, index, role=Qt.DisplayRole):
        row, col = index.row(), index.column()

        if not index.isValid() \
            or not (0 <= row < self.rowCount()) \
            or not (0 <= col < self.columnCount()):
            return QVariant()

        item = self._alloc_table[row]
        if role == Qt.TextAlignmentRole:
            return Qt.AlignLeft | Qt.AlignVCenter
        elif role == Qt.DisplayRole:
            if col == 0:
                return QVariant(row + 1)
            elif col == 1:
                return QVariant(item.start)
            elif col == 2:
                return QVariant(item.n)
        elif role == Qt.ForegroundRole:
            # if proc_name == self._parent.last_alloc:
            #     return QBrush(Qt.blue)
            pass

        return QVariant()


    def refresh(self):
        self._alloc_table = self._parent.hard_drive._allocation_table
        self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'),
                  QModelIndex(), QModelIndex())

