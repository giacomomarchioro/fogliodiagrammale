
from fogliodiagrammale import fogliodiagrammale
#from pdf2image import convert_from_path
import numpy as np 
import matplotlib.pyplot as plt

#images_p2i = convert_from_path('doc01377820200113132615.pdf')
#img = np.array(images_p2i[0])
img= plt.imread('Starting_five_days_afterat11.tiff')
h = fogliodiagrammale.fogliodiagrammale(img)
h.extract_plots()
h.wizard()
# relative humidity
h.relativehumidity_plot.find_referencesystem()
h.relativehumidity_plot.manual_detectpoints()
h.relativehumidity_plot.calculate_values()
h.relativehumidity_plot.export_data()
h.relativehumidity_plot.plot_extracted()
