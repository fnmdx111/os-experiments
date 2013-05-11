# encoding: utf-8
from collections import defaultdict

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from xp2 import PageTable


class ProcessModel(QAbstractTableModel, object):
    def __init__(self, parent):
        super(ProcessModel, self).__init__(parent)

        self._parent = parent
        self._proc_list = defaultdict(int)

        self.headers = [u'进程名', u'已分配 (kB)']


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]


    def rowCount(self, index=None, *args, **kwargs):
        return len(self._proc_list)


    def columnCount(self, index=None, *args, **kwargs):
        return 2


    def data(self, index, role=Qt.DisplayRole):
        row, col = index.row(), index.column()

        if not index.isValid() \
            or not (0 <= row < self.rowCount()) \
            or not (0 <= col < self.columnCount()):
            return QVariant()

        proc_name = sorted(self._proc_list.keys())[row]
        size = self._proc_list[proc_name]
        if role == Qt.TextAlignmentRole:
            if col == 0:
                return Qt.AlignLeft | Qt.AlignVCenter
            if col == 1:
                return Qt.AlignLeft | Qt.AlignVCenter
        elif role == Qt.DisplayRole:
            if col == 0:
                return QString(proc_name)
            elif col == 1:
                return QVariant(size)
        elif role == Qt.ForegroundRole:
            if proc_name == self._parent.last_alloc:
                return QBrush(Qt.blue)
        elif role == Qt.UserRole:
            return proc_name

        return QVariant()


    def update(self, proc_name, size):
        if size:
            if not self._proc_list[proc_name]:
                self.beginInsertRows(QModelIndex(), 0, 0)
                self._proc_list[proc_name] = size
                self.endInsertRows()
            else:
                self._proc_list[proc_name] = size
        else:
            self.beginRemoveRows(QModelIndex(), 0, 0)
            del self._proc_list[proc_name]
            self.endRemoveRows()
            return True
        self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'),
                  QModelIndex(), QModelIndex())



class PageTableModel(QAbstractTableModel, object):
    def __init__(self, parent=None):
        super(PageTableModel, self).__init__(parent)

        self._parent = parent
        self._page_table = PageTable(self._parent.mem)

        self.headers = [u'页号', u'块号']


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]


    def rowCount(self, index=None, *args, **kwargs):
        return len(self._page_table.table)


    def columnCount(self, index=None, *args, **kwargs):
        return 2


    def data(self, index, role=Qt.DisplayRole):
        row, col = index.row(), index.column()

        if not index.isValid() \
            or not (0 <= row < self.rowCount()) \
            or not (0 <= col < self.columnCount()):
            return QVariant()

        page = self._page_table.table.keys()[row]
        block = self._page_table.get_block(page)
        if role == Qt.DisplayRole:
            if col == 0:
                return QVariant(page)
            elif col == 1:
                return QVariant(block)
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignLeft | Qt.AlignVCenter

        return QVariant()


    def register(self, blocks):
        self._page_table.register(blocks)
        self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'),
                  QModelIndex(), QModelIndex())


    def release(self, pages):
        self._page_table.release(*pages)
        self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'),
                  QModelIndex(), QModelIndex())



class BitmapModel(QAbstractTableModel, object):
    def __init__(self, parent):
        super(BitmapModel, self).__init__(parent)
        self._parent = parent
        self.last_bit_map = self._parent.mem.bit_map


    def rowCount(self, index=None, *args, **kwargs):
        return 8


    def columnCount(self, index=None, *args, **kwargs):
        return 8


    def headerData(self, idx, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return idx


    def data(self, index=QModelIndex(), role=None):
        row, col = index.row(), index.column()

        if not index.isValid() \
            or not (0 <= index.row() < self.rowCount()) \
            or not (0 <= index.column() < self.columnCount()):
            return QVariant()

        idx = row * self.rowCount() + col
        if role == Qt.TextAlignmentRole:
            return Qt.AlignHCenter | Qt.AlignVCenter
        elif role == Qt.DisplayRole:
            return QVariant(self._parent.mem.bit_map[idx])
        elif role == Qt.ForegroundRole:
            if self.last_bit_map[idx] != self._parent.mem.bit_map[idx]:
                return QBrush(Qt.blue)

        return QVariant()


    def save(self):
        self.last_bit_map = self._parent.mem.bit_map[:]


    def refresh(self):
        self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'),
                  self.index(0, 0), self.index(7, 7))


