from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMessageBox, QTableWidgetItem, QMainWindow
from PyQt5.QtCore import QObject, pyqtSignal, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from threading import Thread
import requests
import re
class Mysignal(QObject):
    check = pyqtSignal()
    check1 = pyqtSignal(str)
class Stats:
    def __init__(self):
        self.iddic = {"n" : "2"}
        self.subjectid = {
            "默认": "-1",
            "数学": "1",
            "化学": "2",
            "物理": "3",
            "生物": "5",
            "英语": "6",
            "语文": "7",
            "历史": "8",
            "地理": "9",
            "政治": "10"


        }
        self.type = {"1": "文本",
                     "2": "题目",
                     "4": "文件"
        }
        self.value = []
        self.detaildic = {}
        self.ms5 = Mysignal()
        self.ms3 = Mysignal()
        self.ms1 = Mysignal()
        self.ms2 = Mysignal()
        self.ms4 = Mysignal()
        self.ui = uic.loadUi("untitled.ui")
        self.ui.open.clicked.connect(self.change)
        self.ui.but1.clicked.connect(self.t1)
        self.ms1.check.connect(self.msg)
        self.ms2.check.connect(self.settext)
        self.ms3.check.connect(self.clear)
        self.ms4.check.connect(self.cl1)
        self.ms5.check.connect(self.sethtml)
        self.ui.gettask.clicked.connect(self.t2)
        self.ui.choice.clicked.connect(self.t3)
    def sethtml(self):
        self.que = self.js["questions"][self.num]["question"]
        self.browser.setHtml(self.que)
    def change(self):
        text = self.ui.cbox.currentText()
        id = self.detaildic[text]
        #初始化
        self.sonui = uic.loadUi("sonui.ui")
        self.sonui.last.clicked.connect(self.lastimage)
        self.sonui.next.clicked.connect(self.nextimage)
        url = "http://api.fuulea.com/api/paper/" + str(id) + "/"
        resp = requests.get(url=url, headers=self.headers)
        self.js = resp.json()
        self.arrlenth = len(self.js["questions"])
        self.num = 0
        #执行判断
        self.que = self.js["questions"][self.num]["question"]
        self.ui.hide()
        self.imageget()
        self.sonui.show()
    def nextimage(self):
        if self.num + 1 < self.arrlenth:
           self.num = self.num + 1
           self.ms5.check.emit()
        else:
           QMessageBox.critical(self.sonui, '错误', '已经是最后一题了！')
    def lastimage(self):
        if self.num > 0:
           self.num = self.num - 1
           self.ms5.check.emit()
        else:
           QMessageBox.critical(self.sonui, '错误', '已经是第一题了！')
    def imageget(self):
        self.ui2 = QMainWindow()
        self.ui2.resize(400, 500)
        self.ui2.move(10, 20)
        self.browser = QWebEngineView()
        self.browser.setHtml(self.que)
        self.ui2.setCentralWidget(self.browser)
        self.ui2.show()
    def cl1(self):
        self.ui.detail.setRowCount(0)
    def additem2(self, text):
        self.newitem2.setText(text)
        self.ui.detail.setItem(0, 2, self.newitem2)
    def clear(self):
        self.ui.task.clear()
    def settext(self):
        self.ui.task.addItems(self.value)
    def t1(self):
        t1 = Thread(target=self.login)
        t1.start()
    def t2(self):
        t2 = Thread(target=self.gettask_but)
        t2.start()
    def t3(self):
        t3 = Thread(target=self.lookover)
        t3.start()
    def lookover(self):
        self.ui.cbox.clear()
        self.ms4.check.emit()
        text = self.ui.task.currentItem().text()
        text = text[0:-4]
        id = self.iddic[text]
        url = "http://api.fuulea.com/api/task/" + str(id) + "/"
        res = requests.get(url=url, headers=self.headers)
        js = res.json()
        id = 1
        for x in js["detail"]:
            self.ui.detail.insertRow(0)
            iditem = QTableWidgetItem()
            iditem.setText(str(id))
            self.ui.detail.setItem(0, 0, iditem)
            self.newitem1 = QTableWidgetItem()
            self.newitem2 = QTableWidgetItem()
            try:
                ###作业 （有chapterid和title）
                self.detaildic[str(id)] = x["paper_id"]
                self.newitem1.setText("题目")
            except:
                 ###非作业 html文本或文件(无chapterid有content)
                 self.newitem1.setText("文本或文件")
                 if x["attachments"] == "  ":
                    self.detaildic[str(id)] = x["content"]
                 else:
                     self.detaildic[str(id)] = x["atteachments"][0]["source_file"]
            if x["is_finished"] == True:
                self.newitem2.setText("完成")
            else:
                self.newitem2.setText("未完成")
            try:
                newitem = QTableWidgetItem(x["title"])
                newitem.setToolTip(x["title"])
                self.ui.detail.setItem(0, 1, newitem)
            except:
               newitem3 = QTableWidgetItem("无法显示标题，请打开文件查看")
               newitem3.setToolTip("无法显示标题，请打开文件查看")
               self.ui.detail.setItem(0, 1, QTableWidgetItem(newitem3))
            self.ui.detail.setItem(0, 2, self.newitem1)
            self.ui.detail.setItem(0, 3, self.newitem2)
            self.ui.cbox.addItem(str(id))
            id = id + 1
    def msg(self):
        QMessageBox.critical(self.ui, "登录失败", self.json["msg"])
    def login(self):
        username = self.ui.username.toPlainText()
        password = self.ui.password.toPlainText()
        headers = {
            "APP-Version": "1.5.1",
            "user-agent": "apifox/2.1.8 (https://www.apifox.cn)"
        }
        data = {
            "username": username,
        "password": password
        }
        res = requests.post(url="https://api.fuulea.com/api/login/", headers=headers, data=data)
        self.json = res.json()
        if "token" in self.json:
            headers = res.headers
            self.sessionid = "sessionid=" + re.findall("sessionid=(.*?);", headers["Set-Cookie"])[0]
            print(self.sessionid)
            self.taskget()
        else:
            self.ms1.check.emit()
    def taskget(self):

            self.headers = {
                "user-agent": "apifox/2.1.8 (https://www.apifox.cn)",
                "cookie": self.sessionid,
                "version": "1.7.1"
            }
            self.taskid = ["n"]
            res = requests.get(url="https://api.fuulea.com/api/task/?finished=false&page=1&inbox=false&subjectId=-1&favorite=false", headers=self.headers)
            json = res.json()
            for x in json["data"]:
                self.iddic[x["title"]] = x["id"]
                self.value.append(x["title"] + "(" + x["subject_name"] + ")")
            self.ms2.check.emit()

    def gettask_but(self):
        self.iddic = {"n": "2"}
        self.clear()
        self.value = []
        subject = self.ui.subject.currentText()
        number = self.ui.page.value()
        gettask_url = "https://api.fuulea.com/api/task/?finished=false&page=" + str(number) + "&inbox=false&subjectId=" + self.subjectid[subject] + "&favorite=false"
        res = requests.get(url=gettask_url, headers=self.headers)
        json = res.json()
        for x in json["data"]:
            tit = x["title"]
            self.iddic[tit] = x["id"]
            self.value.append(x["title"] + "(" + x["subject_name"] + ")")
        self.ms2.check.emit()
        print(self.iddic)




if __name__ == "__main__":
    app = QApplication([])
    stats = Stats()
    stats.ui.show()
    app.exec_()