from fogliodiagrammale import fogliodiagrammale
from pdf2image import convert_from_path
import numpy as np 
import matplotlib.pyplot as plt
try:
    import cPickle as pickle
except:
    import pickle
import os 
lstfiles = os.listdir(os.getcwd())
print("Reading pdf file... ")
images_p2i = convert_from_path('doc01377820200113132615.pdf')

locdic = {}
sheets = []
for pagenumber,page in enumerate(images_p2i):
    print("Working on page %s of %s. (index %s)" %(pagenumber+1,len(images_p2i),pagenumber) )
    filename = "page_%s.p" %pagenumber
    if filename not in lstfiles:
        img = np.array(page)
        h = fogliodiagrammale.fogliodiagrammale(img)
        h.extract_plots()
        h.wizard(cycle_duration=6,locationdict=locdic)

        # temperature
        h.temperature_plot.find_referencesystem()
        h.temperature_plot.manual_detectpoints()
        h.temperature_plot.calculate_values()
        h.temperature_plot.export_data()
        
        # relative humidity
        h.relativehumidity_plot.find_referencesystem()
        h.relativehumidity_plot.manual_detectpoints()
        h.relativehumidity_plot.calculate_values()
        h.relativehumidity_plot.export_data()

        h.export_data()
        try:
            locdic[h.location] +=1
            print("increasing countin location %s" %h.location)
        except KeyError:
            print("Adding location %s to dict" %h.location)
            locdic[h.location] = 0
        print("Completed page %s" %(pagenumber+1))
        pickle.dump( h, open( filename, "wb" ),protocol=-1 )
        sheets.append(h)
    else:
        print("Loading data from folder")
        h = pickle.load(open( filename, "rb" ))
        sheets.append(h)
