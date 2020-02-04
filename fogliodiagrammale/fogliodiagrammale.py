import matplotlib
matplotlib.use('Qt4Agg')
from singlediagram import single_diagram
from datetime import datetime,timedelta 
import matplotlib.pyplot as plt
import numpy as np
import os
import json
import time

try:
    input = raw_input
except NameError:
    pass

class fogliodiagrammale(object):
    def __init__(self,sheet_image):
        self.sheet_image = sheet_image
        self.instrument_model = None
        self.temperature_plot = None
        self.relativehumidity_plot = None
        self.cycle_duration = None 
        self.begin_datetime = None
        self.time_offset = 0
        self.location = None
        self.station = None
        self.ROI_RH = None
        self.ROI_T = None
        self.ROI_date = None
        self.ROI_location = None
        self.ROI_header = None
        self.coordsROI_RH = None
        self.coordsROI_T = None
        self.coordsROI_date = None
        self.coordsROI_location = None
        self.coordsROI_header = None
        self.end_datetime = None


    def extract_plots(self,titles = None):
        if titles is None:
            titles = ['Relative Humidity plot','location','date','temperature plot',]
        c = [0]
        from matplotlib.widgets import RectangleSelector
        fig, current_ax = plt.subplots(figsize=(20,7))
        current_ax.imshow(self.sheet_image)
        current_ax.set_title("Drag a ROI over %s (r to restart)" %titles[c[0]])
        
        def line_select_callback(eclick, erelease):
            
            'eclick and erelease are the press and release events'
            x1, y1 = int(eclick.xdata), int(eclick.ydata)
            x2, y2 = int(erelease.xdata), int(erelease.ydata)  
            print("%s = img[%s:%s,%s:%s]"% (titles[c[0]], y1, y2, x1, x2))
            if titles[c[0]] == 'Relative Humidity plot':
                self.ROI_RH = self.sheet_image[y1:y2,x1:x2]
                self.coordsROI_RH = [y1,y2,x1,x2]
            if titles[c[0]] == 'location':
                self.ROI_location = self.sheet_image[y1:y2,x1:x2]
                self.coordsROI_location = [y1,y2,x1,x2]
            if titles[c[0]] == 'date':
                self.ROI_date = self.sheet_image[y1:y2,x1:x2]
                self.coordsROI_date = [y1,y2,x1,x2]
            if titles[c[0]] == 'temperature plot':
                self.ROI_T = self.sheet_image[y1:y2,x1:x2]
                self.coordsROI_T = [y1,y2,x1,x2]
                plt.close(fig)
                return
            c[0]+=1
            current_ax.set_title("Drag a ROI over %s" %titles[c[0]])  
            fig.canvas.draw()
            fig.canvas.flush_events()
            time.sleep(1)
            print("c%s" %c[0])
            

        def toggle_selector(event):
            print(' Key pressed.')
            if event.key in ['Q', 'q'] and toggle_selector.RS.active:
                print(' RectangleSelector deactivated.')
                toggle_selector.RS.set_active(False)
            if event.key in ['A', 'a'] and not toggle_selector.RS.active:
                print(' RectangleSelector activated.')
                toggle_selector.RS.set_active(True)
            # if event.key in ['R', 'r'] and not toggle_selector.RS.active:
            #     print(' RectangleSelector activated.')
            #     c[0] = 0
            # if event.key in ['B', 'b'] and not toggle_selector.RS.active:
            #     print(' RectangleSelector activated.')
            #     c[0] -=1

            print("\n      click  -->  release")

        # drawtype is 'box' or 'line' or 'none'
        toggle_selector.RS = RectangleSelector(current_ax, line_select_callback,
                                            drawtype='box', useblit=True,
                                            # don't use middle button
                                            button=[1, 3],
                                            minspanx=5, minspany=5,
                                            spancoords='pixels',)
        plt.connect('key_press_event', toggle_selector)

        plt.show()
    
    def extract_singleplot(self,title):
        from matplotlib.widgets import RectangleSelector
        fig, current_ax = plt.subplots(figsize=(20,7))
        current_ax.imshow(self.sheet_image)
        current_ax.set_title("Drag a ROI over %s " %title)
        coords = []
        def line_select_callback(eclick, erelease):
            
            'eclick and erelease are the press and release events'
            x1, y1 = int(eclick.xdata), int(eclick.ydata)
            x2, y2 = int(erelease.xdata), int(erelease.ydata)  
            plt.close(fig)
            ROI = self.sheet_image[y1:y2,x1:x2]
            return ROI,(y1, y2, x1, x2)       
            
        def toggle_selector(event):
            print(' Key pressed.')
            if event.key in ['Q', 'q'] and toggle_selector.RS.active:
                print(' RectangleSelector deactivated.')
                toggle_selector.RS.set_active(False)
            if event.key in ['A', 'a'] and not toggle_selector.RS.active:
                print(' RectangleSelector activated.')
                toggle_selector.RS.set_active(True)

        # drawtype is 'box' or 'line' or 'none'
        toggle_selector.RS = RectangleSelector(current_ax, line_select_callback,
                                            drawtype='box', useblit=True,
                                            # don't use middle button
                                            button=[1, 3],
                                            minspanx=5, minspany=5,
                                            spancoords='pixels',)
        plt.connect('key_press_event', toggle_selector)

        plt.show()

    def extract_temperatureplot(self):
        img, coords = self.extract_singleplot('temperature plot')
        self.ROI_T = img
        self.coordsROI_T = coords
    
    def extract_relativehumidityplot(self):
        img, coords = self.extract_singleplot('relative humidity plot')
        self.ROI_RH = img
        self.coordsROI_RH = coords

    def wizard(self,cycle_duration=None,locationdict=None, header_xcoords=None):
        plt.ion()
        if header_xcoords is not None:
            xi,xf = header_xcoords
            self.ROI_header = self.sheet_image[:,xi:xf]
            yf = self.sheet_image.shape[0]
            self.coordsROI_header = [0,yf,xi,xf]
            fig = plt.figure(figsize=(12,8))
            ax = fig.add_subplot(111)
            ax.imshow(np.rot90(self.ROI_header,-1))
        else:
            fig = plt.figure(figsize=(12,8))
            ax = fig.add_subplot(121)
            ax.imshow(np.rot90(self.ROI_location,-1))
            ax2 = fig.add_subplot(122)
            ax2.imshow(np.rot90(self.ROI_date,-1))
        plt.show()
        if locationdict != None:
            text="Input the location number of the entry or a new location: "
            self.location = self._dictchoice(locationdict,text=text,retk=True)
        else:
            self.location = input("Write location: ")
        self.instrument_model = self._select_instrument()
        bd = True
        while bd:
            try:
                begin_date = input ("Write begin date using spaces e.g. 1988 12 31 15 30 : ")
                begin_date = map(int,begin_date.split())
                bd = False
            except ValueError:
                print('Date in wrong format!')
        self.begin_datetime = datetime(*begin_date)
        end_date = input ("Write end date using spaces e.g. 1988 12 31 15 30 or press enter to continue: ")
        if end_date != '':
            end_date = map(int,end_date.split())
            self.end_datetime = datetime(*end_date)
        self.cycle_duration = cycle_duration
        if cycle_duration == None:
            self.cycle_duration = int(input("Duration of a rotation of the cylinder in days: "))
        # if hours are not provided the hours are calculated from the position on the plot
        if len(begin_date) < 4: # three etries means that only  years, months and day is provided
            print("No hours found") # debug
            if self.cycle_duration > 1: 
                 print("Isoline for daily cycle used")   # debug     
                 self.time_offset= self.instrument_model["first_complete_isoline_weekly_cycle"]
            else:
                 self.time_offset=self.instrument_model["first_complete_isoline_daily_cycle"]
                 print("Isoline for weekly cycle used")   # debug
       
        
        
        plt.ioff()
        plt.close()
        # Here we create the single diagram object
        self.temperature_plot = single_diagram(data=self.ROI_T,
                                majorticks=self.instrument_model["temperature ticks C"],
                                unit='degC',
                                cycle=self.cycle_duration,
                                begin_datetime=self.begin_datetime,
                                time_offset = self.time_offset,
                                reported_end_datetime = self.end_datetime
                                )
        self.relativehumidity_plot = single_diagram(data=self.ROI_RH,
                                majorticks=self.instrument_model["relative humidity ticks"],
                                unit='percentageRH',
                                cycle=self.cycle_duration,
                                begin_datetime=self.begin_datetime,
                                time_offset = self.time_offset,
                                reported_end_datetime = self.end_datetime
                                )
    
    def export_data(self,path=None,filename=None):
        if filename == None:
            filename = "chart_%s_%s.csv" %(self.begin_datetime,self.location)
        if path == None:
            path = os.getcwd()
        filename = os.path.join(path,filename) 
        with open(filename,'w') as f:
            f.write("manufacturer : %s \n" %self.instrument_model["manufacturer"])
            f.write("model : %s \n" %self.instrument_model["model"])
            f.write("location : , %s\n" %self.location)
            f.write("coords RH plot:  %s\n" %self.coordsROI_RH)
            f.write("coords T plot: %s\n" %self.coordsROI_T)
            f.write("coords date: %s\n" %self.coordsROI_date)
            f.write("coords location: %s\n" %self.coordsROI_location)
            f.write("coords header: %s\n" %self.coordsROI_header)

            f.write("date, %s\n" %self.temperature_plot.unit)
            for i in range(len(self.temperature_plot.measured_values)):
                f.write("%s , %s \n" %(self.temperature_plot.time[i],
                                    self.temperature_plot.measured_values[i]))
            f.write("date, %s\n" %self.relativehumidity_plot.unit)
            for i in range(len(self.relativehumidity_plot.measured_values)):
                f.write("%s , %s \n" %(self.relativehumidity_plot.time[i],
                                    self.relativehumidity_plot.measured_values[i]))

    def _select_instrument(self):
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'instruments_list.json')
        with open(filename,'r') as f:
            data = json.load(f)
        return self._dictchoice(data,"Input id of the insturment or name: ")
    
    def _dictchoice(self,dictionary,text="Input the number of the entry or a new entry: ",retk=False):    
        dictdata = dict(zip(range(1,len(dictionary.keys())+1),dictionary.keys()))
        for i in dictdata:
            print("%s -> %s" %(i,dictdata[i]))
        isdate = True
        while isdate:
            ans = input(text)
            isdate  = self._is_date(ans)
        try:
            ans = int(ans)
            data = dictionary[dictdata[ans]]
            if retk:
                data = dictdata[ans]
            print("Using location in dict")
        except ValueError:
            data = ans
            print('Creating new location')
        return data
        
    def _is_date(self,string):
        try:
            date = map(int,string.split())
            datetime(*date)
            print("This seems a date, instrument should have at least the manufacturer name!")
            return True
        except (ValueError,TypeError):
            return False
