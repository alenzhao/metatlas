import matplotlib 
matplotlib.use('Agg')
import sys
sys.path.insert(0,'/global/homes/j/jtouma/metatlas')
from metatlas.helpers import metatlas_get_data_helper_fun as ma_data
import yaml
import os
import multiprocessing as mp
from matplotlib import pyplot as plt
import numpy as np

def plot_chromatogram(d,file_name, ax=None):
    import numpy as np
    from textwrap import wrap
    if ax is None:
        ax = plt.gca()

    plt.rcParams['pdf.fonttype']=42
    plt.rcParams['pdf.use14corefonts'] = True
    plt.rcParams['text.usetex'] = False
    plt.rcParams.update({'font.size': 12})
    plt.rcParams.update({'font.weight': 'bold'})
    plt.rcParams['axes.linewidth'] = 2 # set the value globally

    rt_min = d['identification'].rt_references[0].rt_min
    rt_max = d['identification'].rt_references[0].rt_max
    rt_peak = d['identification'].rt_references[0].rt_peak
        
    if len(d['data']['eic']['rt']) > 0:
        x = d['data']['eic']['rt']
        y = d['data']['eic']['intensity']
        ax.plot(x,y,'k-',linewidth=2.0,alpha=1.0)  
        myWhere = np.logical_and(x>=rt_min, x<=rt_max )
        ax.fill_between(x,0,y,myWhere, facecolor='c', alpha=0.3)

    ax.axvline(rt_min, color='k',linewidth=2.0)
    ax.axvline(rt_max, color='k',linewidth=2.0)
    ax.axvline(rt_peak, color='r',linewidth=2.0)

    ax.set_title("\n".join(wrap(file_name,54)),fontsize=12,weight='bold')

    
def plot_compounds_and_filesMP(kwargs):
    my_data= kwargs['data'] # data for all compounds for one file
    file_name  = kwargs['file_name'] # full path of output file name
    nRows, nCols = kwargs['rowscols']
    names = kwargs['names']
    share_y = kwargs['share_y']   
    
    f,ax = plt.subplots(nRows, nCols, sharey=share_y,figsize=(8*nCols,nRows*6))
    ax = ax.flatten()
    
    for i,name in enumerate(names):
        p = plot_chromatogram(my_data[i], name, ax=ax[i])

    f.savefig(file_name)    
    plt.close(f)


def plot_compounds_and_files(info):
    '''
    fname is the yaml file name containing the parameters needed to perform the plots
    '''

            
    nCols = info['nCols']
    share_y = info['share_y']
    pkl_file = info['pkl_file']
    output_dir = info['output_dir']
    processes = info['processes']
    plot_types = info['plot_types']

    data = ma_data.get_dill_data(pkl_file)
    compound_names = ma_data.get_compound_names(data)[0]
    file_names = ma_data.get_file_names(data)
    print 'Number of files: ', len(file_names)
    print 'Number of compounds:', len(compound_names)

    # setup the parameters according to the request
    if 'files' in plot_types:
        nRows = int(np.ceil(len(compound_names)/float(nCols)))
        args_list = []
        for file_idx,my_file in enumerate(file_names):
            kwargs = {'data':data[file_idx], 
                  'file_name': os.path.join(output_dir,my_file+'.pdf'),
                  'rowscols':(nRows, nCols),
                  'share_y':share_y,
                  'names':compound_names}
            args_list.append(kwargs)

        nprocs = min(processes, len(file_names))
        pool = mp.Pool(processes=nprocs)
        pool.map(plot_compounds_and_filesMP, args_list)
        print len(args_list), nprocs
    if 'compounds' in plot_types:
        nRows = int(np.ceil(len(file_names)/float(nCols)))
        args_list = []
        for compound_idx,my_compound in enumerate(compound_names):
            my_data = list()
            for file_idx, my_file in enumerate(file_names):
                my_data.append(data[file_idx][compound_idx])

            kwargs = {'data':my_data,
                  'file_name': os.path.join(output_dir, my_compound+'.pdf'),
                  'rowscols':(nRows, nCols),
                  'share_y':share_y,
                  'names':file_names}
            args_list.append(kwargs)

        nprocs = min(processes, len(compound_names))
        pool = mp.Pool(processes=nprocs)
        pool.map(plot_compounds_and_filesMP, args_list)
        print len(args_list), nprocs


if __name__ == '__main__':
    
    with open(sys.argv[1], 'r') as fin:
        info = yaml.load(fin)

    plot_compounds_and_files(info)