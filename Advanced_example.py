from fogliodiagrammale import fogliodiagrammale
from pdf2image import convert_from_path
import numpy as np 
import matplotlib.pyplot as plt
import os
import json 
lstfiles = os.listdir(os.getcwd())
print("Reading pdf file... ")
images_p2i = convert_from_path('doc01377820200113132615.pdf')

try:
    with open('locdic.jos','r') as f:
        locdic = json.load(f)
except IOError:
    locdic = {}
sheets = []
for pagenumber,page in enumerate(images_p2i):
    print("Working on page %s of %s. (index %s)" %(pagenumber+1,len(images_p2i),pagenumber) )
    filenamegen = "page_%s.csv" %pagenumber
    if filenamegen not in lstfiles:
        img = np.array(page)
        h = fogliodiagrammale.fogliodiagrammale(img)
        # we could use this but sometimes is not stable
        h.extract_plots(titles=['Relative Humidity plot','temperature plot'])
        # we write each plot separately
        #h.extract_relativehumidityplot()
        #h.extract_temperatureplot()
        h.wizard(cycle_duration=6,locationdict=locdic,header_xcoords=(0,150))

        # temperature
        h.temperature_plot.find_referencesystem()
        h.temperature_plot.manual_detectpoints(plot=False)
        h.temperature_plot.calculate_values()
        filename = "%s_%s_%s.csv" %(h.location,h.temperature_plot.begin_datetime,h.temperature_plot.unit)
        h.temperature_plot.export_data(filename=filename)
        h.temperature_plot.plot_results()
        
        # relative humidity
        h.relativehumidity_plot.find_referencesystem()
        h.relativehumidity_plot.manual_detectpoints(plot=False)
        h.relativehumidity_plot.calculate_values()
        filename = "%s_%s_%s.csv" %(h.location,h.relativehumidity_plot.begin_datetime,h.relativehumidity_plot.unit)
        h.relativehumidity_plot.export_data(filename=filename)
        h.relativehumidity_plot.plot_results()
        
        h.export_data(filename=filenamegen)
        try:
            locdic[h.location] +=1
            print("increasing countin location %s" %h.location)
        except KeyError:
            print("Adding location %s to dict" %h.location)
            locdic[h.location] = 1
        print("Completed page %s" %(pagenumber+1))
        sheets.append(h)
        # we save the collected location
        with open('locdic.jos','w') as f:
            json.dump(locdic,f)
    else:
        print("Skipped page %s already digitized" %pagenumber)
