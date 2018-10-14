#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import time
import numpy as np
from nilearn.image import load_img
from nilearn.input_data import NiftiMasker
from rena import recursive_nearest_agglomeration
from sklearn.cluster import AgglomerativeClustering
from nilearn.plotting import plot_stat_map, plot_epi
from sklearn.feature_extraction.image import grid_to_graph


class ImplReNA:

    def __init__(self, data_path):
        self.data = load_img(data_path)
        self.masker = NiftiMasker(mask_strategy='epi',
                                  smoothing_fwhm=2,
                                  memory='nilearn_cache')
        self.X_masked = self.masker.fit_transform(self.data)
        self.X_train = self.X_masked[:100, :]

        X_data = self.masker.inverse_transform(self.X_train).get_data()

        self.n_x, self.n_y, self.n_z, self.n_samples = X_data.shape
        self.mask = self.masker.mask_img_.get_data()

    def data_info(self):
        return self.n_samples, self.n_x, self.n_y, self.n_z

    def get_connectivity(self):
        connectivity_ward = grid_to_graph(n_x=self.n_x, n_y=self.n_y,
                                          n_z=self.n_z, mask=self.mask)
        n_clusters = 2000

        ward = AgglomerativeClustering(n_clusters=n_clusters,
                                       connectivity=connectivity_ward,
                                       linkage='ward')

        ti_ward = time.clock()
        ward.fit(self.X_masked.T)
        to_ward = time.clock() - ti_ward
        self.labels_ward = ward.labels_

        ti_rena = time.clock()
        _, self.labels_rena = recursive_nearest_agglomeration(masker=self.masker,
                                                              data_matrix=self.X_train,
                                                              n_clusters=n_clusters,
                                                              n_iter=10, thr=1e-7)
        to_rena = time.clock() - ti_rena
        return to_ward, to_rena

    @classmethod
    def custering(cls, masked, labels):
        unique_labels = np.unique(labels)
        nX = []
        for l in unique_labels:
            nX.append(np.mean(masked[:, labels == l], axis=1))
        _, inverse = np.unique(labels, return_inverse=True)
        return np.array(nX).T[..., inverse]

    @classmethod
    def visualize_labels(cls, labels, masker):
        permutation = np.random.permutation(labels.shape[0])
        labels = permutation[labels]
        return masker.inverse_transform(labels)

    def visualizing(self):
        X_approx_rena = self.custering(self.X_masked,
                                       self.labels_rena)
        X_approx_ward = self.custering(self.X_masked,
                                       self.labels_ward)

        cut_coords = (-34, -16)
        n_image = 0

        labels_rena_img = self.visualize_labels(self.labels_rena,
                                                self.masker)
        labels_ward_img = self.visualize_labels(self.labels_ward,
                                                self.masker)

        clusters_rena_fig = plot_stat_map(labels_rena_img,
                                          bg_img=self.data,
                                          title='ReNA: clusters',
                                          display_mode='yz',
                                          cut_coords=cut_coords,
                                          colorbar=False)

        clusters_ward_fig = plot_stat_map(labels_ward_img,
                                          bg_img=self.data,
                                          title='Ward: clusters',
                                          display_mode='yz',
                                          cut_coords=cut_coords,
                                          colorbar=False)

        compress_rena_fig = plot_epi(self.masker.inverse_transform(X_approx_rena[n_image]),
                                     title='ReNA: approximated',
                                     display_mode='yz',
                                     cut_coords=cut_coords)

        compress_ward_fig = plot_epi(self.masker.inverse_transform(X_approx_ward[n_image]),
                                     title='Ward: approximated',
                                     display_mode='yz',
                                     cut_coords=cut_coords)

        original_fig = plot_epi(self.masker.inverse_transform(self.X_masked[n_image]),
                                title='original',
                                display_mode='yz',
                                cut_coords=cut_coords)

        return clusters_rena_fig, clusters_ward_fig, compress_rena_fig, compress_ward_fig, original_fig

    def storefig(self, store_path):
        store_path = store_path.strip()
        store_path = store_path.rstrip("\\")
        if not os.path.exists(store_path):
            os.makedirs(store_path)

        clusters_rena_fig, clusters_ward_fig, compress_rena_fig, compress_ward_fig, original_fig = self.visualizing()
        clusters_rena_fig.savefig(os.path.join(store_path, 'clusters_rena.png'))
        clusters_ward_fig.savefig(os.path.join(store_path, 'clusters_ward.png'))
        compress_rena_fig.savefig(os.path.join(store_path, 'compress_rena.png'))
        compress_ward_fig.savefig(os.path.join(store_path, 'compress_ward.png'))
        original_fig.savefig(os.path.join(store_path, 'original.png'))
        print('Figures have been stored in ' + store_path)
