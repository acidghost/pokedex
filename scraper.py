#!/usr/bin/env python

import requests
from BeautifulSoup import BeautifulSoup
import time, cPickle


# get pokemons list from pokemondb
pdb_page = requests.get('http://pokemondb.net/pokedex/national')
pdb_soup = BeautifulSoup(pdb_page.text)
pdb = [{
    'number': int(elm.find('small').contents[0].split('#')[1]),
    'slug':   elm.find('a', { 'class': 'ent-name' }).get('href').split('pokedex/')[1],
    'name':   bytearray(elm.find('a', { 'class': 'ent-name' }).contents[0], encoding='utf-8')
} for elm in pdb_soup.findAll('span', { 'class': 'infocard-tall ' })]
#                                        this is intended -----^

# dump db into file
with open('./pdb.pkl', 'wb') as f:
    cPickle.dump(pdb, f)

# pretty print pokemons
for pokemon in pdb:
    print '#{number:03d}\t{slug:12}'.format(**pokemon)

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
