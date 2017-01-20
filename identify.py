#!/usr/bin/env python

import argparse, cPickle
import cv2
import utils
from operator import itemgetter


ap = argparse.ArgumentParser()
ap.add_argument('-i', '--image', required=True, help='Captured image')
args = ap.parse_args()


# load the query image, compute the ratio of the old width
# to the new width and resize it
img = cv2.imread(args.image)
width = 600
ratio = float(width) / img.shape[1]
img = utils.resize(img, width=width)


# try brute-forcing the grid to extract pokemon images
imroi = img[120:img.shape[0]-70, 55:img.shape[1]-225, :]
GRID_X, GRID_Y = 5, 6
incx, incy = imroi.shape[0] / GRID_X, imroi.shape[1] / GRID_Y
imgs = []
sift = cv2.SIFT()
for x in range(GRID_X):
    imgs.append([])
    for y in range(GRID_Y):
        imgs[x].append(dict(image=imroi[x*incx:(x+1)*incx, y*incy:(y+1)*incy, :]))
        # utils.show(imgs[x][y]['image'])
        _, imgs[x][y]['descriptors'] = utils.color_sift(sift, imgs[x][y]['image'])
        if imgs[x][y]['descriptors'].shape[0] == 0:
            print '[-] ({}, {}) has no descriptors...\n'.format(x+1, y+1)


# load pokemon DB with descriptors...
with open('./pdb.pkl', 'rb') as f:
    pdb = cPickle.load(f)

# ...and find matches
FLANN_INDEX_KDTREE = 0
index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=10)
search_params = dict(checks=50)   # or pass empty dictionary
flann = cv2.FlannBasedMatcher(index_params, search_params)
for pokemon in pdb:
    for x in range(GRID_X):
        for y in range(GRID_Y):
            # print '[?] Testing ({}, {}) against {}'.format(x+1, y+1, pokemon['slug'])
            im = imgs[x][y]
            if im['descriptors'].shape[0] <= 1:
                continue
            if pokemon['descriptors'].shape[0] <= 1:
                # print '[-] {number:03d} / {slug} has no descriptors'.format(**pokemon)
                continue

            matches = flann.knnMatch(im['descriptors'], pokemon['descriptors'], k=2)
            # ratio test as per Lowe's paper
            nmatches = 0
            for i, (m, n) in enumerate(matches):
                if m.distance < 0.7 * n.distance:
                    nmatches += 1
            matches_ratio = float(nmatches) / max(pokemon['descriptors'].shape[0], im['descriptors'].shape[0])

            if not im.has_key('ratios'):
                im['ratios'] = []
            im['ratios'].append(dict(pokemon=pokemon['slug'], ratio=matches_ratio))


# print sorted matches for each subimage
for x in range(GRID_X):
    for y in range(GRID_Y):
        im = imgs[x][y]
        if not im.has_key('ratios'):
            continue
        # sort by ratio in descending order
        im['ratios'] = sorted(im['ratios'], key=itemgetter('ratio'), reverse=True)
        print '[+] ({}, {})'.format(x+1, y+1)
        # print only pokemons with most matches
        for ratio in im['ratios'][:10]:
            ratio['ratio'] = ratio['ratio'] * 100
            print '[+] {ratio:2.3f}% {pokemon}'.format(**ratio)
        print ''
