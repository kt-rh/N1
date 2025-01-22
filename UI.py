import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton, QHBoxLayout

from PyQt5.QtCore import Qt, QSize, QEvent

from PyQt5.QtGui import QColor, QTextFormat, QTextCursor, QPainter

import typo1

import typo2

 

class LineNumberTextEdit(QTextEdit):

    def __init__(self, *args, **kwargs):

        super(LineNumberTextEdit, self).__init__(*args, **kwargs)

        self.lineNumberArea = LineNumberArea(self)

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)

        self.updateRequest.connect(self.updateLineNumberArea)

        self.cursorPositionChanged.connect(self.highlightCurrentLine)

        self.updateLineNumberAreaWidth(0)

 

    def lineNumberAreaWidth(self):

        digits = len(str(self.blockCount()))

        space = 3 + self.fontMetrics().width('9') * digits

        return space

 

    def updateLineNumberAreaWidth(self, _):

        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

 

    def updateLineNumberArea(self, rect, dy):

        if dy:

            self.lineNumberArea.scroll(0, dy)

        else:

            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

 

        if rect.contains(self.viewport().rect()):

            self.updateLineNumberAreaWidth(0)

 

    def resizeEvent(self, event):

        super(LineNumberTextEdit, self).resizeEvent(event)

        cr = self.contentsRect()

        self.lineNumberArea.setGeometry(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height())

 

    def highlightCurrentLine(self):

        extraSelections = []

 

        if not self.isReadOnly():

            selection = QTextEdit.ExtraSelection()

            lineColor = self.palette().alternateBase()

            selection.format.setBackground(lineColor)

            selection.format.setProperty(QTextFormat.FullWidthSelection, True)

            selection.cursor = self.textCursor()

            selection.cursor.clearSelection()

            extraSelections.append(selection)

 

        self.setExtraSelections(extraSelections)

 

    def lineNumberAreaPaintEvent(self, event):

        painter = QPainter(self.lineNumberArea)

        painter.fillRect(event.rect(), Qt.lightGray)

 

        block = self.firstVisibleBlock()

        blockNumber = block.blockNumber()

        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()

        bottom = top + self.blockBoundingRect(block).height()

 

        while block.isValid() and top <= event.rect().bottom():

            if block.isVisible() and bottom >= event.rect().top():

                number = str(blockNumber + 1)

                painter.setPen(Qt.black)

                painter.drawText(0, top, self.lineNumberArea.width(), self.fontMetrics().height(),

                                 Qt.AlignRight, number)

 

            block = block.next()

            top = bottom

            bottom = top + self.blockBoundingRect(block).height()

            blockNumber += 1

 

class LineNumberArea(QWidget):

    def __init__(self, editor):

        super(LineNumberArea, self).__init__(editor)

        self.codeEditor = editor

 

    def sizeHint(self):

        return QSize(self.codeEditor.lineNumberAreaWidth(), 0)

 

    def paintEvent(self, event):

        self.codeEditor.lineNumberAreaPaintEvent(event)

 

class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.initUI()

 

    def initUI(self):

        self.setWindowTitle('Text Editor with Line Numbers')

        self.setGeometry(100, 100, 800, 600)

 

        self.textEditA = LineNumberTextEdit()

        self.textEditB = QTextEdit()

        button = QPushButton('Check Errors')

        button.clicked.connect(self.check_errors)

 

        layoutA = QVBoxLayout()

        layoutA.addWidget(self.textEditA)

        layoutB = QVBoxLayout()

        layoutB.addWidget(self.textEditB)

        buttonLayout = QHBoxLayout()

        buttonLayout.addWidget(button)

 

        mainLayout = QVBoxLayout()

        mainLayout.addLayout(layoutA)

        mainLayout.addLayout(buttonLayout)

        mainLayout.addLayout(layoutB)

 

        container = QWidget()

        container.setLayout(mainLayout)

        self.setCentralWidget(container)

 

    def check_errors(self):

        text = self.textEditA.toPlainText()

 

        # typo1.pyの関数を使用して誤りを検出し、補完されたテキストを取得

        completed_text, errors = typo1.detect_and_correct_errors(text)

 

        # 誤り部分を赤字でハイライト表示

        cursor = self.textEditA.textCursor()

        for error in errors:

            cursor.setPosition(error['position'])

            cursor.movePosition(cursor.Right, cursor.KeepAnchor)

            char_format = cursor.charFormat()

            char_format.setForeground(QColor(Qt.red))

            cursor.setCharFormat(char_format)

 

            error_message = {

                1: "脱字があります。",

                2: "衍字があります。",

                3: "衍字があります。",

                4: "誤字があります。",

                5: "誤字があります。",

                6: "誤字があります。",

                7: "誤字があります。",

                8: "誤字があります。"

            }

            error_type_label = typo1.typo_model.config.id2label[error['error_type']]

            error_message_text = error_message.get(error['error_type'], "誤字があります。")

            block_number = cursor.blockNumber() + 1

            error_text = f"行: {block_number} 位置: {error['position']} 文字: {error['character']} エラー: {error_message_text}"

            self.textEditB.append(error_text)

 

        # typo2.pyの関数を使用してエラーメッセージを取得

        typo2_errors = typo2.check_kanji_and_length(text)

        for error in typo2_errors:

            self.textEditB.append(error)

 

if __name__ == '__main__':

    app = QApplication(sys.argv)

    mainWin = MainWindow()

    mainWin.show()

    sys.exit(app.exec_())