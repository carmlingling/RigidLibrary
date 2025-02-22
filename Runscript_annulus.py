import random
import sys, os, glob


# Load pebble game and dynamical matrix libraries
from Configuration import *
import Pebbles as PB
import Hessian as HS
import Analysis as AN
import Tiling as TY

# Global list of exisiting geometries
# Include in script, not here
setups={'simulation':ConfigurationSimulation,'lattice':ConfigurationLattice,'experiment_square':ConfigurationExpSquare,'experiment_annulus':ConfigurationExpAnnulus}

import matplotlib.pyplot as plt
import numpy as np
import pickle
import pandas as pd

#topdir='/directory/where/experimental/data/is/located/'
topdir='./DataAnnulus/'

# experimental friction coefficient
# mu=0.3
# Experiment type, for other types please use a different runscript.
# datatype = 'experiment_annulus'
# self.folder = param["folder"]
# self.mu = param["mu"]
# self.R1 = param["R1"]
# self.R2 = param["R2"]
# self.mid_x = param["mid_x"]
# self.mid_y = param["mid_y"]
# self.texture = param["texture"]
# self.density = param["density"]
# # Prefactor of the stiffness coefficient, k_n = \frac{\pi}{6} E h = 6490 kg /s^2
# self.stiffness = param["stiffness"]
# # radius conversion factor from pixel to m.
# self.rconversion = param["rconversion"]
# # height of the disks in m
# self.height = param["height"]
# # boundary width
# self.width = param["width"]
param = {}
param["mu"]=0.3
param["datatype"] = 'experiment_annulus'
param["R1"] = 1548
param["R2"] = 2995
param["mid_x"]=3134
param["mid_y"]=3028
param["texture"]=30
param["density"]=1060.0
param["stiffness"]=6490.0
param["rconversion"]=2.7e-4
param["height"]=3.1e-3
param["width"]=20e-3

