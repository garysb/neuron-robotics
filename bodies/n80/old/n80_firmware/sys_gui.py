# Import required modules
import appuifw
import e32
import graphics
import key_codes
import sys_listener
import os

class cam_gui:
	def __init__(self, path):
		self._lock											= e32.Ao_lock()
		self._path											= unicode(path)
		self._canvas										= None
		self._loop											= 0
		self._mw											= sys_listener.image_push(self._path)
		self._bg											= graphics.Image.open(self._path + os.sep + 'img' + os.sep + 'bg.jpg')
		self._bghelp										= graphics.Image.open(self._path + os.sep + 'img' + os.sep + 'help.jpg')
		self._img											= None
		self._help											= 0

	def OnRun(self):
		appuifw.app.title									= unicode('Image push')
		appuifw.app.body									= self._canvas = appuifw.Canvas(redraw_callback=self.OnUpdate)
		self.OnUpdate(None)

		appuifw.app.menu									= [(u'Pusher...',
																((u'Start Push...', self.OnStartPhonePc),
																(u'Stop Push...', self.OnStopPhonePc))),
																(u'Exit...', self.OnExit)]
		appuifw.app.exit_key_handler						= self.OnExit

		self._eventKey()
		self._threadUI(1)

	def OnHelp(self):
		if not self._help:
			self._bghelp.text((25, 20),u'0: Help', fill=0x145326, font=u'fixed4x6')
			self._bghelp.text((25, 30),u'5: About', fill=0x145326, font=u'fixed4x6')

			self._canvas.blit(self._bghelp)
			self._help										= 1
		else:
			self._help										= 0
			self.OnUpdate(None)

	def _eventKey(self):
		self._canvas.bind(key_codes.EKey0, self.OnHelp)
		self._canvas.bind(key_codes.EKey5, self.OnAbout)

	def OnUpdate(self, rect):
		self._help											= 0
		if self._img <> None:
			self._canvas.blit(self._img, target=(10, 10, 160, 120))
		else:
			self._bg.text((147, 7), u'0: HELP', fill=0x697EEA, font=u'fixed4x6')
			self._canvas.blit(self._bg)

	def OnStartPhonePc(self):
		try:
			menuOLD											= appuifw.app.menu
			appuifw.app.exit_key_handler					= self.OnStopPhonePc
			appuifw.app.menu								= [(u'Stop Pusher...', self.OnStopPhonePc)]
			addr											= appuifw.query(u'BT Address:', 'text', u'00:00:00:00:00:00')

			if addr <> None and len(addr) == len('00:00:00:00:00:00'):
				self._mw.openSocket()
				self._mw.connect(addr, 1)
				self._loop									= 1

				while self._loop:
					self._img								= self._mw.grabPhoto()
					self.OnUpdate(None)
					self._mw.sendPhoto()
				self._mw.sendMessage('__QUIT__')
				self._mw.closeSocket()
				self._img									= None
				self.OnUpdate(None)
				appuifw.app.menu							= menuOLD
				appuifw.app.exit_key_handler				= self.OnExit
				self._cancelPhoto()
			else:
				appuifw.note(unicode('Error pushing image...'), 'error')
				appuifw.app.menu							= menuOLD
				appuifw.app.exit_key_handler				= self.OnExit
		except Exception, errore:
			appuifw.note(unicode(str(errore)), 'error')
			appuifw.app.menu								= menuOLD
			appuifw.app.exit_key_handler					= self.OnExit
			self._img										= None
			self.OnUpdate(None)
			self._loop										= 0
			try:
				self._mw.sendMessage('__QUIT__')
				self._mw.closeSocket()
			except:
				pass
			try:
				self._cancelPhoto()
			except:
				pass

	def OnStopPhonePc(self):
		self._loop											= 0
		appuifw.note(unicode('Pusher stopped'), 'info')

	def OnExit(self):
		self._loop											= 0
		self._threadUI(2)
		try:
			self._mw.sendMessage('__QUIT__')
			self._mw.closeSocket()
		except:
			pass
		appuifw.note(u'Goodbye...', 'info')

	def _threadUI(self, opz):
		try:
			if opz == 1:
				self._lock.wait()
			elif opz == 2:
				self._lock.signal()
		except:
			raise

	def _cancelPhoto(self):
		try:
			os.remove(unicode(self._path + os.sep + 'img' + os.sep + '_foto_.jpg'))
		except:
			pass
