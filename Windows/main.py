"""
Required packages
"""
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
#sys.modules['PyQt4.QtGui'] = PySide.QtGui
from PIL import Image
from PIL.ImageQt import ImageQt
import os
import socket
import timeit
import numpy as np
"""
Import GUI elements
"""
import main_window
import image_window

"""
Import other files
"""
"""
Main define
"""
app = QApplication(sys.argv)
def main():
    #app = QApplication(sys.argv)
    SLM_Image = MainDialog()
    SLM_Image.show()
    app.exec_()
"""
Main Dialog class
"""
class MainDialog(QMainWindow, main_window.Ui_main_window):
    def __init__(self, parent = None):
        super(MainDialog, self).__init__(parent)
        self.setupUi(self)
        
        """
        Initialize support classes
        """
        self.imageManager = Image_Manager()
        self.imageManager.start()
        self.tcpip_host = TCPIP_Host()
        self.showing_image = False
        """
        Define Variables
        """
        self.paths = np.array([])
        self.LW_paths.show()
        self.curent_index = -1
        self.showing_index = -1
        self.h_val = 0.0
        self.v_val = 0
        self.g_val = 255
        self.swap_gray_bool = self.CB_graySwap.isChecked()
        self.host_on = False
        
        self.current_image_data = np.zeros((1,1))
        self.next_image_data = np.zeros((1,1))
        """
        DEFINE CONNECTIONS
        """
        self.tcpip_host.signal_swap.connect(self.image_swap, Qt.QueuedConnection)        
        self.tcpip_host.signal_reset.connect(self.reset_image, Qt.QueuedConnection)
        self.tcpip_host.signal_gray_change.connect(self.host_update_gray,Qt.QueuedConnection)
        self.tcpip_host.signal_h_change.connect(self.host_update_horizontal,Qt.QueuedConnection)
        self.tcpip_host.signal_v_change.connect(self.host_update_vertical,Qt.QueuedConnection)
        self.tcpip_host.signal_gray_swap.connect(self.host_swap_gray, Qt.QueuedConnection)        
        
        #self.connect(self.PB_StartHost, SIGNAL("clicked()"),self.start_host)
        self.PB_StartHost.clicked.connect(self.start_host)
        #self.connect(self.PB_stopHost, SIGNAL("clicked()"),self.stop_host)
        self.PB_stopHost.clicked.connect(self.stop_host)
        
        #self.connect(self.PB_addImage, SIGNAL("clicked()"),self.add_image)
        self.PB_addImage.clicked.connect(self.add_image)
        #self.connect(self.PB_removeImage, SIGNAL("clicked()"), self.remove_image)
        self.PB_removeImage.clicked.connect(self.remove_image)
        #self.connect(self.PB_showImage, SIGNAL("clicked()"), self.show_image)
        self.PB_showImage.clicked.connect(self.show_image)
        #self.connect(self.PB_imageClose, SIGNAL("clicked()"),self.image_close)
        self.PB_imageClose.clicked.connect(self.image_close)
        
        self.SB_horizontal.valueChanged.connect(self.update_horizontal)
        self.Slide_Horizontal.valueChanged.connect(self.update_horizontal)   
        self.SB_vertical.valueChanged.connect(self.update_vertical)
        self.Slide_Vertical.valueChanged.connect(self.update_vertical)
        self.SB_gray.valueChanged.connect(self.update_gray)
        self.Slide_Gray.valueChanged.connect(self.update_gray)
        self.CB_graySwap.stateChanged.connect(self.swap_gray)
        """
        DEFINE CONNECTION FUNCTIONS
        """
        self.TB_host.appendPlainText("Welcome to SLM-HOST-MASTER-9001")
        self.TB_host.appendPlainText("Your host name is: "+self.tcpip_host.host)
        self.TB_host.appendPlainText("Your IP is: "+str(socket.gethostbyname(socket.gethostname()))) 
        #self.TB_host.appendPlainText("Your IP is: "+str(socket.gethostbyname(socket.getfqdn())))
        self.TB_host.appendPlainText("Your port number is: "+str(self.tcpip_host.port))
    """
    Host functions
    """   
    def start_host(self):
        self.tcpip_host.setTerminationEnabled(True)
        self.tcpip_host.start()
        self.TB_host.appendPlainText("Listening")
        self.host_on = True
        
    def stop_host(self):
        self.tcpip_host.host_stop()
        self.TB_host.appendPlainText("Stopped\n")
        self.host_on = False
    
    def add_image(self):
        dir = "."
        fileObj = QFileDialog.getOpenFileNames(self,"Image Selection", directory=dir)
        for path in fileObj[0]:
            imgPath = str(path)            
            self.paths = np.append(self.paths,imgPath)
            self.update_image_slection()
    """
    Image list functions
    """
    def remove_image(self):
        index = -1
        index = self.LW_paths.currentRow()
        if index==-1:
            print("Select item to delete")
        else:
            self.paths = np.delete(self.paths,index)
            self.update_image_slection()

    def update_image_slection(self):
        self.LW_paths.clear()
        for i in self.paths:
            path = i
            path = QListWidgetItem(path)
            self.LW_paths.addItem(path)
        self.LW_paths.show()
    """
    Image showing functions
    """  
    def show_image(self):
        self.curent_index = -1        
        self.curent_index = self.LW_paths.currentRow()
        if (self.curent_index == -1):
            print("Select Item to View")
        else:
            path = self.paths[self.curent_index]
            self.current_image_data, data = self.imageManager.process_all(path,self.h_val,self.v_val,self.g_val,self.swap_gray_bool)
            self.currentPM = self.pm_from_data(data)
            h,w = self.current_image_data.shape
            self.image_window = Image_Window(self.currentPM, w+4, h+4)
            self.showing_image = True
            self.showing_index = self.curent_index
            
            if(self.showing_index+1 < len(self.paths) and len(self.paths)>1):
                path = self.paths[self.showing_index+1]
                self.next_image_data, data = self.imageManager.process_all(path,self.h_val,self.v_val,self.g_val,self.swap_gray_bool)
                self.nextPM = self.pm_from_data(data)
            elif(self.showing_index+1 >= len(self.paths) and len(self.paths)>1):
                path = self.paths[0]
                self.next_image_data, data = self.imageManager.process_all(path,self.h_val,self.v_val,self.g_val,self.swap_gray_bool)
                self.nextPM = self.pm_from_data(data)
            #if self.image_window.exec_():
            #    print "OK" 
                
    def image_swap(self, sig):
        #print(sig)
        if (self.CB_hostSwap.isChecked() and self.showing_image):