#Change this if multiple experiments were used and use this to locate the correct data per experiment
experiment_nums=['10']
# Loop over experiment
for experiment in experiment_nums:
        # Extract some information from the data set:
        param["folder"] = topdir+'/'+experiment
        try:
            data = np.loadtxt(topdir+'/'+experiment+'/Adjacency_list.txt', delimiter=',')
            #nsteps is the maximal frame number
            nsteps = np.max(data[:,0]).astype(int)
        except:
            print('No valid data found for experiment ' + str(experiment))
            #if no data is found for an experiment number go to the next experiment
            continue
        
        # Loop over strain steps for a given experiment
        # Start at 1 since steps start at 1. Ends at nsteps.
        for u in range(1, nsteps+1):
                #Creating configuration
                # self.geom=geometries[self.param.constraint](self.param)
                #ThisConf = CF.Configuration(topdir+experiment,datatype, stupid,stupid,stupid, 0.2,u)
                # setups={'simulation':ConfigurationSimulation,'lattice':ConfigurationLattice,'experiment_square':ConfigurationExpSquare,'experiment_annulus':ConfigurationExpAnnulus}
                #class ConfigurationExpAnnulus(Configuration):
                #   def __init__(self,param):
                #       print("ConfigurationExpAnnulus: Created new Configuration Experimental Annulus")
                #       super(ConfigurationExpAnnulus,self).__init__('experiment_annulus')
                ThisConf = setups[param["datatype"]](param)
                
                #Reading in the data
                # def ReadData(self, posfile,confile,step,verbose=False):    
                ThisConf.ReadData(param["folder"] + '/particle_positions.txt',param["folder"] + '/Adjacency_list.txt',u,True)
                
                #Adding boundary contacts, passsing threshold argument is possible
                # def AddBoundaryContacts(self,verbose=False):
                ThisConf.AddBoundaryContacts(True)

                #Setting up and playing the pebble game
                ThisPebble = PB.Pebbles(ThisConf,3,3,'nothing',False)
                
                #Play pebble game
                ThisPebble.play_game()
                # compute rigid clusters
                cidx, clusterall, clusterallBonds, clusteridx, BigCluster=ThisPebble.rigid_cluster()

                ########### Setting up the dynamical matrix and getting eigenmodes
                # This itself does very little, just creates an empty Hessian class
                ThisHessian = HS.Hessian(ThisConf)
                
                #Create tiling class
                ThisTiling = TY.Tiling(ThisConf)
    
                #Make the Maxwell-Cremona tiling
                ThisTiling.tile(start=20, verbose=False)
                
                ########## Have a look at some analysis functions of the rigid clusters
                #def __init__(self,conf0,pebbles0,hessian0,verbose=False):
                ThisAnalysis=AN.Analysis(ThisConf,ThisPebble,ThisHessian,ThisTiling,0.01,False)
                
                #Tiling statistics
                err, fvertices, err_mean, f_mean, err_force_ratio = ThisAnalysis.tiling_statistics()
                
                # stress statistics
                zav,nm,pres,fxbal,fybal,torbal,mobin,mohist,sxx,syy,sxy,syx=ThisAnalysis.getStressStat()
                # cluster statistics
                frac,fracmax,lenx,leny=ThisAnalysis.clusterStatistics()
                #def plotStresses(self,plotCir,plotVel,plotCon,plotF,plotStress,**kwargs):
                fig1 = ThisAnalysis.plotStresses(True,False,False,True,False)
                #def plotPebbles(self,plotCir,plotPeb,plotPebCon,plotClus,plotOver,**kwargs):
                #ThisAnalysis.plotPebbles(True,True,True,False,False)
                
                #Plot pebbles has the following arguments: plotCir,plotPeb,plotPebCon,plotClus,plotOver
                #fig1 = ThisAnalysis.plotPebbles(True,True,True,False,False)
                fig2 = ThisAnalysis.plotPebbles(True,True,False,True,False)
                #fig3 = ThisAnalysis.plotPebbles(True,True,False,False,False)
                #For saving the plot as plot.pickle
                #pickle.dump(fig2, open('plot.pickle', 'wb')) # This is for Python 3 - py2 may need `file` instead of `open`
                
                """
                ######### continuing with the Hessian now 
                # constructing the matrix
                #  makeHessian(self,frictional,recomputeFnor,stabilise,verbose=False):
                ThisHessian.makeHessian(True,False,0,False)
                # diagonalising the matrix
                # def getModes(self,debug=False):
                ThisHessian.getModes(False)
                
                ##### a couple of checks on the modes (optional)
                #plotModes(self,usepts):
                #usepts=[3*ThisConf.N-5,3*ThisConf.N-4,3*ThisConf.N-3,3*ThisConf.N-2,3*ThisConf.N-1]
                #ThisHessian.plotModes(usepts)
                #plotZeroModes(self,thresh=2e-8,simple=True):
                #ThisHessian.plotZeroModes()
                
                ############ Now look for the cross-correlations
                # what is rigid according to modes with a given threshold:
                fig3 = ThisAnalysis.ModeClusters('translations',2e-4)
                # how this cross-correlates to rigidy according to pebbles:
                P_eig_if_pebble,P_pebble_if_eig,fig5 = ThisAnalysis.RigidModesCorrelate(2e-4)
                # These are the conditional probabilities of being rigid by mode while being rigid by pebble and the reverse
                print (P_eig_if_pebble,P_pebble_if_eig)
                # if there is a next data set
                # Needs revision in any case, don't use for now
                #if ThisConf.Nnext>0:
                #    P_disp_if_pebble,P_pebble_if_disp, fig6 = ThisAnalysis.RigidDisplacementsCorrelate(2e-4)
                #    # Conditional probabilities of being rigid by displacement while being rigid by pebble
                #    print (P_disp_if_pebble,P_pebble_if_disp)
                #    # D2_min, needs assessment
                #    fig7 = ThisAnalysis.DisplacementCorrelateD2min(True) 
                """
                
                #Plotting the contact network
                #fig3 = ThisAnalysis.contactnetwork()
                #Plotting Maxwell-Cremona tiling
                #Colorscheme options filled = False: cluster, force, colorblind, random
                #Colorscheme options filled = True: colorblind, random

                #fig4 = ThisAnalysis.tileplotter(colorscheme='force', filled=False)     
                #Force color scheme does not make sense, for know we only determine the size of the force using the normal force. I think that the tangential force also needs to be used. 
                fig5 = ThisAnalysis.tileplotter(colorscheme='cluster', filled=False)
                fig6 = ThisAnalysis.tileplotter(colorscheme='random', filled=True)

                plt.show()