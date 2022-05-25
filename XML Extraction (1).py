#!/usr/bin/env python
# coding: utf-8

# In[1]:


#if you have installed GTK Runtime and would like to have extracted trajectory data converted to PDF, uncomment
#all lines of code in this document.

#After initial running of this code, you can comment out all !pip install commmands.

#!pip install tabulate
#!pip install glob2
#!pip install markdown
#!pip install plotly

import os
GTK_FOLDER = r'C:\Users\amkillam\Documents\XML Data Extraction\bin'
os.environ['PATH'] = GTK_FOLDER + os.pathsep +os.environ.get('PATH', '')
#!pip install weasyprint

import glob
import xml.etree.ElementTree as et
from bs4 import BeautifulSoup
from mpl_toolkits import mplot3d
get_ipython().run_line_magic('matplotlib', 'inline')
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import tabulate
from markdown import markdown
import itertools
import plotly.express as px
import weasyprint


# In[2]:


def dataExtractor(directory):
    
    path = directory.replace("\\", '\\\\')
    
    #uncomment if you would like to see all data headers, does not seem to work with glob library, but this is not necessary for current use of XML documents.
    
    #file = open(path, "r")
    #master_df = pd.DataFrame()
    #soup = BeautifulSoup(file.read() , 'xml')
    #print("All data headers in this XML document are:")
    #list([str(tag.name) for tag in soup.find_all()])
    tree=et.parse(path)
    root=tree.getroot()

    columnsDataFrame =['Measured Depth (m)', 'Inclination (rad)', 'Azimuth (rad)', 'True Vertical Depth (m)', '+N/-S (m)', '+E/-W (m)', 'Vertical Section (m)', 'Build Rate (rad/m)', 'Turn Rate (rad/m)', 'Dogleg Severity(rad/m)']

    df = pd.DataFrame(columns = columnsDataFrame)

    for feature in root.findall(".//{http://www.witsml.org/schemas/1series}trajectoryStation"):
        dispEw = feature.find(".//{http://www.witsml.org/schemas/1series}dispEw")
        if dispEw != None:
            dispEw = float(dispEw.text)
        else: 
            dispEw = float(0)

        tvd = feature.find(".//{http://www.witsml.org/schemas/1series}tvd")
        if tvd != None:
            tvd = float(tvd.text)
        else: 
            tvd=float(0)

        dispNs = feature.find(".//{http://www.witsml.org/schemas/1series}dispNs")
        if dispNs != None:
            dispNs = float(dispNs.text)
        else: 
             dispNs= float(0)

        measuredepth = feature.find(".//{http://www.witsml.org/schemas/1series}md")
        if measuredepth != None:
            measuredepth = float(measuredepth.text)
        else: 
            measuredepth = float(0)

        inclination = feature.find(".//{http://www.witsml.org/schemas/1series}incl")
        if inclination != None:
            inclination = float(inclination.text)
        else: 
            inclination = float(0)
        
        azi = feature.find(".//{http://www.witsml.org/schemas/1series}azi")
        if azi != None:
            azi = float(azi.text)
        else: 
            azi = float(0)

        vertSect = feature.find(".//{http://www.witsml.org/schemas/1series}vertSect")
        if vertSect != None:
            vertSect = float(vertSect.text)
        else: 
            vertSect = float(0)

        dls = feature.find(".//{http://www.witsml.org/schemas/1series}dls")
        if dls != None:
            dls = float(dls.text)
        else: 
            dls = float(0)

        rateBuild = feature.find(".//{http://www.witsml.org/schemas/1series}rateBuild")
        if rateBuild != None:
            rateBuild = float(rateBuild.text)
        else:
            rateBuild = float(0)

        rateTurn = feature.find(".//{http://www.witsml.org/schemas/1series}rateTurn")
        if rateTurn != None:
            rateTurn = float(rateTurn.text)
        else:
            rateTurn = float(0)

        new_row = {'Measured Depth (m)': measuredepth,
                                  'Inclination (rad)': inclination,
                                  'Azimuth (rad)':azi,
                                  'True Vertical Depth (m)': tvd,
                                  '+N/-S (m)': dispNs,
                                  '+E/-W (m)': dispEw,
                                  'Vertical Section (m)': vertSect,
                                  'Build Rate (rad/m)': rateBuild,
                                  'Turn Rate (rad/m)': rateTurn,
                                  'Dogleg Severity(rad/m)': dls}

        df = df.append(new_row, ignore_index= True)
        
    directoryCreatePath = directory[:len(directory)-5]
    directoryCreatePath = directoryCreatePath.replace("DrillingData", "ExtractedData")
    if not os.path.exists(directoryCreatePath):
        os.makedirs(directoryCreatePath)
    fileName = path.replace("DrillingData", "ExtractedData")
    fileName = fileName.replace(".xml", ".md")
    df.to_markdown(fileName)
    fileName = fileName.replace(".md", ".html")
    df.to_html(fileName)
    fileNameTwo=fileName.replace(".html", ".pdf")
    weasyprint.HTML(fileName).write_pdf(target=fileNameTwo, stylesheets = [weasyprint.CSS('stylesheet.css')])
    fileName = fileName.replace(".html", ".csv")
    df.rename(columns = {'+N/-S (m)':'Displacement NorthSouth (m)', '+E/-W (m)':'Displacement EastWest (m)'}, inplace = True)
    df.to_csv(fileName)
    df.rename(columns = {'Displacement NorthSouth (m)' : '+N/-S (m)', 'Displacement EastWest (m)' : '+E/-W (m)'}, inplace = True)
   
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.plot(df.loc[:,"+N/-S (m)"], df.loc[:,"+E/-W (m)"], df.loc[:,"True Vertical Depth (m)"], color='g', marker="x")
    ax.set_xlabel("+N/-S")
    ax.set_ylabel("+E/-W")
    ax.set_zlabel("True Vertical Depth")
    fig.set_size_inches(10,10)
    ax.set_title("Well Trajectory")
    ax.set_zlim3d((max(df.loc[:,"True Vertical Depth (m)"])),0)
    ax.set_xlim3d(-5000,5000)
    ax.set_ylim3d(-5000,5000)
    
    graphDirectorySavePath = path.replace("DrillingData", "ExtractedData")
    graphDirectorySavePath =  graphDirectorySavePath.replace(".xml", "")
    graphDirectorySavePath =  (graphDirectorySavePath + " Non-interactive Trajectory Graph.png")
    plt.savefig(graphDirectorySavePath)
    
    fig = px.line_3d(df, '+N/-S (m)', '+E/-W (m)','True Vertical Depth (m)', title = 'Trajectory of Well', range_z = [(max(df.loc[:,"True Vertical Depth (m)"])), 0], width=1350,height=700)
    graphDirectorySavePath = graphDirectorySavePath.replace("Non-interactive Trajectory Graph.png", "Interactive Trajectory Graph.html")
    fig.write_html(graphDirectorySavePath)
    plt.close()
    
    


# In[3]:


#The directory inputted assumes that you have the folder "WITSML Realtime drilling data" in the same directory as notebook file,
#and you have renamed the folder to DrillingData
for i in glob.iglob('.\DrillingData/*/*/trajectory/*.xml'):
    print (i, "beginning")
    dataExtractor(i)
    print(i, "complete")
print("Extraction complete")
    
    


# In[ ]:




