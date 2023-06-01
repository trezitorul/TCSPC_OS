import sys
import  time

sys.path.append("C:\\Users\\Ozymandias\\TCSPC_project\\LAC")
sys.path.append("C:\\Users\\Ozymandias\\TCSPC_project\\MFF101FlipperMirror")
from LAC import LAC
from MFF101FlipperMirror import MFF101FlipperMirror
cameraFlipperID = "37005411"
cameraFlipper = MFF101FlipperMirror(cameraFlipperID)
#mirror.HomeMirror()
beamBlockFlipperID = "37005466"
beamBlockFlipper = MFF101FlipperMirror(beamBlockFlipperID)

cameraFlipper.SetMode("off")
beamBlockFlipper.SetMode("off")
#time.sleep(1)
lac = LAC()
time.sleep(1)
lac.set_position(int(0.9*1023))