
from fogliodiagrammale import fogliodiagrammale
#from pdf2image import convert_from_path
import numpy as np 
import matplotlib.pyplot as plt
import os 
#images_p2i = convert_from_path('doc01377820200113132615.pdf')
#img = np.array(images_p2i[0])
img = os.path.join('..','images','Complicated.tiff')
h = fogliodiagrammale.fogliodiagrammale(img)
h.extract_plots()
h.wizard()
# relative humidity
h.relativehumidity_plot.find_referencesystem()
h.relativehumidity_plot.manual_detectpoints()
h.relativehumidity_plot.calculate_values()
h.relativehumidity_plot.export_data()
# temperature
h.temperature_plot.find_referencesystem()
h.temperature_plot.manual_detectpoints()
h.temperature_plot.calculate_values()
h.temperature_plot.export_data()
