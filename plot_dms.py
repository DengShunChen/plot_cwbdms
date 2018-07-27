#!/usr/bin/env python 
#
# Purpose : read directly from dms key and plot it.
#
#  CopyRight @ Deng-Shun Chen
#-------------------------------------------------------------
import os
import sys 
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from struct import Struct 
from gauss_grid import *
from mpl_toolkits.basemap import Basemap
from cwbgfs_model  import *
from matplotlib import gridspec as gspec
from datetime import datetime
from dateutil.relativedelta import *
from argparse import ArgumentParser,ArgumentDefaultsHelpFormatter

def plot_field(df,var):
  if len(expids) == 1:
    fig = plt.figure(figsize=(10,6),dpi=100)
    plt.subplots_adjust(top=0.85,bottom=0.15,right=0.95,left=0.05)
    gs = gspec.GridSpec(1,1) 
  elif len(expids) == 2:
    fig = plt.figure(figsize=(10,10),dpi=100)
    plt.subplots_adjust(top=0.9,bottom=0.1,right=0.98,left=0.02)
    gs = gspec.GridSpec(2,1) 
  else:
    raise ValueError('len(expids)>2')
 
  for e,expid in enumerate(expids):
    ax = plt.subplot(gs[e])
    data = np.reshape(df[expid].values,(nlat,nlon)) 
    # plot map 
    m = Basemap(lon_0=180,ax=ax)
    m.drawcoastlines(linewidth=1,color="k")
    m.drawparallels(np.arange(-90,90,20), labels=[1,1,0,1])
    m.drawmeridians(np.arange(-180,180,40), labels=[1,1,0,1])
    # gaussian lattitudes
    lats, bonds = gaussian_latitudes(int(float(nlat)/2.))
    lats = np.asarray(lats)    
    # longitudes
    lons = np.linspace(0,360,nlon,endpoint=False)

    X,Y = np.meshgrid(lons,lats)
    x,y = m(X,Y)
    # find max and min value 
    if e == 0:
      if var == '850000':
        vmin = 600.
        vmax = 1800.
      elif var == '850100':
        vmin = 210.
        vmax = 320. 
      elif var == '500000':
        vmin = 4400.
        vmax = 6100.
      elif var == '500100':
        vmin = 210.
        vmax = 290. 
      elif var == 'SSL010':
        vmin = 910.
        vmax = 1060.
      else:
        vmax = np.max(np.amax(data,axis=0))
        vmin = np.min(np.amin(data,axis=0))
      inc = (vmax - vmin)/100.
      levels = np.arange(vmin,vmax,inc)
      clevels = np.arange(vmin,vmax,inc*4)
    # plot countourf
    shading = ax.contourf(x, y, data, levels, cmap='RdYlBu_r',  alpha=0.75)
    contour = ax.contour(x, y, data, clevels, colors='k', linewidths=0.5)
    plt.clabel(contour,inline=True, fontsize=10, fmt='%5.1f')
    plt.title(labels[e],fontsize='large',fontweight='bold')
  cbar_ax = fig.add_axes([0.15, 0.05, 0.7, 0.02 ]) 
  plt.suptitle('%s \n%s  f%3.3d  - valid at %s' % (var_substr,title_substr,int(fcst),vdate_substr),fontsize='x-large',fontweight='bold')
  plt.colorbar(shading, cax=cbar_ax, orientation='horizontal')
  return fig, ax, m

def plot_diff(df):
  fig = plt.figure(figsize=(10,6),dpi=100)
  plt.subplots_adjust(top=0.85,bottom=0.15,right=0.95,left=0.05)
  gs = gspec.GridSpec(1,1)

  ax = plt.subplot(gs[0])
  data = np.reshape(df[expids[1]].values,(nlat,nlon))
  data = data - np.reshape(df[expids[0]].values,(nlat,nlon))
  # plot map
  m = Basemap(lon_0=180,ax=ax)
  m.drawcoastlines(linewidth=1,color="k")
  m.drawparallels(np.arange(-90,90,20), labels=[1,1,0,1])
  m.drawmeridians(np.arange(-180,180,40), labels=[1,1,0,1])
  # gaussian lattitudes
  lats, bonds = gaussian_latitudes(int(float(nlat)/2.))
  lats = np.asarray(lats)
  # longitudes
  lons = np.linspace(0,360,nlon,endpoint=False)
  X,Y = np.meshgrid(lons,lats)
  x,y = m(X,Y)
  # find max and min value
  vmax = np.max(np.amax(data,axis=0))
  vmin = np.min(np.amin(data,axis=0))
  range = vmax
  if vmin > vmax:
    range = vmin
  # plot countourf
  #im = ax.contourf(x, y, data, 10, cmap='RdBu', vmin=vmin, vmax=vmax)
  im = ax.contourf(x, y, data, 200, cmap='seismic', vmin=-range, vmax=range)
  label = labels[1]+'-'+labels[0]
  plt.title(label,fontsize='large',fontweight='bold')
  plt.suptitle('%s Difference\n%s  f%3.3d' % (var_substr,title_substr,int(fcst)),fontsize='x-large',fontweight='bold')
  cbar_ax = fig.add_axes([0.15, 0.05, 0.7, 0.02 ])
  plt.colorbar(im, cax=cbar_ax, orientation='horizontal')
  return fig, ax, m


def read_records(format,f):
  record_struct = Struct(format)
  chunks = iter(lambda : f.read(record_struct.size),b'')
  return (record_struct.unpack(chunk) for chunk in chunks)

