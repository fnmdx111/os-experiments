# encoding: utf-8
from collections import defaultdict

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
from xp2 import Memory
from xp2_ui_comp import ProcessModel, PageTableModel, BitmapModel


class XP2(QDialog, object):
    def __init__(self, mem):
        super(XP2, self).__init__()

        self.mem = mem

        self.last_alloc = None

        ctrl_panel = QGridLayout()

        proc_name_label = QLabel(u'进程名')
        self.proc_name_le = QLineEdit()
        proc_name_label.setBuddy(self.proc_name_le)

        size_label = QLabel(u'大小 (kB)')
        self.size_le = QLineEdit()
        size_label.setBuddy(self.size_le)

        self.add_button = QPushButton(u'添加')
        self.add_button.setSizePolicy(QSizePolicy.Preferred,
                                      QSizePolicy.Preferred)
        self.connect(self.add_button, SIGNAL('clicked()'), self.add_process)

        ctrl_panel.addWidget(proc_name_label, 0, 0)
        ctrl_panel.addWidget(self.proc_name_le, 0, 1)
        ctrl_panel.addWidget(size_label, 1, 0)
        ctrl_panel.addWidget(self.size_le, 1, 1)
        ctrl_panel.addWidget(self.add_button, 0, 3, 2, 1)

        self.process_model = ProcessModel(self)
        self.proc_list_view = QTreeView()
        self.proc_list_view.setModel(self.process_model)
        self.proc_list_view.setRootIsDecorated(False)
        self.proc_list_view.setItemsExpandable(False)

        self.page_table_models = defaultdict(lambda: PageTableModel(self))
        self.page_table_view = QTreeView()
        self.page_table_view.setModel(self.page_table_models[None])
        self.page_table_view.setRootIsDecorated(False)
        self.page_table_view.setItemsExpandable(False)
        self.page_table_view.setSelectionMode(QAbstractItemView.ExtendedSelection)

        bit_map_dialog = QDialog(self)
        _l = QHBoxLayout()
        self.bit_map_view = QTableView()
        self.bit_map_model = BitmapModel(self)
        self.bit_map_view.setModel(self.bit_map_model)
        self.bit_map_view.resizeColumnsToContents()
        _l.addWidget(self.bit_map_view)
        bit_map_dialog.setLayout(_l)
        bit_map_dialog.resize(220, 295)
        bit_map_dialog.show()

        self.connect(self.proc_list_view, SIGNAL('clicked(QModelIndex)'),
                     self.switch_page_table_model)
        self.connect(self.proc_list_view, SIGNAL('activated(QModelIndex)'),
                     self.switch_page_table_model)

        self.release_button = QPushButton(u'释放')
        self.connect(self.release_button, SIGNAL('clicked()'),
                     self.release_pages)

        v_box = QVBoxLayout()
        v_box.addWidget(self.proc_list_view)
        v_box.addLayout(ctrl_panel)
        v_box.addWidget(self.page_table_view)
        v_box.addWidget(self.release_button)
        self.setLayout(v_box)


    def add_process(self):
        proc_name = unicode(self.proc_name_le.text())
        if not proc_name:
            return
        else:
            self.proc_name_le.setText('')

        size = int(self.size_le.text())
        if not size:
            return
        else:
            self.size_le.setText('')

        self.bit_map_model.save()
        blocks = self.mem.allocate(size)
        if blocks:
            self.bit_map_model.refresh()

            page_table_model = self.page_table_models[proc_name]
            page_table_model.register(blocks)
            self.page_table_view.setModel(page_table_model)

            self.current_proc_name = proc_name
            self.refresh_alloc_size(proc_name)


    def refresh_alloc_size(self, proc_name):
        self.last_alloc = proc_name

        page_table_model = self.page_table_models[proc_name]

        removed = self.process_model.update(proc_name,
                                    len(page_table_model._page_table.table)
                                    * self.mem.page_size)
        if removed:
            self.current_proc_name = None


    def switch_page_table_model(self, index):
        proc_name = self.process_model.data(index, role=Qt.UserRole)
        self.current_proc_name = proc_name
        self.page_table_view.setModel(self.page_table_models[proc_name])


    def release_pages(self):
        page_table_model = self.page_table_view.model()

        indices = self.page_table_view.selectedIndexes()
        if not indices:
            indices = [page_table_model.index(row, 0)
                       for row in
                       range(len(page_table_model._page_table.table))]

        pages = [idx.data().toPyObject() for idx in indices
                 if idx.column() == 0]

        self.bit_map_model.save()
        self.bit_map_model.refresh()

        page_table_model.release(pages)
        self.page_table_view.clearSelection()


        proc_selected_idx = self.proc_list_view.selectedIndexes()
        if proc_selected_idx:
            self.switch_page_table_model(proc_selected_idx[0])
        current_proc_name = unicode(proc_selected_idx[0].data().toPyObject())\
                            if proc_selected_idx else self.current_proc_name
        if current_proc_name:
            self.refresh_alloc_size(current_proc_name)



if __name__ == '__main__':
    app = QApplication(sys.argv)

    dialog = XP2(Memory())
    dialog.show()

    app.exec_()


