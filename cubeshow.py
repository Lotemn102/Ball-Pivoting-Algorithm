"""
Framework for plotting 3D volumetric data (3D cube) as voxel grid.
Transparency and color of voxels represent properties of one or two (3D) data arrays.
Run imcube.cubeshow() for voxel plots
Notes:
Scatter and Cross-sectional plots in development.
matplotlib version >=2.2 allows to plot voxels as well with ax.voxels(), but currently cumbersome to install.
Author: Sebastian Haan
Version 0.1
"""

from __future__ import print_function
import numpy as np
import os
import sys
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from matplotlib import cm


class imcube(object):
    """
    Plotting framework for cube (3D) data in voxel grid.
    Data values are represented using transparency and color of voxels
    To plot cube run imcube.cubeshow()
    """

    def _cube_data(self, pos):
        """ Calculation of voxel box
        :param pos: (x,y,z) coordinates;  axis direction: x: to left; y: to inside; z: to upper
        """
        size = (self.voxelsize[0], self.voxelsize[1], self.voxelsize[2])
        o = [a - b / 2 for a, b in zip(pos, size)]
        # length, width, and heightleft
        l, w, h = size
        x = [[o[0], o[0] + l, o[0] + l, o[0], o[0]],
             [o[0], o[0] + l, o[0] + l, o[0], o[0]],
             [o[0], o[0] + l, o[0] + l, o[0], o[0]],
             [o[0], o[0] + l, o[0] + l, o[0], o[0]]]
        y = [[o[1], o[1], o[1] + w, o[1] + w, o[1]],
             [o[1], o[1], o[1] + w, o[1] + w, o[1]],
             [o[1], o[1], o[1], o[1], o[1]],
             [o[1] + w, o[1] + w, o[1] + w, o[1] + w, o[1] + w]]
        z = [[o[2], o[2], o[2], o[2], o[2]],
             [o[2] + h, o[2] + h, o[2] + h, o[2] + h, o[2] + h],
             [o[2], o[2], o[2] + h, o[2] + h, o[2]],
             [o[2], o[2], o[2] + h, o[2] + h, o[2]]]
        return x, y, z

    def _plotvoxel(self, pos=(0, 0, 0), color='b', alpha=1, ax=None):
        """
        Plot a surface element at one position
        :param color: optional, color scheme
        :param alpha: optional, transparency from 0 to 1
        :param ax: optional, matplotlib axis
        """
        if ax != None:
            X, Y, Z = self._cube_data(pos)
            ax.plot_surface(X, Y, Z, color=color, rstride=1, cstride=1, alpha=alpha)

    def _plotcube(self, ax):
        """
        Plot of surfaceplot for each voxel
        :param ax: optional, matplotlib axis
        """
        maxcount = np.count_nonzero(self.mask == 0)
        count = 0
        densmax = np.max(self.density)
        for i in range(self.density.shape[0]):
            for j in range(self.density.shape[1]):
                for k in range(self.density.shape[2]):
                    if self.mask[i, j, k] == 0:
                        count += 1
                        # to have the
                        self._plotvoxel(pos=self.offset[0] + ((i + 0.5) * self.voxelsize[0],
                                                              self.offset[1] + (j + 0.5) * self.voxelsize[1],
                                                              self.offset[2] + (k + 0.5) * self.voxelsize[2]),
                                        color=self.color_dens[i, j, k],
                                        alpha=self.scale * self.density[i, j, k] / densmax / len(self.density), ax=ax)
                        if count % np.int(maxcount / 10) == 0:
                            # process bar
                            nper = np.int(count * 1. / maxcount * 100)
                            sys.stdout.write('\r')
                            sys.stdout.write("[%-20s] %d%%" % ('=' * np.int(nper / 5.), nper))
                            sys.stdout.flush()

    def cubeshow(self, density, data_color=None, scale=0.5, colorscheme=cm.jet,
                 mask=None, voxelsize=(1, 1, 1), offset=(0, 0, 0), colorbar=True, show=True,
                 rotate=None, savefig=False, path_out='', filename_out=None):
        """ Plotting voxels of 3d cube with data values converted in tranparency and color.
            Supports currently only cubes with same number of voxels in each dimension.
        :param density: 3D array with data, which will scale to transparency of voxels
        :param data_color: 3D array with data, which will scale to color of voxels, default data_color = density
        :param scale: scalar factor to scale transparency by a factor, default 0.5 (0 is complete transparent)
        :param colorscheme: optional, e.g. cm.jet or cm.Reds  (see matplotlib.cm), default is just constant color 'blue'
        :param mask: optional, must be same shape as density, set values to exclude to 1
        :param voxelsize: optional, must be in form (xsize_voxel,ysize_voxel, zsize_voxel), default = (1,1,1)
        :param offset: optional, must be in form (xoffset,yoffset, zoffset)
        :param colorbar: if True, plot colorbar. default = False
        :param show: if True, show interactive graph. default = True
        :param rotate: (elev, azim) elev stores the elevation angle in the z plane.
                azim stores the azimuth angle in the x,y plane. default (45,45)
        :param savefig: if True, saves file as png
        :param path_out: path name for figure to save
        :param filename_out: string for full filename (including path)
        """
        # Check input parameters:
        if density.shape[0] == density.shape[1] == density.shape[2]:
            self.density = density
        else:
            raise ValueError("Density array must have same length in all three dimensions")
        if data_color is not None:
            if data_color.shape == density.shape:
                self.data_color = data_color
            else:
                raise ValueError("Data for color must have same shape as density array")
        else:
            self.data_color = self.density
        self.color_dens = colorscheme(self.data_color / self.data_color.max())
        self.colorscheme = colorscheme
        if mask is not None:
            if mask.shape == density.shape:
                self.mask = mask
            else:
                raise ValueError("Mask must have same shape as density array")
        else:
            self.mask = np.zeros_like(density)
        voxelsize = np.asarray(voxelsize)
        if len(voxelsize) == 3:
            self.voxelsize = voxelsize
        else:
            raise ValueError("Incorrect size for voxelsize")
        offset = np.asarray(offset)
        if len(offset) == 3:
            self.offset = offset
        else:
            raise ValueError("Incorrect size for voxelsize")
        if rotate is not None:
            rotate = np.asarray(rotate)
            self.rot_azim = rotate[0]
            self.rot_elev = rotate[1]
        if savefig:
            if not os.path.exists(path_out):
                raise ValueError("Path not found: " + path_out)
            else:
                self.outfile = path_out + filename_out
        self.scale = scale

        # Start of plotting
        print("Plotting cube")
        fig = plt.figure()
        fig.clf()
        ax = fig.gca(projection='3d')
        ax.set_aspect('auto')
        self._plotcube(ax)
        if rotate is not None:
            ax.view_init(elev=self.rot_elev, azim=self.rot_azim)
        if colorbar:
            m = cm.ScalarMappable(cmap=self.colorscheme)
            m.set_array(np.linspace(self.data_color.min(), self.data_color.max(), 100))
            cbar = plt.colorbar(m)
        if savefig:
            plt.savefig(self.outfile)
            print('')
            print("saving figure as", self.outfile)
        if show:
            plt.show()
        # print('CUBESHOW FINISHED')