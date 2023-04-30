import numpy as np
import os.path
import time

from ctypes import *



class CameraOpenError(Exception):
    def __init__(self, mesg):
        self.mesg = mesg
    def __str__(self):
        return self.mesg

class Camera(object):
    def __init__(self):
        uc480_file = 'C:\\Program Files\\Thorlabs\\Scientific Imaging\\ThorCam\\uc480_64.dll'
        if os.path.isfile(uc480_file):        
            self.bit_depth = None
            self.roi_shape = None
            self.camera = None
            self.handle = None
            self.meminfo = None
            self.exposure = None
            self.roi_pos = None
            self.frametime = None
            self.uc480 = windll.LoadLibrary(uc480_file)
        else:
            raise CameraOpenError("ThorCam drivers not available.")

    def open(self, bit_depth=8, roi_shape=(1024, 1024), roi_pos=(0,0), camera="ThorCam FS", exposure = 0.01, frametime = 10.0):
        self.bit_depth = bit_depth
        self.roi_shape = roi_shape
        self.camera = camera
        self.roi_pos = roi_pos
        
        is_InitCamera = self.uc480.is_InitCamera
        is_InitCamera.argtypes = [POINTER(c_int)]
        self.handle = c_int(0)
        i = is_InitCamera(byref(self.handle))       

        if i == 0:
            print("ThorCam opened successfully.")
            pixelclock = c_uint(43) #set pixel clock to 43 MHz (fastest)
            is_PixelClock = self.uc480.is_PixelClock
            is_PixelClock.argtypes = [c_int, c_uint, POINTER(c_uint), c_uint]
            is_PixelClock(self.handle, 6 , byref(pixelclock), sizeof(pixelclock)) #6 for setting pixel clock
            
            self.uc480.is_SetColorMode(self.handle, 6) # 6 is for monochrome 8 bit. See uc480.h for definitions
            self.set_roi_shape(self.roi_shape)
            self.set_roi_pos(self.roi_pos)
            self.set_frametime(frametime)
            self.set_exposure(exposure)
        else:
            raise CameraOpenError("Opening the ThorCam failed with error code "+str(i))


    def close(self):
        if self.handle != None:
            self.stop_live_capture()
            i = self.uc480.is_ExitCamera(self.handle) 
            if i == 0:
                print("ThorCam closed successfully.")
            else:
                print("Closing ThorCam failed with error code "+str(i))
        else:
            return

    def get_image(self, buffer_number=None):
        #buffer number not yet used
        #if buffer_number is None:
        #    buffer_number = self.epix.pxd_capturedBuffer(1)

        im = np.frombuffer(self.meminfo[0], c_ubyte).reshape(self.roi_shape[1], self.roi_shape[0])

        
        return im

    def get_frame_number(self):
        #not implemented for thorcam_fs 
        #return self.epix.pxd_capturedBuffer(0x1,1)-1

       return 1

    def finished_live_sequence(self):
        #not implemented for thorcam_fs 
        #return self.epix.pxd_goneLive(0x1) == 0
        return 0

    def start_continuous_capture(self, buffersize = None):

        '''
        buffersize: number of frames to keep in rolling buffer
        '''

        self.uc480.is_CaptureVideo(self.handle, 1)

    def start_sequence_capture(self, n_frames):
        #not implemented for thorcam_fs 
        print('sequence capture started')
        #self.epix.pxd_goLiveSeq(0x1,1,n_frames,1,n_frames,1)

    def stop_live_capture(self, ):
        print('unlive now')
        #self.epix.pxd_goUnLive(0x1)
        self.uc480.is_StopLiveVideo(self.handle, 1)
        
    def initialize_memory(self):
        if self.meminfo != None:
            self.uc480.is_FreeImageMem(self.handle, self.meminfo[0], self.meminfo[1])
        
        xdim = self.roi_shape[0]
        ydim = self.roi_shape[1]
        imagesize = xdim*ydim
            
        memid = c_int(0)
        c_buf = (c_ubyte * imagesize)(0)
        self.uc480.is_SetAllocatedImageMem(self.handle, xdim, ydim, 8, c_buf, byref(memid))
        self.uc480.is_SetImageMem(self.handle, c_buf, memid)
        self.meminfo = [c_buf, memid]

        
    def set_bit_depth(self, set_bit_depth = 8):
         if set_bit_depth != 8:
            print("only 8-bit images supported")
    
    def set_roi_shape(self, set_roi_shape):
        class IS_SIZE_2D(Structure):
            _fields_ = [('s32Width', c_int), ('s32Height', c_int)]
        AOI_size = IS_SIZE_2D(set_roi_shape[0], set_roi_shape[1]) #Width and Height
            
        is_AOI = self.uc480.is_AOI
        is_AOI.argtypes = [c_int, c_uint, POINTER(IS_SIZE_2D), c_uint]
        i = is_AOI(self.handle, 5, byref(AOI_size), 8 )#5 for setting size, 3 for setting position
        is_AOI(self.handle, 6, byref(AOI_size), 8 )#6 for getting size, 4 for getting position
        self.roi_shape = [AOI_size.s32Width, AOI_size.s32Height]
        
        if i == 0:
            print("ThorCam ROI size set successfully.")
            self.initialize_memory()
        else:
            print("Set ThorCam ROI size failed with error code "+str(i))

    def set_roi_pos(self, set_roi_pos):
        class IS_POINT_2D(Structure):
            _fields_ = [('s32X', c_int), ('s32Y', c_int)]
        AOI_pos = IS_POINT_2D(set_roi_pos[0], set_roi_pos[1]) #Width and Height
            
        is_AOI = self.uc480.is_AOI
        is_AOI.argtypes = [c_int, c_uint, POINTER(IS_POINT_2D), c_uint]
        i = is_AOI(self.handle, 3, byref(AOI_pos), 8 )#5 for setting size, 3 for setting position
        is_AOI(self.handle, 4, byref(AOI_pos), 8 )#6 for getting size, 4 for getting position
        self.roi_pos = [AOI_pos.s32X, AOI_pos.s32Y]
        
        if i == 0:
            print("ThorCam ROI position set successfully.")
        else:
            print("Set ThorCam ROI size failed with error code "+str(i))
    
    def set_exposure(self, exposure):
        #exposure should be given in ms
        exposure_c = c_double(exposure)
        is_Exposure = self.uc480.is_Exposure
        is_Exposure.argtypes = [c_int, c_uint, POINTER(c_double), c_uint]
        is_Exposure(self.handle, 12 , exposure_c, 8) #12 is for setting exposure
        self.exposure = exposure_c.value
    
    def set_frametime(self, frametime):
        #must reset exposure after setting framerate
        #frametime should be givin in ms. Framerate = 1/frametime
        is_SetFrameRate = self.uc480.is_SetFrameRate 
        
        if frametime == 0: frametime = 0.001
        
        set_framerate = c_double(0)
        is_SetFrameRate.argtypes = [c_int, c_double, POINTER(c_double)]
        is_SetFrameRate(self.handle, 1.0/(frametime/1000.0), byref(set_framerate))
        self.frametime = (1.0/set_framerate.value*1000.0)

if __name__ == '__main__':
    import matplotlib.pyplot as plt

    plt.figure()

    cam = Camera()
    cam.open()
    cam.initialize_memory()
    cam.set_exposure(10e5)
    cam.start_continuous_capture(1)
    print(cam.bit_depth)
    img = cam.get_image()
    cam.stop_live_capture()
    cam.close()
    print(img)
    plt.imshow(img)
    plt.show()
