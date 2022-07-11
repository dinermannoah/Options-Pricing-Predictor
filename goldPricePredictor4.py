# -*- coding: utf-8 -*-
"""
Created on Wed May 25 11:29:49 2022

@author: noahd
"""

import yfinance as yf
import numpy as np
import datetime as dt
import pandas as pd
from pandas_datareader import data as pdr
import math

yf.pdr_override()
now =  dt.datetime.now()
goldindex  = 'GC=F'
goldvol = '^GVZ'
comEq = 'GUNR'
inflation = 'TIP'





startyear = 2012
startmonth = 2
startday = 1

start = dt.datetime(startyear, startmonth, startday)

now = dt.datetime.now()

golddf = pdr.get_data_yahoo(goldindex, start, now)
goldvoldf = pdr.get_data_yahoo(goldvol, start, now)
comEqdf = pdr.get_data_yahoo(comEq, start, now)
inflationdf = pdr.get_data_yahoo(inflation, start, now)

metrics = []

frameLen = len(golddf)


def assignPriceVol(period, predictordf):

    weightsum = 0
    

    daysBetween = math.floor((now - start).days * 250/365)
    
    intervals = math.floor(daysBetween/period)+1
    currentVol = predictordf.iloc[frameLen-period:frameLen,4].mean()
    
    for i in range (2, intervals):        
        volDiff = currentVol- predictordf.iloc[period*(i-2):period*(i-1),4].mean()
        priceDiffPercent = (golddf.iloc[period*(i-1):period*i,4].mean() - golddf.iloc[period*(i-2):period*(i-1),4].mean()) /(golddf.iloc[period*(i-2):period*(i-1),4].mean())
        periodsBack = i-1
        weights = weightAlgo(volDiff, periodsBack)
        projDiff = priceDiffPercent*weights
        weightsum = weightsum + weights


        

    pastPriceVol = projDiff / weightsum

    
    
    return pastPriceVol

def assignPriceVolGrowth(period, predictordf):

    weightsum = 0
    

    daysBetween = math.floor((now - start).days * 250/365)
    
    intervals = math.floor(daysBetween/period)+1
    currentPriceDiffPercent = (predictordf.iloc[frameLen-period:frameLen,4].mean() - predictordf.iloc[frameLen-(2*period):frameLen-period,4].mean())
    
    for i in range (2, intervals):        
        predictorPriceDiffPercent = (predictordf.iloc[period*(i-1):period*i,4].mean() - predictordf.iloc[period*(i-2):period*(i-1),4].mean()) /(predictordf.iloc[period*(i-2):period*(i-1),4].mean())
        priceDiffPercent = (golddf.iloc[period*(i-1):period*i,4].mean() - golddf.iloc[period*(i-2):period*(i-1),4].mean()) /(1+golddf.iloc[period*(i-2):period*(i-1),4].mean())
        periodsBack = i-1
        weights = weightAlgo(predictorPriceDiffPercent, periodsBack)
        projDiff = priceDiffPercent*weights
        weightsum = weightsum + weights


        

    pastPriceVol = projDiff / weightsum

    
    
    return pastPriceVol


def weightAlgo(Diff, periodsBack):
    if Diff == 0 :
        weight = 0
    elif Diff <= .1:
        diffWeight = 1 / abs(Diff)**0.5
        timeWeight = 1 / periodsBack
        weight  = diffWeight * timeWeight *1000
    else:    
        diffWeight = 1 / abs(Diff)
        timeWeight = 1 / periodsBack
        weight  = diffWeight * timeWeight
    return weight

def averageReturn(period):
   
    a = assignPriceVol(period, goldvoldf)
    weighta = 0.4
    b = assignPriceVolGrowth(period, comEqdf)
    weightb = 0.2
    c = assignPriceVol(period, inflationdf)
    weightc = 0.5
    avg = (a+b+c)/(weighta+weightb+weightc)
    low = min(a,b,c)
    high = max(a,b,c)
    bestLowHigh = (avg, low, high)
    
    return bestLowHigh

print(averageReturn(1))

    
