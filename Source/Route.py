import sys
from scapy.all import *
import ipaddress
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import QObject, QThread,pyqtSignal

class Threadw(QThread): 
    fckList = list()
    fcksignal = pyqtSignal(list,QTreeWidgetItem)
    
    def __init__(self, parent,new):
        super().__init__(parent)
        self.parent = parent
        self.new = new
        
    def run(self):
        self.fckList.clear()
        to = 0
        enable = False
        
        ip = IP() #Why??????????????????????
        ip.dst = str(self.parent.tip.text())
        icmp = ICMP()
        hop = int(self.parent.hop.text())
        
        for i in range(1,hop+1): 
            if to == 4:
                self.fckList.append("Process Shutdown (Type 4)")
                self.fcksignal.emit(self.fckList,self.new)
                enable = True
                break

            ip.ttl = i
            h = sr1(ip/icmp,timeout=2,verbose=0)
            
            if h is None:
                to+=1
                self.fckList.append('*** (Fire Wall)')
            else:
                to = 0
                self.fckList.append(str(h.src))
                
                if str(h.src) == str(ip.dst):
                    self.fcksignal.emit(self.fckList,self.new)
                    enable = True
                    break
        
        if not enable:
            self.fcksignal.emit(self.fckList,self.new)

        
        self.quit()
    

class WindowClass(QMainWindow) :
    def __init__(self) :
        super().__init__()
        self.ui = uic.loadUi("route_ui.ui",self)
        self.show()
        
        self.comfirm.clicked.connect(self.run)
    
    def fcksignal_on(self,data1,new):
        cnt = 1 #old and spooky count valuable
        for i in data1:
            comp = QTreeWidgetItem(new)
            comp.setText(1,i)
            comp.setText(2,str(cnt))
            
            if i == '*** (Fire Wall)':
                comp.setText(3,'(Time out)')
            elif i=='Process Shutdown (Type 4)':
                comp.setText(4,"Mass Timeout")
            else:
                comp.setText(3,'<1ms')
            cnt += 1
                
        new.setText(0,'To {} (stat : Finished)'.format(str(self.tip.text())))
        data1.clear()
    
    def run(self,button):
        new = QTreeWidgetItem(self.treeWidget)
        
        if self.tip.text()=="" or self.hop.text()=="": #these are my insignificant warning handler
            new.setText(0,"Error (Type 1)")
            error = QTreeWidgetItem(new)
            error.setText(4,"Ip address or hop is Empty")
            return
        elif int(self.hop.text()) <=0:
            error = QTreeWidgetItem(new)
            new.setText(0,"Error (Type 3)")
            error.setText(4,"Hop number must be in range 1~")
            return
        else:
            try:
                ip_obj = ipaddress.ip_address(self.tip.text())
            except ValueError:
                error = QTreeWidgetItem(new)
                new.setText(0,"Error (Type 2)")
                error.setText(4,"Ip address is not vaild")
                return

        self.comfirm.setEnabled(False)

        self.worker = Threadw(self,new)
        self.worker.finished.connect(self.thread_fin)   
        self.worker.start()
        self.worker.fcksignal.connect(self.fcksignal_on)
        new.setText(0,'To {} (stat : Ongoing)'.format(self.tip.text()))
    
    def thread_fin(self):
        self.comfirm.setEnabled(True)
        

if __name__ == "__main__" :
    app = QApplication(sys.argv) 
    myWindow = WindowClass() 
    myWindow.show()
    app.exec_()