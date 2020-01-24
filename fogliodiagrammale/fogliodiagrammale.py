from singlediagram import single_diagram
from datetime import datetime,timedelta 
import matplotlib.pyplot as plt
import numpy as np
import os
import json

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
        self.location = None
        self.station = None
        self.ROI_RH = None
        self.ROI_T = None
        self.ROI_date = None
        self.ROI_location = None


    def extract_plots(self):
        titles = ['Relative Humidity plot','location','date','temperature plot',]
        c = [0]
        from matplotlib.widgets import RectangleSelector
        label = titles[0]
        fig, current_ax = plt.subplots(figsize=(20,7))
        current_ax.imshow(self.sheet_image)
        current_ax.set_title("Drag a ROI over %s" %titles[c[0]])
        
        def line_select_callback(eclick, erelease):
            
            'eclick and erelease are the press and release events'
            x1, y1 = int(eclick.xdata), int(eclick.ydata)
            x2, y2 = int(erelease.xdata), int(erelease.ydata)  
            print("%s = img[%s:%s,%s:%s]"% (titles[c[0]], y1, y2, x1, x2))
            if titles[c[0]] == 'Relative Humidity plot':
                self.ROI_RH = self.sheet_image[y1:y2,x1:x2]
            if titles[c[0]] == 'location':
                self.ROI_location = self.sheet_image[y1:y2,x1:x2]
            if titles[c[0]] == 'date':
                self.ROI_date = self.sheet_image[y1:y2,x1:x2]
            if titles[c[0]] == 'temperature plot':
                self.ROI_T = self.sheet_image[y1:y2,x1:x2]
                plt.close(fig)
                return
            c[0]+=1
            current_ax.set_title("Drag a ROI over %s" %titles[c[0]])  
            fig.canvas.draw()
            fig.canvas.flush_events()
            
            
            
            


        def toggle_selector(event):
            print(' Key pressed.')
            if event.key in ['Q', 'q'] and toggle_selector.RS.active:
                print(' RectangleSelector deactivated.')
                toggle_selector.RS.set_active(False)
            if event.key in ['A', 'a'] and not toggle_selector.RS.active:
                print(' RectangleSelector activated.')
                toggle_selector.RS.set_active(True)

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
    
    def wizard(self):
        plt.ion()
        plt.imshow(np.rot90(self.ROI_location,-1))
        plt.show()
        self.location = input("Write location: ")
        self.instrument_model = self._dictchoice()
        plt.close()
        plt.ioff
        plt.imshow(np.rot90(self.ROI_date,-1))
        plt.show()
        begin_date = input ("Write begin date using spaces e.g. 1988 12 31 15 30 :")
        begin_date = map(int,begin_date.split())
        self.begin_datetime = datetime(*begin_date)
        end_date = input ("Write end date using spaces e.g. 1988 12 31 15 30 or press enter to continue:")
        if end_date != '':
            end_date = map(int,end_date.split())
            self.end_datetime = datetime(*end_date)
        while self.cycle_duration not in ['w','d']:
            self.cycle_duration = input("Write cycle time weekly (w) or daily (d): ")
        plt.ioff()
        plt.close()
        # Here we create the single diagram object
        self.temperature_plot = single_diagram(data=self.ROI_T,
                                majorticks=self.instrument_model["temperature ticks C"],
                                unit=' C',
                                cycle=self.cycle_duration,
                                begin_datetime=self.begin_datetime,
                                )
        self.relativehumidity_plot = single_diagram(data=self.ROI_RH,
                                majorticks=self.instrument_model["relative humidity ticks"],
                                unit=' % RH',
                                cycle=self.cycle_duration,
                                begin_datetime=self.begin_datetime,
                                )

    def _dictchoice(self):
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'instruments_list.json')
        with open(filename,'r') as f:
            data = json.load(f)
        dictdata = dict(zip(range(1,len(data.keys())+1),data.keys()))
        for i in dictdata:
            print("%s -> %s" %(i,dictdata[i]))
        ans = input("Input id of the insturment or name:")
        try:
            ans = int(ans)
            data = data[dictdata[ans]]
        except ValueError:
            data = ans
        return data
        
