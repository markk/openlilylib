#!/usr/bin/env python
# -*- coding: utf-8

import sys, os
from PyQt4 import QtCore,  QtGui, QtWebKit
import oll
import metadata
import docview

class AppInfo(QtCore.QObject):
    """Stores global information about the application
    and the content of the openlilylib directories."""
    
    def __init__(self, path):
        # determine the root paths of the different operations
        # based on the argument representing the path of the application.
        self.root = os.path.abspath(os.path.join(os.path.dirname(path), ".."))
        self.scriptPath = os.path.join(self.root, "docgen")
        self.docPath = os.path.join(self.root, "doc")
        self.defPath = os.path.join(self.root, "library", "oll")
        self.xmpPath = os.path.join(self.root, "usage-examples")
    
class MainWindow(QtGui.QMainWindow):
    def __init__(self, *args):
        QtGui.QMainWindow.__init__(self, *args)
        self.setWindowTitle("openlilylib documentation generator")
        self.createComponents()
        self.createLayout()
        self.createConnects()
        
        self._oll = None
        self.OLL().read()
        
        #TEMPORARY
        self.displayTree()
        self.OLL().saveToHtml()

        
    def createComponents(self):
        self.labelOverview = QtGui.QLabel("Library directory: " + appInfo.defPath)

        # Browsing Tree View
        self.labelBrowse = QtGui.QLabel("Browse Library:")
        self.tvBrowse = QtGui.QTreeView()
        self.modelBrowse = QtGui.QStandardItemModel()
        self.modelBrowse.setHorizontalHeaderLabels(['Browse library'])
        self.tvBrowse.setModel(self.modelBrowse)
        self.tvBrowse.setUniformRowHeights(True)
        self.tvBrowse.header().hide()

        # Snippet Definition
        # This is kept as a reminder. The MetadataWidget
        # will later be used as an _editor_
#        self.metadataWidget = metadata.MetadataWidget(self)

        # Documentation Viewer
        self.wvDocView = docview.DocView()
        self.wvDocView.settings().setUserStyleSheetUrl(
            QtCore.QUrl.fromLocalFile(os.path.join(appInfo.docPath, 'css', 'detailPage.css')))
        self.wvDocView.setHtml("<html><body><p>No snippet opened yet</p></body></html>")
        
        # Buttons
        self.pbReread = QtGui.QPushButton("Read again")
        self.pbExit = QtGui.QPushButton("Exit")
    
    def createConnects(self):
        self.pbReread.clicked.connect(self.refreshOLL)
        self.pbExit.clicked.connect(self.close)
        
        self.tvBrowse.clicked.connect(self.itemRowClicked)

    def createLayout(self):
        centralWidget = QtGui.QWidget()
        centralLayout = cl = QtGui.QGridLayout()

        # organize main window layout
        cl.addWidget(self.labelOverview, 0, 0, 1, 3)
        # browser column
        cl.addWidget(self.labelBrowse, 2, 0)
        cl.addWidget(self.tvBrowse, 3, 0)
        # doc viewer
        cl.addWidget(self.wvDocView, 3, 2)
        # button row
        cl.addWidget(self.pbReread, 5, 0)
        cl.addWidget(self.pbExit, 5, 2)
        
        # complete layout
        centralWidget.setLayout(centralLayout)
        self.setCentralWidget(centralWidget)
    
    def OLL(self):
        if not self._oll:
            self._oll = oll.OLL(self)
        return self._oll
        
    def displayTree(self):
        """Build a tree for browsing the library
        by snippet name, category, tag, author."""
        self.modelBrowse.clear()

        numsnippets = ' (' + str(len(self._oll.items)) + ')'
        byName = QtGui.QStandardItem('By Name' + numsnippets)
        for sn in self._oll.names:
            byName.appendRow(QtGui.QStandardItem(sn))        # usage example column

        self.modelBrowse.appendRow(byName)

        byCategory = QtGui.QStandardItem('By Category')
        for c in self._oll.categories['names']:
            numsnippets = ' (' + str(len(self._oll.categories[c])) + ')'
            cat = QtGui.QStandardItem(c + numsnippets)
            byCategory.appendRow(cat)
            for s in self._oll.categories[c]:
                cat.appendRow(QtGui.QStandardItem(s))
        self.modelBrowse.appendRow(byCategory)
        
        byTag = QtGui.QStandardItem('By Tag')
        for t in self._oll.tags['names']:
            numsnippets = ' (' + str(len(self._oll.tags[t])) + ')'
            tag = QtGui.QStandardItem(t + numsnippets)
            byTag.appendRow(tag)
            for s in self._oll.tags[t]:
                tag.appendRow(QtGui.QStandardItem(s))
        self.modelBrowse.appendRow(byTag)
        
        byAuthor = QtGui.QStandardItem('By Author')
        for a in self._oll.authors['names']:
            numsnippets = ' (' + str(len(self._oll.authors[a])) + ')'
            author = QtGui.QStandardItem(a + numsnippets)
            byAuthor.appendRow(author)
            for s in self._oll.authors[a]:
                author.appendRow(QtGui.QStandardItem(s))
        self.modelBrowse.appendRow(byAuthor)
    
    def refreshOLL(self):
        self.OLL().read()
        self.displayTree()
        self.OLL().saveToHtml()

    def showItem(self, item):
        self.wvDocView.setHtml(item.htmlForDisplay().page())
        self._oll.current = item.name
        
    def itemRowClicked(self, index):
        """When clicking on a row with a snippet name
        'open' that snippet and show its data."""
        
        # determine the content of the clicked row
        # and lookup a snippet if it exists.
        name = unicode(self.modelBrowse.itemFromIndex(index).text())
        item = self._oll.byName(name)
        if item is not None:
            self.showItem(item)

def main(argv):
    global appInfo, mainWindow
    app = QtGui.QApplication(argv)
    appInfo = AppInfo(argv[0])
    mainWindow = MainWindow()
    mainWindow.showMaximized()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main(sys.argv)