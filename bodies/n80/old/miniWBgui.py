import miniWBCServer
import os
import thread
import wx

EVENT_RESULT = wx.NewId()

def EVT_RESULT(win, func):
    
    win.Connect(-1, -1, EVENT_RESULT, func)
    
class Result(wx.PyEvent):
    
    def __init__(self, data):
        
        wx.PyEvent.__init__(self)
        self.SetEventType(EVENT_RESULT)

        self.data = data
        
class mainFrame(wx.Frame):
    
    def __init__(self, padre=None, parent=None, id=-1, title='Mini WebCam Server...', pos=wx.Point(-1, -1), size=wx.Size(500, 400), style=541072960):
        
        self._parent = padre
        self._abort = 0
        
        wx.Frame.__init__(self, parent, id, title, pos, size, style)
        self.CenterOnScreen()
        self.Show()
        
        self._sb = self.CreateStatusBar()
        
        self._menubar = wx.MenuBar()
        self._menu1 = wx.Menu()
        self._menu2 = wx.Menu()
        
        self.ID_EXIT = wx.NewId()
        self.ID_ABOUT = wx.NewId()
        self.ID_START = wx.NewId()
        self.ID_STOP = wx.NewId()
        
        self._menubar.Append(menu=self._menu1, title='&File')
        self._menubar.Append(menu=self._menu2, title='&Help')
        
        self._menu1.Append(id=self.ID_START, text='&Start WebCam...', help='Start WebCam...')
        self._menu1.Append(id=self.ID_STOP, text='S&top WebCam...', help='Stop WebCam...')
        self._menu1.Append(id=self.ID_EXIT, text='E&xit...', help='Exit...')
        self._menu2.Append(id=self.ID_ABOUT, text='A&bout...', help='About...')
        
        self.SetMenuBar(menubar=self._menubar)
        
        self.Bind(event=wx.EVT_MENU, handler=self.OnClose, id=self.ID_EXIT)
        self.Bind(event=wx.EVT_MENU, handler=self.OnAbout, id=self.ID_ABOUT)
        self.Bind(event=wx.EVT_MENU, handler=self.OnStart, id=self.ID_START)
        self.Bind(event=wx.EVT_MENU, handler=self.OnStop, id=self.ID_STOP)
        
        EVT_RESULT(self, self.OnResult)
                
        self._panel = wx.Panel(parent=self, id=-1)
        
        self.bmp = wx.Image('img/logo.jpg').ConvertToBitmap()
        self.image = wx.StaticBitmap(parent=self._panel, id=-1, bitmap=self.bmp, pos=((500-320)/2,(400-300)/2), size=(320, 240))
    
    def _setSB(self, msg=''):
            
        self._sb.SetStatusText('Fotogrammi Ricevuti: ' + msg)
    
    def _getSB(self):
        
        return self._sb.GetStatusText()
    
    def OnClose(self, event):
        
        self._parent.ExitMainLoop()
    
    def OnAbout(self, event):
        
        dlg = wx.MessageDialog(parent=self, message='Mini WebCam Server...\n\nAutore: ' + str(__author__) + '\nE-Mail: ' + str(__email__), caption='About...', style=wx.OK|wx.CENTRE)
        dlg.ShowModal()
    
    def OnStart(self, event):
        
        thread.start_new_thread(self.OnCamServer, (self, ))
    
    def OnResult(self, event):
        
        if event.data <> None:
                 
            self._setSB(str(event.data))
            
            self.bmp = wx.Image('img/fotogramma.jpg').ConvertToBitmap()
            self.image.SetBitmap(self.bmp)
            
        else:
            
            self._setSB('')
            
            self.bmp = wx.Image('img/logo.jpg').ConvertToBitmap()
            self.image.SetBitmap(self.bmp)
            
        try:
                            
            os.remove('img/fotogramma.jpg')
            
        except:
            
            pass
        
    def OnCamServer(self, frm):
        
        try:
            
            self._abort = 0
            
            WBCam = miniWBCServer.ServerWB()
            
            WBCam.openSocket()
            WBCam.bindSocket()
            WBCam.listenSocket()
            
            while True:
    
                fotogramma = 0
                client = WBCam.acceptSocket()
    
                print 'Client connesso: ' + str(client[1])
                
                try:
                    
                    os.remove('img/fotogramma.jpg')
                
                except:
                    
                    pass
                
                while not self._abort:
                    
                    data = client[0].recv(WBCam.getBufferLen())
                    
                    if data == '__FOTO_END__':
                        
                        data = ''
                        fotogramma += 1
                        f.close()
                        
                        wx.PostEvent(frm, Result(fotogramma))
                        
                    elif data <> '__QUIT__':
                        
                        f = open('img/fotogramma.jpg', 'ab')
                        f.write(data)
                        
                    elif data == '__QUIT__':
                        
                        data = ''
                        f.close()
                        
                        wx.PostEvent(frm, Result(None))
                        
                        break
                    
                WBCam.closeSocket(1)
                    
            WBCam.closeSocket(0)
                
        except Exception, errore:
            
            print str(errore)
    
    def OnStop(self, event):
        
        self._abort = 1
        
        self.bmp = wx.Image('img/logo.jpg').ConvertToBitmap()
        self.image.SetBitmap(self.bmp)
    
class miniWBgui(wx.App):
    
    def OnInit(self):
        
        self._frame = mainFrame(self)
        
        self.SetTopWindow(self._frame)
        
        return True
    