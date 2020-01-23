from datetime import datetime,timedelta 
from scipy.interpolate import interp1d
import scipy.optimize
import math
from scipy.ndimage.morphology import binary_closing
import matplotlib.pyplot as plt
import numpy as np 

class single_diagram:
    def __init__(self,data,majorticks,unit,cycle,begin_datetime):
        self.pixelhour = None
        self.time = None
        self.measured_values = None
        self.yfunc = None
        self.detected_points_y = None
        self.detected_points_x = None
        self.data = data
        self.unit = unit
        self.correction = 'Not performed'
        self.majorticks = majorticks
        self.cycle = cycle
        self.begin_datetime = begin_datetime
    
    def find_referencesystem(self):
        """correct curvature and return function for finding x and y values"""
        if self.correction == 'Performed':
            print('Correction already performed')
            return
        def tellme(s):
            print(s)
            plt.title(s, fontsize=16)
            plt.draw()
        a = self.majorticks[0]
        b = self.majorticks[1]
        c = self.majorticks[-1]
        text = "Select intersection at %s, %s ... %s %s" %(a,b,c,self.unit)
        plt.clf()
        plt.imshow(self.data)
        plt.setp(plt.gca(), autoscale_on=False)
        
        tellme('When you are ready clik on the plot')
        number_of_points = len(self.majorticks)
        plt.waitforbuttonpress()

        while True:
            pts = []
            while len(pts) < number_of_points:
                
                tellme(text)
                pts = np.asarray(plt.ginput(number_of_points, timeout=-1))
            # plot parabola, rotated with respect to the plot
            x = pts[:,1]
            y = pts[:,0]

            def parabola(x, a, b, c):
                return a*x**2 + b*x + c
            fit_params, _ = scipy.optimize.curve_fit(parabola, x, y)
            x_fit = np.arange(math.ceil(min(x)),math.ceil(max(x))).astype(int)
            print(fit_params)
            y_fit = parabola(x_fit, *fit_params)
            plt.plot(y_fit, x_fit, label='fit')

            tellme('Click keyboard key for conferming, mouse for starting agian')

            if plt.waitforbuttonpress():
                break

        displacement = np.ceil(y_fit - min(y_fit)).astype(int)
        for ind,indx in enumerate(x_fit):
            #print(ind, indx)
            self.data[indx] = np.roll(self.data[indx],-displacement[ind],axis=0)
        plt.clf()
        plt.imshow(self.data)
        self.pts = pts
        # Curvature is corrected
        # We calculate the function for finding the y values
        f = interp1d(pts[:,1], self.majorticks, kind='cubic')
        self.yfunc = f
        # We calculate the dimension of pixel
        if  self.cycle == 'w':
            self.pixelhour = 24.*7/self.data.shape[1]
        if  self.cycle == 'd':
            self.pixelhour = 24./self.data.shape[1]
        self.correction = 'Performed'
    
    def auto_detectpoints(self):
        minarr = np.argmin(self.data[:,:,0],axis=0)
        xr = np.arange(len(minarr))
        plt.scatter(xr,minarr)
        self.detected_points_y = minarr
        self.detected_points_x =  xr
    
    def manual_detectpoints(self):
        """correct curvature and return function for finding x and y values"""
        def tellme(s):
            print(s)
            plt.title(s, fontsize=16)
            plt.draw()
        plt.clf()
        plt.imshow(self.data)
        plt.setp(plt.gca(), autoscale_on=False)
        
        tellme('Use left button to add and right to remove last point, prese ENTER to finish')
        plt.waitforbuttonpress()
        while True:
            pts = np.asarray(plt.ginput(-1, timeout=-1))
            if plt.waitforbuttonpress():
                break
        cyclelength = 0
        # in case we have multiple path we must add the previous elapsed time for each cycle
        for indx,val in enumerate(pts[1:,0]):
            # the x value is less then the previous we are begingin a new cycle
            if val < (pts[indx,0] - cyclelength):
                cyclelength += self.data.shape[1]
            pts[indx+1,0]+= cyclelength
        print('finish')           
        self.detected_points_y = pts[:,1]
        self.detected_points_x =  pts[:,0]
        
        
    #from scipy.interpolate import UnivariateSpline
    def sigmafilter(self,interpolation=False,closing=True):
        xr = np.arange(len(self.detected_points_x))
        stdRH = np.std(self.detected_points_y)
        meanRH = np.mean(self.detected_points_y)
        lowerlim = meanRH - stdRH/2
        upperlim = meanRH + stdRH/2
        print(stdRH)
        maskedval = np.ma.masked_outside(self.detected_points_y,lowerlim,upperlim)
        #spl = UnivariateSpline(xr[~maskedval.mask], minarr[~maskedval.mask],s=7,k=3)
        # We use a closing for removing small detection
        print(len(self.detected_points_y))
        print(len(maskedval))
        if closing:
            print("Closing")
            maskedval.mask = binary_closing(maskedval.mask)
            maskedval.mask[0] = True
            maskedval.mask[-1] = True
            

        if interpolation:
            print("Interpolation")
            xn = np.arange(min(xr[~maskedval.mask]), max(xr[~maskedval.mask]))
            f = interp1d(xr[~maskedval.mask], self.detected_points_y[~maskedval.mask],kind='cubic')
            f = f(xn)
        else:
            xn = xr[~maskedval.mask]
            f = self.detected_points_y[~maskedval.mask]
        
        self.detected_points_y = f
        self.detected_points_x =  xn
    
    
    def calculate_values(self):
        t = [self.begin_datetime + timedelta(hours=i*self.pixelhour) for i in self.detected_points_x]
        self.time = t
        self.measured_values = self.yfunc(self.detected_points_y)
    
    def plot(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(self.time,self.measured_values)
        ax.set_ylabel(self.unit)