#            timeit.timeit('self.image_window.change_image(self.nextPM)')
            self.image_window.change_image(self.nextPM)
            self.current_image_data = self.next_image_data
            self.currentPM = self.nextPM
            self.showing_index = self.showing_index + 1
            if(self.showing_index >= len(self.paths)):
                self.showing_index = 0
            if (self.showing_index+1<len(self.paths)):
                path = self.paths[self.showing_index+1]
                self.next_image_data, data = self.imageManager.process_all(path,self.h_val,self.v_val,self.g_val,self.swap_gray_bool)
                self.nextPM = self.pm_from_data(data)
            else: 
                path = self.paths[0]
                self.next_image_data, data = self.imageManager.process_all(path,self.h_val,self.v_val,self.g_val,self.swap_gray_bool)
                self.nextPM = self.pm_from_data(data)

            self.TB_host.appendPlainText("Got message to swap")    
            self.TB_host.appendPlainText("Listening")
            print(self.showing_index)
        else:
            print("Need to show image")      
            
    def image_close(self):
        self.image_window.close()    
        self.showing_image = False
        
    def reset_image(self):
        if (self.CB_hostSwap.isChecked() and self.showing_image):
            self.TB_host.appendPlainText("Got message to reset image")
            index = self.LW_paths.currentRow()
            path = self.paths[index]
            self.current_image_data, data  = self.imageManager.process_all(path,self.h_val,self.v_val,self.g_val,self.swap_bool)
            self.curentPM = self.pm_from_data(self.data)            
            self.image_window.change_image(self.curentPM)
            self.TB_host.appendPlainText("Listening")
