
from fogliodiagrammale import fogliodiagrammale
#from pdf2image import convert_from_path
import numpy as np 
import matplotlib.pyplot as plt

#images_p2i = convert_from_path('doc01377820200113132615.pdf')
#img = np.array(images_p2i[0])
img= plt.imread('Interferences.tiff')
h = fogliodiagrammale.fogliodiagrammale(img)
h.extract_plots()
h.wizard()
# relative humidity
h.temperautre_plot.find_referencesystem()
h.temperautre_plot.manual_detectpoints()
h.temperautre_plot.calculate_values()
h.temperautre_plot.export_data()
h.temperautre_plot.plot_extracted()
