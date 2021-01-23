from Morphing import *
from MorphingGUI import *
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QGraphicsScene
import sys
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import QtGui, QtCore, QtWidgets
import PyQt5
import matplotlib


class Morph(QMainWindow,Ui_MainWindow):
    def __init__(self, parent=None):
        super(Morph,self).__init__(parent)
        self.setupUi(self)
        self.sldAlpha.setEnabled(False)
        self.btnBlend.setEnabled(False)
        self.checkBox.setEnabled(False)
        self.enSld = 0
        self.alpha = 0
        self.tempL = (-1,-1)
        self.tempR = (-1,-1)

        self.btnLoadStart.clicked.connect(self.loadStart)
        self.btnLoadEnd.clicked.connect(self.loadEnd)
        self.btnBlend.clicked.connect(self.blendImage)

        self.sldAlpha.valueChanged.connect(self.getAlpha)
        self.txtAlpha.setText('0.0')

        self.checkBox.stateChanged.connect(self.dispPoints)

        self.sceneLeft = GraphicsScene()
        self.sceneRight = GraphicsScene()
        self.sceneBlend = GraphicsScene()

        self.sceneLeft.signalMousePos.connect(self.pixelSelL)
        self.sceneRight.signalMousePos.connect(self.pixelSelR)


        self.gPen = QtGui.QPen(QtCore.Qt.green, 1)
        self.gBrush = QtGui.QBrush(QtCore.Qt.green)
        self.bPen = QtGui.QPen(QtCore.Qt.blue, 1)
        self.bBrush = QtGui.QBrush(QtCore.Qt.blue)
        self.pen = QtGui.QPen(QtCore.Qt.red, 1)
        self.brush = QtGui.QBrush(QtCore.Qt.red)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Backspace:
            if self.tempR != (-1,-1):
                items = self.sceneRight.items()
                self.sceneRight.removeItem(items[0])
                self.tempR = (-1,-1)
            elif self.tempL != (-1,-1):
                items = self.sceneLeft.items()
                self.sceneLeft.removeItem(items[0])
                self.tempL = (-1,-1)

    def mousePressEvent(self, QMouseEvent):
        #to do, make it so that any selection except the right hand image sets the new points to blue
        super().__init__(self)
        x = QMouseEvent.windowPos().x()
        y = QMouseEvent.windowPos().y()
        if  ((x < 33 or x > 352) or (y < 49 or y > 290)) and ((x < 430 or x > 751) or (y < 49 or y > 290)) and (self.tempR != (-1,-1) and self.tempL != (-1,-1)):
            self.savePoints()

    def savePoints(self):
        items = self.sceneRight.items()
        self.sceneRight.removeItem(items[0])

        items = self.sceneLeft.items()
        self.sceneLeft.removeItem(items[0])

        self.sceneRight.addEllipse(self.tempR[0] - 10, self.tempR[1] - 10, 20, 20, self.bPen, self.bBrush)
        self.sceneLeft.addEllipse(self.tempL[0] - 10, self.tempL[1] - 10, 20, 20, self.bPen, self.bBrush)

        with open(self.pathL + '.txt', 'a') as f:
                f.write('\n' + str(self.tempL[0]) + ' ' + str(self.tempL[1]))
        with open(self.pathR + '.txt', 'a') as f:
                f.write('\n' + str(self.tempR[0]) + ' ' + str(self.tempR[1]))

        #self.tris = loadTriangles(self.pathL + '.txt', self.pathR + '.txt')


        self.tempR = (-1, -1)
        self.tempL = (-1, -1)

    def pixelSelL(self,point):
        if self.tempR == (-1,-1) and self.tempL == (-1,-1):
            self.tempL = (round(point.x(),1), round(point.y(),2))
            self.sceneLeft.addEllipse(self.tempL[0] - 10, self.tempL[1] - 10, 20, 20, self.gPen, self.gBrush)
        elif self.tempR != (-1,-1) and self.tempL != (-1,-1):
            self.savePoints()

            self.tempL = (round(point.x(),1), round(point.y(),2))
            self.tempL = (round(self.tempL[0], 1), round(self.tempL[1], 2))
            self.sceneLeft.addEllipse(self.tempL[0] - 10, self.tempL[1] - 10, 20, 20, self.gPen, self.gBrush)



    def pixelSelR(self,point):
        if self.tempR == (-1, -1) and self.tempL != (-1, -1):
            self.tempR = (round(point.x(),1), round(point.y(),2))
            self.sceneRight.addEllipse(self.tempR[0] - 10, self.tempR[1] - 10, 20, 20, self.gPen, self.gBrush)


    def blendImage(self):

        self.btnBlend.setEnabled(False)
        morph = Morpher(self.imgL,self.tris[0],self.imgR,self.tris[1])
        data = morph.getImageAtAlpha(self.alpha)
        qimage = QtGui.QImage(data, data.shape[1], data.shape[0], QtGui.QImage.Format_Indexed8)
        pixmap = QPixmap(qimage)

        self.sceneBlend.clear()
        self.sceneBlend.addPixmap(pixmap)

        self.graRes.setScene(self.sceneBlend)
        self.graRes.fitInView(self.sceneBlend.sceneRect(), QtCore.Qt.KeepAspectRatio)
        self.btnBlend.setEnabled(True)

    def getAlpha(self):
        self.alpha = self.sldAlpha.value() / 20
        self.txtAlpha.setText(str(self.alpha))


    def dispPoints(self):
        if self.checkBox.isChecked():
            try:
                self.tris = loadTriangles(self.pathL + '.txt', self.pathR + '.txt')
                for tri in self.tris[0]:
                    for i in range(len(tri.vertices)):
                        for j in range(i,len(tri.vertices)):
                            self.sceneLeft.addLine(tri.vertices[i][0],tri.vertices[i][1],tri.vertices[j][0],tri.vertices[j][1],self.pen)

                for tri in self.tris[1]:
                    for i in range(len(tri.vertices)):
                        for j in range(i,len(tri.vertices)):
                            self.sceneRight.addLine(tri.vertices[i][0],tri.vertices[i][1],tri.vertices[j][0],tri.vertices[j][1],self.pen)
            except:
                pass
        else:

            for item in self.sceneLeft.items():
                if isinstance(item, PyQt5.QtWidgets.QGraphicsLineItem):
                    self.sceneLeft.removeItem(item)
            for item in self.sceneRight.items():
                if isinstance(item, PyQt5.QtWidgets.QGraphicsLineItem):
                    self.sceneRight.removeItem(item)

    def loadStart(self,path):
        path, _ = QFileDialog.getOpenFileName(self, caption='Open PNG/JPG file ...',
                                                  filter="PNG files (*.png);;JPG files (*.jpg)")

        if path == '':
            return
        self.pathL = path
        #load the image and txt file for the left image


        #self.dataPlotL = plt.triplot(self.pointsL[:, 0], -self.pointsL[:, 1], self.tri.simplices.copy())
        #self.dataplotL = self.graLeft.addPlot()
        self.sceneLeft.clear()

        self.imgL = loadImage(path)
        self.pixmapL = QPixmap(path)
        self.sceneLeft.addPixmap(self.pixmapL)

        self.graLeft.setScene(self.sceneLeft)
        self.graLeft.fitInView(self.sceneLeft.sceneRect(), QtCore.Qt.KeepAspectRatio)

        if os.path.exists(path + '.txt'):

            try:
                [self.pointsL,self.tri] = getTri(path + '.txt')
                for point in self.pointsL:
                    self.sceneLeft.addEllipse(point[0] - 10, point[1] - 10, 20, 20, self.pen, self.brush)
            except:
                    print("Points could not be loaded, the file may be empty or it may be corrupt")
        else:
            with open(path + '.txt', 'w') as f:
                y = self.pixmapL.size().height()
                x = self.pixmapL.size().width()
                f.write('0.0' + ' ' + '0.0')
                f.write('\n' + str(x/2) + ' ' + str(0.0))
                f.write('\n' + str(x-1) + ' ' + str(0.0))
                f.write('\n' + str(0.0) + ' ' + str(y/2))
                f.write('\n' + str(x-1) + ' ' + str(y/2))
                f.write('\n' + str(0.0) + ' ' + str(y-1))
                f.write('\n' + str(x/2) + ' ' + str(y-1))
                f.write('\n' + str(x-1) + ' ' + str(y-1))

            [self.pointsL, self.tri] = getTri(path + '.txt')
            for point in self.pointsL:
                self.sceneLeft.addEllipse(point[0] - 10, point[1] - 10, 20, 20, self.pen, self.brush)

        if self.enSld == 1:
            self.sldAlpha.setEnabled(True)
            self.checkBox.setEnabled(True)
            self.btnBlend.setEnabled(True)
            if os.path.exists(path + '.txt'):
                try:
                    self.tris = loadTriangles(path + '.txt',self.oPath + '.txt')
                except:
                    print("Triangles could not be created, the file may be empty or it may be corrupt")
        else:
            self.enSld += 1
            self.oPath = path

        if not os.path.exists(path + '.txt'):
            f = open(path + ".txt",'w')



    def loadEnd(self,path):
        path, _ = QFileDialog.getOpenFileName(self, caption='Open PNG/JPG file ...', filter="PNG files (*.png);;JPG files (*.jpg)")
        if path == '':
            return
        self.pathR = path
        #load the image and txt file for the right image


        self.sceneRight.clear()

        #self.dataPlotR = plt.triplot(self.pointsR[:, 0], -self.pointsR[:, 1], self.tri.simplices.copy())
        #self.dataplotR = self.graright.addPlot()
        self.imgR = loadImage(path)

        self.pixmapR = QPixmap(path)
        self.sceneRight.addPixmap(self.pixmapR)

        self.graRight.setScene(self.sceneRight)
        self.graRight.fitInView(self.sceneRight.sceneRect(), QtCore.Qt.KeepAspectRatio)


        if os.path.exists(path + '.txt'):
            try:
                self.pointsR = loadPoints(path + '.txt')
                for point in self.pointsR:
                    self.sceneRight.addEllipse(point[0] - 10, point[1] - 10, 20, 20, self.pen, self.brush)
            except:
                    print("Points could not be loaded, the file may be empty or it may be corrupt")
        else:
            with open(path + '.txt', 'w') as f:
                y = self.pixmapR.size().height()
                x = self.pixmapR.size().width()
                f.write('0.0' + ' ' + '0.0')
                f.write('\n' + str(x/2) + ' ' + str(0.0))
                f.write('\n' + str(x-1) + ' ' + str(0.0))
                f.write('\n' + str(0.0) + ' ' + str(y/2))
                f.write('\n' + str(x-1) + ' ' + str(y/2))
                f.write('\n' + str(0.0) + ' ' + str(y-1))
                f.write('\n' + str(x/2) + ' ' + str(y-1))
                f.write('\n' + str(x-1) + ' ' + str(y-1))
            self.pointsR = loadPoints(path + '.txt')
            for point in self.pointsR:
                self.sceneRight.addEllipse(point[0] - 10, point[1] - 10, 20, 20, self.pen, self.brush)

        if self.enSld == 1:
            self.sldAlpha.setEnabled(True)
            self.checkBox.setEnabled(True)
            self.btnBlend.setEnabled(True)
            if os.path.exists(path + '.txt'):
                try:
                    self.tris = loadTriangles(self.oPath + '.txt',path + '.txt')
                except:
                    print("Triangles could not be created, the file may be empty or it may be corrupt")
        else:
            self.enSld += 1
            self.oPath = path

        if not os.path.exists(path + '.txt'):
            f = open(path + ".txt",'w')



class GraphicsScene(QGraphicsScene):

    signalMousePos = QtCore.pyqtSignal(QtCore.QPointF)

    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)

    def mousePressEvent(self, event):
        pos = event.lastScenePos()
        self.signalMousePos.emit(pos)

if __name__ == "__main__":
    currentApp = QApplication(sys.argv)
    currentForm = Morph()

    currentForm.show()
    currentApp.exec_()