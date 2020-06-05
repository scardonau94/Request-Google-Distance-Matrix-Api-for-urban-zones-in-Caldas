# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 11:07:19 2020

@author: Vias
"""

import googlemaps
import geopandas as gpd
import pandas as pd
import numpy as np

#1) Read the shapefile of points with the places to calculate O-D matrix
CP = gpd.read_file("Caldas_municipalities_urban_zones.shp")

#2) Extract gegraphic coordinates (WGS 1984) of the points
#If a table with the coordinates is available, you can read this file

origins = [] #Coordinates are saving on this list
for i in range(0, 27):
    origins.append((CP.Latitud[i], CP.Longitud[i] ))

#This is the request for google maps distance matrix api, here you put the api
# key obtained from Google Cloud
    
gmaps = googlemaps.Client(key='AIzaSyAC-H3HC_tRAC1N54RttmeeG1xX_2G8Zx8')

#This API has restrictions. You onlu can request maximum 100 routes per request
#in this example, we have 27 points, so we need to calculate 729 routes
#for this reason i am going to divid the oring coordinates between three groups 
#of 9 points (A, B, C) and start to calculate the routes within them

originA = origins[0:9]
originB = origins[9:18]
originC = origins[-9:]

#The first matrix between points A is requested. 
#Necessarily you need to put the coordinates of origin and destination
#then you can put the mode of transport, private vehicle by default
#Depend of the city and country you can use walk, bycicle and public transport
#I requested all the routes in order to complet the O-D matrix between the
#27 municipalities
rutaAA = gmaps.distance_matrix(originA, originA)
rutaAB = gmaps.distance_matrix(originA, originB)
rutaAC = gmaps.distance_matrix(originA, originC)
rutaBB = gmaps.distance_matrix(originB, originB)
rutaBC = gmaps.distance_matrix(originB, originC)
rutaCC = gmaps.distance_matrix(originC, originC)
rutaBA = gmaps.distance_matrix(originB, originA)
rutaCA = gmaps.distance_matrix(originC, originA)
rutaCB = gmaps.distance_matrix(originC, originB)

#A list with all the routes requested is built
routes = [rutaAA, rutaAB, rutaAC, rutaBA, rutaBB, rutaBC, rutaCA, rutaCB, rutaCC]

#We create to list in order to put origin and destinations names
Origin = ["a"]*729
Destination = ["a"]*729
#We create a list in order to put times and distance from the routes
Time = np.zeros(729)
Distance = np.zeros(729)

#With this loop, origin, destinations, time and distance of each route is
#extract and save
cont = 0

for r in routes:  
    cont+=1
    for i in range(1, 10):
        for j in range(1, 10):
            Origin[j-1 + 9*(i-1)+81*(cont-1)] = r["origin_addresses"][i-1]
            Destination[j-1 + 9*(i-1)+81*(cont-1)] = r["destination_addresses"][j-1]
            Time[j-1 + 9*(i-1)+81*(cont-1)] = r["rows"][i-1]["elements"][j-1]["duration"]["value"]
            Distance[j-1 + 9*(i-1)+81*(cont-1)] = r["rows"][i-1]["elements"][j-1]["distance"]["value"]   

#results are saved in a dictionary and a dataframe is built
Resultados ={"Origin": Origin, "Destination":Destination, "Travel_time":Time, "Distance":Distance}
Results = pd.DataFrame(Resultados)

#For matrix construction used pivot table
#Travel time matrix, results in seconds
OD_matrix_time = Results.pivot_table(index = ["Origin"],
                                     columns = "Destination",
                                     values = "Travel_time")
#Travel time matrix, results in meters
OD_matrix_distance = Results.pivot_table(index = ["Origin"],
                                     columns = "Destination",
                                     values = "Distance")

#Results are save in excel
OD_matrix_time.to_excel("O_Dmatrix_Caldas_travel_time.xlsx")
OD_matrix_distance.to_excel("O_Dmatrix_Caldas_distance.xlsx")