#            self.showing_index = index
        else:
            print("Need to show image")
            
    def read_conenction(self, sig):
        print(sig)
        
    """
    Image modifying functions
    """
    def update_horizontal(self):
        
        if(self.h_val == self.SB_horizontal.value()):
            self.h_val = self.Slide_Horizontal.value()
            self.SB_horizontal.setValue(self.Slide_Horizontal.value())
            
        elif(self.h_val == self.Slide_Horizontal.value()):
            self.h_val = self.SB_horizontal.value()
            self.Slide_Horizontal.setValue(self.SB_horizontal.value()) 
        #self.imageManager.modifty_image_x(self.h_val)
        self.update_image()
    
    def host_update_horizontal(self,val):
        if (self.host_on and (-1280<val<1280)):
            self.SB_horizontal.setValue(val)
        else:
            print("recieved signal to change horizontal however host is not on or value out of bounds")
    
    def update_vertical(self):
        if(self.v_val == self.SB_vertical.value()):
            self.v_val = self.Slide_Vertical.value()
            self.SB_vertical.setValue(self.Slide_Vertical.value())
            
        elif(self.v_val == self.Slide_Vertical.value()):
            self.v_val = self.SB_vertical.value()
            self.Slide_Vertical.setValue(self.SB_vertical.value())
        #self.imageManager.modifty_image_y(self.v_val)
        self.update_image()
        
    def host_update_vertical(self,val):
        if (self.host_on and (-768<val<768)):
            self.SB_vertical.setValue(val)
        else:
            print("recieved signal to change vertical however host is not on or value out of bounds")
        
    def update_gray(self):
        if(self.g_val == self.SB_gray.value()):
            self.g_val = self.Slide_Gray.value()
            self.SB_gray.setValue(self.Slide_Gray.value())
            
        elif(self.g_val == self.Slide_Gray.value()):
            self.g_val = self.SB_gray.value()
            self.Slide_Gray.setValue(self.SB_gray.value())
        #self.imageManager.modifty_image_gray(self.g_val)
        self.update_image()
    
    def host_update_gray(self,val):
        if (self.host_on and (0<val<256)):
            self.SB_gray.setValue(val)
        else:
            print("recieved signal to change gray however host is not on or value out of bounds")
        
    def swap_gray(self):
        self.swap_gray_bool = self.CB_graySwap.isChecked()
        #self.imageManager.modifty_image_swap(self.CB_graySwap.isChecked())
        self.update_image()
        
    def host_swap_gray(self,val):
        val = bool(val)
#        if (self.swap_gray_bool):
#            check = False
#        else:
#            check = True
        self.CB_graySwap.setChecked(val)
        
    def update_image(self):
        if self.showing_image:
            data = self.imageManager.process_curent_events(self.current_image_data, self.h_val , self.v_val, self.g_val,self.swap_gray_bool)
            self.currentPM = self.pm_from_data(data)            
            self.image_window.change_image(self.currentPM)
            data = self.imageManager.process_curent_events(self.next_image_data, self.h_val , self.v_val, self.g_val,self.swap_gray_bool)
            self.nextPM = self.pm_from_data(data)
            
    def pm_from_data(self,data):
        img = Image.fromarray(data)
        data.flatten() 
        #img.show()
        img = ImageQt(img)
        pixMap = QPixmap.fromImage(img)        
        return pixMap
                         
"""
IMAGE MANAGER
"""

class Image_Manager(QThread):
    def __init__(self, parent = None):
        super(Image_Manager, self).__init__(parent)
              
    def run(self):
        self.manager_imageData = np.zeros((1,1))
        self.manager_modImage = np.zeros((1,1))

    def modifty_image_x(self,x_val):
        #Do X
        self.manager_modImage = np.roll(self.manager_modImage, int(x_val), axis = 1)
               
    def modifty_image_y(self,y_val):
        #Do Y
        self.manager_modImage = np.roll(self.manager_modImage, int(y_val), axis = 0)
        
    def modifty_image_gray(self,gray_val):        
        #Do gray
        self.manager_modImage = (self.manager_modImage*(gray_val/255)).astype(np.uint8)

    def modifty_image_swap(self):        
        #Do swap
        self.manager_modImage = (-1*(self.manager_modImage-255)).astype(np.uint8)
    
    def set_image(self,path):
        im = Image.open(path).convert('L')
        data = np.array(im.getdata()).astype(int)
        sx,sy = im.size
        self.manager_imageData = np.reshape(data,(sy,sx))
        self.manager_modImage = np.reshape(data,(sy,sx))
    
    def return_image_data(self):
        return self.manager_modImage
    
