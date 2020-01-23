
from fogliodiagrammale import fogliodiagrammale
from pdf2image import convert_from_path
import numpy as np 

images_p2i = convert_from_path('doc01377820200113132615.pdf')
h = fogliodiagrammale.fogliodiagrammale(np.array(images_p2i[0]))
h.extract_plots()
h.wizard()
h.relativehumidity_plot.find_referencesystem()
h.temperature_plot.find_referencesystem()