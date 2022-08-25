# importing required libraries
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets
import os
import sys


class SearchPanel(QtWidgets.QWidget):
    searched = QtCore.pyqtSignal(str, QtWebEngineWidgets.QWebEnginePage.FindFlag)
    closed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(SearchPanel, self).__init__(parent)
        lay = QtWidgets.QHBoxLayout(self)
        done_button = QtWidgets.QPushButton('&Done')
        self.case_button = QtWidgets.QPushButton('Match &Case', checkable=True)
        next_button = QtWidgets.QPushButton('&Next')
        prev_button = QtWidgets.QPushButton('&Previous')
        self.search_le = QtWidgets.QLineEdit()
        self.setFocusProxy(self.search_le)
        done_button.clicked.connect(self.closed)
        next_button.clicked.connect(self.update_searching)
        prev_button.clicked.connect(self.on_preview_find)
        self.case_button.clicked.connect(self.update_searching)
        for btn in (self.case_button, self.search_le, next_button, prev_button, done_button, done_button):
            lay.addWidget(btn)
            if isinstance(btn, QtWidgets.QPushButton): btn.clicked.connect(self.setFocus)
        self.search_le.textChanged.connect(self.update_searching)
        self.search_le.returnPressed.connect(self.update_searching)
        self.closed.connect(self.search_le.clear)

        QtWidgets.QShortcut(QtGui.QKeySequence.FindNext, self, activated=next_button.animateClick)
        QtWidgets.QShortcut(QtGui.QKeySequence.FindPrevious, self, activated=prev_button.animateClick)
        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), self.search_le, activated=self.closed)

    @QtCore.pyqtSlot()
    def on_preview_find(self):
        self.update_searching(QtWebEngineWidgets.QWebEnginePage.FindBackward)

    @QtCore.pyqtSlot()
    def update_searching(self, direction=QtWebEngineWidgets.QWebEnginePage.FindFlag()):
        flag = direction
        if self.case_button.isChecked():
            flag |= QtWebEngineWidgets.QWebEnginePage.FindCaseSensitively
        self.searched.emit(self.search_le.text(), flag)

    def showEvent(self, event):
        super(SearchPanel, self).showEvent(event)
        self.setFocus(True)