#    def manipulate_start(self):
#        self.manager_modImage = self.manager_imageData
    
    def process_all(self,path,x_val,y_val,gray,swap):
#        self.manipulate_start()
        self.set_image(path)
        self.modifty_image_x(x_val)
        self.modifty_image_y(y_val)
        self.modifty_image_gray(gray)
        if swap:
            self.modifty_image_swap()
        return self.manager_imageData, self.manager_modImage
   
    def process_curent_events(self, data, x_val, y_val, gray, swap):
        self.manager_modImage = data        
        self.modifty_image_x(x_val)
        self.modifty_image_y(y_val)
        self.modifty_image_gray(gray)
        if swap:
            self.modifty_image_swap()
        return self.manager_modImage
        
"""
TCPIP HOST
"""  
class TCPIP_Host(QThread):
    signal_swap = pyqtSignal(str)
    signal_reset = pyqtSignal(str)
    signal_gray_change = pyqtSignal(int)
    signal_h_change = pyqtSignal(int)
    signal_v_change = pyqtSignal(int)
    signal_gray_swap = pyqtSignal(int)
    
    def __init__(self):
        #super(TCPIP_Host, self).__init__(parent)
        QThread.__init__(self,parent = app)
        self.__s__ = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        #self.host = socket.gethostname()
        self.host = ''
        self.__s__.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        self.port = 12345
        self.listen_b = True
                
    def run(self):
        self.__s__.bind((self.host, self.port))
        #self.__s__.listen(5)
        print("Started client with host name: " + self.host)
        while self.listen_b:
            c, addr = self.__s__.recvfrom(256)
            #print('Got connection from' , addr)
            #print(c)
            msg = c.decode("utf-8")
            #print(msg)
            if (msg == "swap"):
                self.signal_swap.emit(msg)
            elif (msg == "reset"):
                self.signal_reset.emit(msg)
            elif (msg[0:4] == "gray"):
                value = int(msg[4:len(msg)])
                self.signal_gray_change.emit(value)
            elif (msg[0:7] == "hchange"):
                value = int(msg[7:len(msg)])
                self.signal_h_change.emit(value)
            elif (msg[0:7] == "vchange"):
                value = int(msg[7:len(msg)])
                self.signal_v_change.emit(value)
            elif (msg[0:8] == "swapgray"):
                value = int(msg[8])
                self.signal_gray_swap.emit(value)
                
    def host_stop(self):
        self.listen_b = False        
        self.__s__.close()
        self.listen_b = True
        self.quit()

"""
IMAGE WINDOW
"""
      
class Image_Window(QDialog, image_window.Ui_image_window):
    def __init__(self, pixMap, w, h):
        super(Image_Window,self).__init__(None)
        self.gray_color_table = [qRgb(i, i, i) for i in range(256)]
        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        self.desk = QDesktopWidget()
        self.rect = QRect(self.desk.screenGeometry(1))
        self.move(self.rect.left(),self.rect.top())        
        self.resize(self.rect.width(),self.rect.height())
        self.showMaximized()        
        
        self.scene = QGraphicsScene()
        self.image_space.setScene(self.scene)
        
        #h,w = data_vals.shape
        #data_vals.flatten()    
        
        #self.img = Image.fromarray(data_vals)
        #self.img.show()
        #self.img = ImageQt(self.img)
        self.image_space.resize(w,h)
        #pixMap = QPixmap.fromImage(self.img)        
        self.scene.addPixmap(pixMap)
        self.scene.update()
        QCoreApplication.processEvents()
        
    def change_image(self,pixMap):
               
#        h,w = data_vals.shape        
#        self.img = ImageQt(Image.fromarray(data_vals))
#        self.image_space.resize(w+10,h+10)
#        pixMap = QPixmap.fromImage(self.img)
        self.scene.clear()        
        self.scene.addPixmap(pixMap)
        self.scene.update()
        QCoreApplication.processEvents()
        
if __name__ == "__main__":
    main()