def read_dms(filename):
  tmp = []
  with open(filename,'rb') as f:
    for rec, in read_records('>d',f):
      tmp.append(rec) 
  df = pd.DataFrame(tmp)
  return df

def get_field(data_base,data_name):
  df = []
  tmp = []
  for adate in pd.date_range(bdate,edate,freq='6H'):
#    taus = [fcst]
#    for t,tau in enumerate(taus):

      adate = str(adate.to_pydatetime().strftime("%Y%m%d%H"))
      data_time = adate + '00' + "%4.4d" % int(fcst)     # experiment date
      data_dir = 'MASOPS'
      filename = data_base +'/'+ data_dir + '/' + data_time + '/' + data_name

      # continue if time does not exist
      if not os.path.exists(filename):
        print('\033[1;31m' + '%s does not exist' % filename + '\033[1;m')
        continue

      # get data
      df = read_dms(filename)
      tmp.append(df)

  df = pd.concat(tmp,axis=1).mean(axis=1)

  return df

if __name__ == '__main__':

  global expid, labels
  global nlon, nlat, nmem
  global bdate, edate, fcst 
  global title_substr, var_substr

  parser = ArgumentParser(description = 'Process CWB DMS files to get Ensmele Spread',formatter_class=ArgumentDefaultsHelpFormatter)
  parser.add_argument('-x','--expid',help='experiment ID',type=str,nargs='+',required=True)
  parser.add_argument('-b','--begin_date',help='beginning date',type=str,metavar='YYYYMMDDHH',required=True)
  parser.add_argument('-e','--end_date',help='ending date',type=str,metavar='YYYYMMDDHH',default=None,required=False)
  parser.add_argument('-t','--fcst_time',help='forecast time (hours)',type=str,nargs='+',required=False,default=['6'])
  parser.add_argument('-m','--ensemble_size',help='the total number of ensmeble size',type=int,required=False,default=36)
  parser.add_argument('-a','--dmsdb_home',help='dms data base home directory',type=str,nargs='+',required=False,default=['/nwpr/gfs/%s/dmsdb2'%os.environ['USER']])
  parser.add_argument('-f','--dmsflag',help='dms key flag',type=str,nargs='+',required=False,default=['GH0G'])
  parser.add_argument('-v','--variable',help='vriable list for ploting',type=str,nargs='+',required=False,default=['000','100','200','210'])
  parser.add_argument('-k','--level',help='level list for ploting',type=str,nargs='+',required=False,default=['925','850','500','300','200','100'])
  parser.add_argument('-l','--label',help='list of labels for experiment IDs',nargs='+',required=False)
  parser.add_argument('-s','--save_figure',help='save figures as png and pdf',action='store_false',required=False)

  args = parser.parse_args()

  expids = args.expid
  bdate = datetime.strptime(args.begin_date,'%Y%m%d%H')
  edate = bdate if args.end_date is None else datetime.strptime(args.end_date,'%Y%m%d%H')
  fcsts = args.fcst_time
  nmem = args.ensemble_size
  dmsdb_homes = args.dmsdb_home
  dmsflags = args.dmsflag
  variables = args.variable
  levels = args.level
  save_figure = args.save_figure
  labels = expids if args.label is None else expids if len(args.label) != len(expids) else args.label

  if bdate == edate:
      title_substr = '%s' % bdate.strftime('%Y%m%d%H')
  else:
      title_substr = '%s-%s' % (bdate.strftime('%Y%m%d%H'),edate.strftime('%Y%m%d%H'))

  if len(expids) > 1 and len(dmsdb_homes) == 1:
    dmsdb_homes = dmsdb_homes * len(expids)

  if len(expids) > 1 and len(dmsflags) == 1:
    dmsflags = dmsflags * len(expids)

  # loop over levels and variables
  for v,variable in enumerate(variables):
    for l,level in enumerate(levels):
      var_substr = cwbgfs_level_dict[level]+' '+ cwbgfs_variable_dict[variable]  

      for fcst in fcsts:
        data = {} 

        if bdate == edate:
          vdate = bdate + relativedelta(hours=int(fcst)) + relativedelta(hours=8)
          vdate_substr = str(vdate.strftime("%Y%m%d%H")) + ' LST'
        else:
          vdate_substr = 'Time Mean'

        for expid,dmsdb_home,dmsflag in zip(expids,dmsdb_homes,dmsflags):
          print('reading files for ...',expid)

          # model configuration 
          model = cwbgfs_model_dict[dmsflag[0:2]]
          jcap = model[0] ; nlon = model[1] ; nlat = model[2]  
          lengh = "%7.7d" % (nlat*nlon)

          # set level and variabel 
          if level[0] == 'M':
            dmsflag = list(dmsflag)
            dmsflag[2] = 'M'
            dmsflag = ''.join(dmsflag)
          data_name = level + variable + dmsflag + 'H' + lengh
          data_base = dmsdb_home +'/'+ expid + '.ufs'   # experiment 

          # get field
          data[expid] = get_field(data_base,data_name)

        # plot field 
        fig, ax, m = plot_field(data,level+variable) 

        # save/show figure
        if save_figure:
          plt.savefig(expid+'_'+level+variable+'_f'+"%3.3d"%int(fcst)+'.png',dpi=100)  
        else:
          plt.show()

        if len(expids) == 2:
          fig, ax, m = plot_diff(data)
          if save_figure:
            plt.savefig('Diff'+'_'+level+variable+'_'+'f'+"%3.3d"%int(fcst)+'.png',dpi=100)  
          else:
            plt.show()


