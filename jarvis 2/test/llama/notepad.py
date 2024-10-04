import sys
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QPushButton, QVBoxLayout, QMenu, QMenuBar
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class Notepad(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Notepad')

        self.textEdit = QTextEdit()
        self.textEdit.setFont(QFont('Arial', 12))

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.textEdit)

        self.menuBar = QMenuBar()
        self.layout.setMenuBar(self.menuBar)

        self.fileMenu = QMenu('File')
        self.menuBar.addMenu(self.fileMenu)

        self.newAction = self.fileMenu.addAction('New')
        self.newAction.triggered.connect(self.newFile)
        self.openAction = self.fileMenu.addAction('Open')
        self.openAction.triggered.connect(self.openFile)
        self.saveAction = self.fileMenu.addAction('Save')
        self.saveAction.triggered.connect(self.saveFile)
        self.exitAction = self.fileMenu.addAction('Exit')
        self.exitAction.triggered.connect(self.close)

        self.layout.addWidget(self.textEdit)

        self.setLayout(self.layout)

    def newFile(self):
        self.textEdit.clear()

    def openFile(self):
        filename, _ = QApplication.instance().fileDialog('Open', 'Text Files (*.txt)')
        if filename:
            with open(filename, 'r') as file:
                self.textEdit.setText(file.read())

    def saveFile(self):
        filename, _ = QApplication.instance().fileDialog('Save', 'Text Files (*.txt)')
        if filename:
            with open(filename, 'w') as file:
                file.write(self.textEdit.toPlainText())

def main():
    app = QApplication(sys.argv)
    ex = Notepad()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()