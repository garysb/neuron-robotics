
import appuifw
import os.path
import sys

# Setup out paths

localpath = str(os.path.split(appuifw.app.full_name())[0])
sys.path = [localpath] + sys.path

import sys_gui

if __name__ == '__main__':
	webcam = sys_gui.cam_gui(localpath)
	webcam.OnRun()

	sys.exit()