# main window
class MainWindow(QMainWindow):
 
    # constructor
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
 
        # creating a tab widget
        self.tabs = QTabWidget()
 
        # making document mode true
        self.tabs.setDocumentMode(True)
 
        # adding action when double clicked
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
 
        # adding action when tab is changed
        self.tabs.currentChanged.connect(self.current_tab_changed)
 
        # making tabs closeable
        self.tabs.setTabsClosable(True)
 
        # adding action when tab close is requested
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
 
        # making tabs as central widget
        self.setCentralWidget(self.tabs)
 
        # creating a status bar
        self.status = QStatusBar()
 
        # setting status bar to the main window
        self.setStatusBar(self.status)
 
        # creating a tool bar for navigation
        navtb = QToolBar("Navigation")
 
        # adding tool bar tot he main window
        self.addToolBar(navtb)
 
        # creating back action
        back_btn = QAction("Back", self)
 
        # setting status tip
        back_btn.setStatusTip("Back to previous page")
 
        # adding action to back button
        # making current tab to go back
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
 
        # adding this to the navigation tool bar
        navtb.addAction(back_btn)
 
        # similarly adding next button
        next_btn = QAction("Forward", self)
        next_btn.setStatusTip("Forward to next page")
        next_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        navtb.addAction(next_btn)
 
        # similarly adding reload button
        reload_btn = QAction("Reload", self)
        reload_btn.setStatusTip("Reload page")
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        navtb.addAction(reload_btn)
 
        # creating home action
        home_btn = QAction("Home", self)
        home_btn.setStatusTip("Go home")
 
        # adding action to home button
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)
 
        # adding a separator
        navtb.addSeparator()
 
        # creating a line edit widget for URL
        self.urlbar = QLineEdit()
 
        # adding action to line edit when return key is pressed
        self.urlbar.returnPressed.connect(self.navigate_to_url)
 
        # adding line edit to tool bar
        navtb.addWidget(self.urlbar)
 
        # similarly adding stop action
        stop_btn = QAction("Stop", self)
        stop_btn.setStatusTip("Stop loading current page")
        stop_btn.triggered.connect(lambda: self.tabs.currentWidget().stop())
        navtb.addAction(stop_btn)
 
        # creating first tab
        self.add_new_tab(QUrl('http://www.google.com'), 'Homepage')
        
        self._search_panel = SearchPanel()
        self.search_toolbar = QtWidgets.QToolBar()
        self.search_toolbar.addWidget(self._search_panel)
        self.addToolBar(QtCore.Qt.BottomToolBarArea, self.search_toolbar)
        self.search_toolbar.hide()
        self._search_panel.searched.connect(self.on_searched)
        self._search_panel.closed.connect(self.search_toolbar.hide)
        self.create_menus()
 
        # showing all the components
        self.show()
 
        # setting window title
        self.setWindowTitle("Geek PyQt5")
    @QtCore.pyqtSlot(str, QtWebEngineWidgets.QWebEnginePage.FindFlag)
    def on_searched(self, text, flag):
        def callback(found):
            if text and not found:
                self.statusBar().show()
                self.statusBar().showMessage('Not found')
            else:
                self.statusBar().hide()
        self.tabs.currentWidget().findText(text, flag, callback)

    def create_menus(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction('&Find...', self.search_toolbar.show, shortcut=QtGui.QKeySequence.Find)
    # method for adding new tab
    def add_new_tab(self, qurl = None, label ="Blank"):
 
        # if url is blank
        if qurl is None:
            # creating a google url
            qurl = QUrl('http://www.google.com')
 
        # creating a QWebEngineView object
        browser = QWebEngineView()
 
        # setting url to browser
        browser.setUrl(qurl)
 
        # setting tab index
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
 
        # adding action to the browser when url is changed
        # update the url
        browser.urlChanged.connect(lambda qurl, browser = browser:
                                   self.update_urlbar(qurl, browser))
 
        # adding action to the browser when loading is finished
        # set the tab title
        browser.loadFinished.connect(lambda _, i = i, browser = browser:
                                     self.tabs.setTabText(i, browser.page().title()))
 
    # when double clicked is pressed on tabs
    def tab_open_doubleclick(self, i):
 
        # checking index i.e
        # No tab under the click
        if i == -1:
            # creating a new tab
            self.add_new_tab()
 
    # when tab is changed
    def current_tab_changed(self, i):
 
        # get the curl
        qurl = self.tabs.currentWidget().url()
 
        # update the url
        self.update_urlbar(qurl, self.tabs.currentWidget())
 
        # update the title
        self.update_title(self.tabs.currentWidget())
 
    # when tab is closed
    def close_current_tab(self, i):
 
        # if there is only one tab
        if self.tabs.count() < 2:
            # do nothing
            return
 
        # else remove the tab
        self.tabs.removeTab(i)
 
    # method for updating the title
    def update_title(self, browser):
 
        # if signal is not from the current tab
        if browser != self.tabs.currentWidget():
            # do nothing
            return
 
        # get the page title
        title = self.tabs.currentWidget().page().title()
 
        # set the window title
        self.setWindowTitle("% s - Geek PyQt5" % title)
 
    # action to go to home
    def navigate_home(self):
 
        # go to google
        self.tabs.currentWidget().setUrl(QUrl("http://www.google.com"))
 
    # method for navigate to url
    def navigate_to_url(self):
 
        # get the line edit text
        # convert it to QUrl object
        q = QUrl(self.urlbar.text())
 
        # if scheme is blank
        if q.scheme() == "":
            # set scheme
            q.setScheme("http")
 
        # set the url
        self.tabs.currentWidget().setUrl(q)
 
    # method to update the url
    def update_urlbar(self, q, browser = None):
 
        # If this signal is not from the current tab, ignore
        if browser != self.tabs.currentWidget():
 
            return
 
        # set text to the url bar
        self.urlbar.setText(q.toString())
 
        # set cursor position
        self.urlbar.setCursorPosition(0)
 
# creating a PyQt5 application
app = QApplication(sys.argv)
 
# setting name to the application
app.setApplicationName("Geek PyQt5")
 
# creating MainWindow object
window = MainWindow()
 
# loop
app.exec_()