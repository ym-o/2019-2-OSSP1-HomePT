import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys

def ResizeWithAspectRatio(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)

class ShowVideo(QtCore.QObject):
    VideoSignal1 = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, parent=None):
        super(ShowVideo, self).__init__(parent)

    @QtCore.pyqtSlot()
    def startVideo(self):
        global image

        # result 영상 불러오기
        capture = cv2.VideoCapture("./result.avi")
        while True:
            if (capture.get(cv2.CAP_PROP_POS_FRAMES) == capture.get(cv2.CAP_PROP_FRAME_COUNT)):
                capture.open("./result.avi")

            # 프레임별로 쪼개서 화면에 출력
            ret, image = capture.read()
            if ret:
                cv2.imshow("VideoFrame", ResizeWithAspectRatio(image, width=640))

                if cv2.waitKey(33) & 0xFF == ord('q'):
                    break
            else:
                break
        capture.release()

# 결과 출력 페이지
class show_result(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()


    def setupUI(self):
        self.resize(850, 600)
        self.setWindowTitle("HomePT와 함께 하는 올바른 홈트레이닝 라이프")

        # 아이콘
        icon = QtGui.QIcon()
        pixicon = QPixmap('heart.png') # 아이콘에 이미지 삽입
        icon.addPixmap(QtGui.QPixmap(pixicon), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)


        # 스타일시트
        self.setStyleSheet("font: 24pt\"경기천년제목M Medium\"; background-color:\"Aliceblue\";")

        # 문구
        self.textlabel = QtWidgets.QLabel(self)
        self.textlabel.setText("아래 버튼을 클릭하면 영상이 재생됩니다."+"\n"
                               "'q'를 누르면 영상이 정지합니다.")
        self.textlabel.setGeometry(QtCore.QRect(30, 200, 800, 120))
        self.textlabel.setStyleSheet("color:\"black\";font: 26pt\"경기천년제목M Medium\";")
        self.textlabel.setAlignment(QtCore.Qt.AlignCenter)

        # 결과 확인 버튼
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(215, 450, 440, 40))  # 버튼 위치 및 사이즈 설정
        self.pushButton.setText("결과화면 재생")
        self.pushButton.setStyleSheet("background-color:\"Dodgerblue\"; color:\"white\";font: 16pt\"경기천년제목M Medium\";")

        # 버튼을 클릭하면 영상 재생
        self.pushButton.clicked.connect(ShowVideo.startVideo)
