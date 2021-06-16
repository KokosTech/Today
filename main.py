# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys
import urllib
import ssl

from PyQt5.uic.properties import QtCore
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QFrame
from PySide6.QtCore import QFile, QTime, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap
from PySide6 import QtGui
from PySide6 import *
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection

# Local

import components.news.news as news
import components.weather.weather as weather
import components.mail.email_sec as email_sec


class App(QWidget):
    def __init__(self):
        super(App, self).__init__()
        self.load_ui()

        # Title bar

        self.ui.closeButton.setShortcut('Ctrl+D')
        self.ui.closeButton.clicked.connect(self.close)

        self.ui.minimize.clicked.connect(self.showSmall)

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.displayTime)
        self.timer.start()

        # News

        self.display_news()
        self.w_timer = QtCore.QTimer(self)
        self.w_timer.setInterval(600000)
        self.w_timer.timeout.connect(self.display_news)
        self.w_timer.start()

        # Weather

        self.display_weather()
        self.w_timer = QtCore.QTimer(self)
        self.w_timer.setInterval(300000)
        self.w_timer.timeout.connect(self.display_weather)
        self.w_timer.start()

        self.display_email()
        # self.e_timer = QtCore.QTimer(self)
        # self.e_timer.setInterval(1000)
        # self.e_timer.timeout.connect(self.display_email)
        # self.e_timer.start()

    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")
        ui_file.close()

    # Title Bar

    def showSmall(self):
        widget.showMinimized()

    def close(self):
        sys.exit(app.exec())

    def displayTime(self):
        self.ui.time.setText(QTime.currentTime().toString('hh:mm'))

    # News

    def display_news(self):
        self.news_class = news.News()
        newss = self.news_class.get_news()

        for i in newss:
            hl = QHBoxLayout()
            vl = QVBoxLayout()

            img = QLabel()
            try:
                image = QtGui.QImage()
                icon_link = i["urlToImage"]
                if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
                        getattr(ssl, '_create_unverified_context', None)):
                    ssl._create_default_https_context = ssl._create_unverified_context
                data = urllib.request.urlopen(icon_link).read()
                image.loadFromData(data)
                img.setPixmap(QPixmap(image).scaled(175, 175, Qt.KeepAspectRatio, Qt.FastTransformation))
            except urllib.error.URLError:
                image = QtGui.QImage('assets/image.png')
                img.setPixmap(QPixmap(image).scaled(175, 175, Qt.KeepAspectRatio, Qt.FastTransformation))

            title = QLabel()
            title.setText(f"<a style='text-decoration: none !important; color: white !important;' href=\"{i['url']}\">{i['title']}</a>")
            title.setTextFormat(Qt.RichText)
            title.setTextInteractionFlags(Qt.TextBrowserInteraction)
            title.setOpenExternalLinks(True)
            title.setStyleSheet('color: white !important; font-size: 18px; font-weight: bold; text-decoration: none !important')
            title.setWordWrap(True)

            desc = QLabel()
            desc.setText(str(i["description"]))
            desc.setStyleSheet('color: white; font-size: 14px')
            desc.setWordWrap(True)

            vl.addWidget(title, stretch=1)
            vl.addWidget(desc, stretch=3)

            hl.addWidget(img, alignment=Qt.AlignVCenter | Qt.AlignHCenter, stretch=1)
            hl.addLayout(vl, stretch=3)

            frame = QFrame()
            frame.setLayout(hl)
            frame.setStyleSheet('background: #2B2B2B')

            self.ui.news.addWidget(frame)

    # Weather

    def display_weather(self):
        # Temp at the moment
        self.weather_class = weather.Weather()
        self.ui.weather.setText(str(int(self.weather_class.get_temp("celsius"))) + "C°")

        # Reset
        for i in reversed(range(self.ui.forecast.count())):
            self.ui.forecast.itemAt(i).layout().setParent(None)

        # Icon at the moment
        self.display_weather_icon()

        # City

        self.ui.city.setText(self.weather_class.city)

        # Min Max Today

        self.ui.minmax.setText(self.weather_class.get_min() + " | " + self.weather_class.get_max())

        # 5-day forecast

        self.display_forecast()

    def display_weather_icon(self):
        wi = self.ui.weather_icon
        data = urllib.request.urlopen(self.weather_class.get_icon()).read()

        image = QtGui.QImage()
        image.loadFromData(data)
        wi.setPixmap(QPixmap(image).scaled(wi.frameGeometry().width() * 1.5, wi.frameGeometry().height() * 1.5,
                                           Qt.KeepAspectRatio, Qt.FastTransformation))

    def display_forecast(self):
        for i in self.weather_class.get_fc():
            layout = QVBoxLayout()

            # Icon
            icony = QLabel()

            icon_link = self.weather_class.icon(i['icon'])
            data = urllib.request.urlopen(icon_link).read()

            image = QtGui.QImage()
            image.loadFromData(data)
            icony.setPixmap(QPixmap(image).scaled(36, 36, Qt.KeepAspectRatio, Qt.FastTransformation))
            layout.addWidget(icony, alignment=Qt.AlignCenter | Qt.AlignBottom)
            # Temps
            minmax = QLabel()
            minmax.setText(f"{str(i['max'])}/{str(i['min'])}")
            minmax.setAlignment(Qt.AlignCenter)
            minmax.setStyleSheet('color: white')
            layout.addWidget(minmax, alignment=Qt.AlignCenter | Qt.AlignTop)

            # Date
            date = QLabel()
            date.setText(i['date'])
            date.setAlignment(Qt.AlignCenter)
            date.setStyleSheet('color: white')
            layout.addWidget(date, alignment=Qt.AlignCenter | Qt.AlignTop)

            self.ui.forecast.addLayout(layout)

    # Email

    def display_email(self):
        email_class = email_sec.Email('smtp', 'imap', 'email', 'password')
        email_class.receive()
        for mdict in email_class.show_widget():
            print(mdict)
            subj = QLabel()
            subj.setText(mdict['subject'])
            subj.setStyleSheet('color: white; font-size: 14px')

            sender = QLabel()
            sender.setText(mdict['sender'])
            sender.setStyleSheet('color: white; font-size: 11px')

            mail = QVBoxLayout()
            mail.addWidget(subj)
            mail.addWidget(sender)

            mail_frame = QFrame()
            mail_frame.setLayout(mail)
            mail_frame.setStyleSheet('background: #383838; border-radius: 5px')
            self.ui.email.addWidget(mail_frame)


if __name__ == "__main__":
    app = QApplication([])
    widget = App()
    widget.setWindowFlags(QtCore.Qt.FramelessWindowHint)

    widget.show()
    sys.exit(app.exec())
