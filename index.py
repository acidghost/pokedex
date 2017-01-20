#!/usr/bin/env python

import requests
from BeautifulSoup import BeautifulSoup
import time, cPickle, argparse
import cv2


ap = argparse.ArgumentParser()
ap.add_argument('-p', '--pokemon-list', action='store_true', help='Download the pokemon list')
ap.add_argument('-s', '--sprites', action='store_true', help='Download sprites too')
ap.add_argument('-i', '--index', action='store_true', help='Index sprites')
args = ap.parse_args()


if args.sprites or args.pokemon_list:
    # get pokemons list from pokemondb
    pdb_page = requests.get('http://pokemondb.net/pokedex/national')
    pdb_soup = BeautifulSoup(pdb_page.text)
    pdb = []
    for elm in pdb_soup.findAll('span', { 'class': 'infocard-tall ' }):
        #                                  this is intended -----^
        aelm = elm.find('a', { 'class': 'ent-name' })
        pnumber = int(elm.find('small').contents[0].split('#')[1])
        pslug = aelm.get('href').split('pokedex/')[1]
        pname = bytearray(aelm.contents[0], encoding='utf-8')

        pdb.append({
            'number': pnumber,
            'slug':   pslug,
            'name':   pname,
            'sprite': '{:03d}.{}.png'.format(pnumber, pslug)
        })

    # dump db into file
    with open('./pdb.pkl', 'wb') as f:
        cPickle.dump(pdb, f)

    # pretty print pokemons
    for pokemon in pdb:
        print '#{number:03d}\t{slug:12}'.format(**pokemon)


if args.sprites:
    # download menusprites
    sprite_base_url = 'http://archives.bulbagarden.net/wiki/'
    sprite_fmt = 'File:{:03d}MS.png'
    for pokemon in pdb:
        # get initial sprite page
        sprite_url = sprite_base_url + sprite_fmt.format(pokemon['number'])
        sprite_page = requests.get(sprite_url)
        sprite_soup = BeautifulSoup(sprite_page.text)
        # ... and find url to real sprite image
        img = sprite_soup.find('img', { 'alt': sprite_fmt.format(pokemon['number']) })

        # get img file
        img_req = requests.get(img.get('src'))
        if img_req.status_code == 200:
            print '[+] {number:03d} / {slug:12}'.format(**pokemon)
        else:
            print '[-] {number:03d} / {slug:12}'.format(**pokemon)
            continue

        # save image to file
        with open('./sprites/{number:03d}.{slug}.png'.format(**pokemon), 'wb') as f:
            f.write(img_req.content)
            f.close()

        # be polite...
        time.sleep(1)


if args.index:
    # load db if not loaded
    if not args.pokemon_list:
        with open('./pdb.pkl', 'rb') as f:
            pdb = cPickle.load(f)
    sift = cv2.SIFT()
    total_kps = 0
    for pokemon in pdb:
        # load sprite and convert to gray scale
        img = cv2.imread('./sprites/' + pokemon['sprite'])
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # compute SIFT descriptors
        kp, pokemon['descriptors'] = sift.detectAndCompute(gray, None)
        total_kps += len(kp)

    # store DB with descriptors
    with open('./pdb.pkl', 'wb') as f:
        cPickle.dump(pdb, f)
    print '[INDEX] Total KPs: {}'.format(total_kps)
