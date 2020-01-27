from datetime import datetime,timedelta 
from scipy.interpolate import interp1d
import scipy.optimize
import math
from scipy.ndimage.morphology import binary_closing
import matplotlib.pyplot as plt
import numpy as np 
import os

class single_diagram:
    def __init__(self,data,majorticks,unit,cycle,begin_datetime,time_offset):
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
        self.time_offset = time_offset
        self.sampled_points = None
        plt.rcParams["figure.figsize"] = (20,17)
    
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
        plt.draw()
        self.pts = pts
        # Curvature is corrected
        # We calculate the function for finding the y values
        f = interp1d(pts[:,1], self.majorticks, kind='cubic')
        self.yfunc = f
        # We calculate the dimension of pixel
        self.pixelhour = 24.*self.cycle/self.data.shape[1]
        self.correction = 'Performed'
    
    def auto_detectpoints(self):
        minarr = np.argmin(self.data[:,:,0],axis=0)
        xr = np.arange(len(minarr))
        plt.scatter(xr,minarr)
        self.detected_points_y = minarr
        self.detected_points_x =  xr
    
    def manual_sampling(self,plot=True):
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
                plt.close()
                break
        self.sampled_points = pts

    def manual_detectpoints(self,distance_treshold = 15,blue_threshold=50,interpolation=True,plot=True):
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
                plt.close()
                break
        # check if x values are sorted        
        if not all(pts[i,0] <= pts[i+1,0] for i in range(len(pts[:,0])-1)):
            cyclelength = 0
            # in case we have multiple path we must add the previous elapsed time for each cycle
            for indx,val in enumerate(pts[1:,0]):
                # the x value is less then the previous we are begingin a new cycle
                if val < (pts[indx,0] - cyclelength):
                    cyclelength += self.data.shape[1]
                pts[indx+1,0]+= cyclelength
            print("Cycle correction performed")
 
        if interpolation:
            f = interp1d(pts[:,0],pts[:,1],kind='linear')
            # this correspond to the columns
            minx, maxx = math.ceil(min(pts[:,0])),math.ceil(max(pts[:,0]))
            xran = np.arange(minx,maxx).astype(int)
            ynew = f(xran)
        
            y_detected = []
            # we iterate on the original x positions and for each column we select the points
            for idx,column in enumerate(xran):
                column = column%self.data.shape[1]
                indexes_detected = np.argwhere(self.data[:,column,0] < blue_threshold)
                # calculate the distances between the interpolated control point
                distances = np.abs(indexes_detected - ynew[idx])
                indx_close = np.argwhere(distances < distance_treshold)
                if len(indx_close) == 0:
                    # No pixel are close to the control path
                    # we keep the interpolated control point
                    y_detected.append(ynew[idx])
                else:
                    # Otherwise we keep the closest point to the interpolated value
                    index_of_the_closest = np.argmin(distances)
                    y_detected.append(indexes_detected[index_of_the_closest][0])
            self.detected_points_y = np.array(y_detected)
            self.detected_points_x = xran
        else:          
            self.detected_points_y = pts[:,1]
            self.detected_points_x =  pts[:,0]
        if plot:
            self.plot_detected()
        
        
    # from scipy.interpolate import UnivariateSpline
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
        t = [self.begin_datetime + timedelta(hours=i*self.pixelhour+self.time_offset) for i in self.detected_points_x]
        self.time = t
        self.measured_values = self.yfunc(self.detected_points_y)

    def export_data(self,path=None,filename=None):
        if filename == None:
            filename = "%s_%s.csv" %(self.begin_datetime,self.unit)
        if path == None:
            path = os.getcwd()
        filename = os.path.join(path,filename) 
        with open(filename,'w') as f:
            f.write(self.unit+'\n')
            for i in range(len(self.measured_values)):
                f.write("%s , %s \n" %(self.time[i],
                                    self.measured_values[i]))
            
    def plot_detected(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(self.detected_points_x,self.detected_points_y)
        orgpts = np.mod(self.detected_points_x,self.data.shape[1])
        ax.scatter(orgpts,self.detected_points_y)
        ax.imshow(self.data)
        ax.set_ylabel(self.unit)

    def plot_extracted(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(self.time,self.measured_values)
        ax.set_ylabel(self.unit)