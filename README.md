# pokedex
###### Recognize Pokemons with a screenshot!


### What / Why
I have a Nintendo 3DS, a Pokemon game and I want to keep a list of my poket monsters.
I'm too lazy to manually keep the list updated, so I've put togheter a Computer Vision script that given
a screen capture of the PC boxes gives you the Pokemons in the image.
If you take pictures of all boxes in your in-game PC, you can easily load all your Pokemons.
Later you can take a picture of the newly caught to load them too.


### How
First you need to download the Pokemons list (with names and numbers) and then all sprites.
From the sprites we extract SIFT color descriptors (experimentation shows that LAB color scheme works best) by extracting
key-points from the grayscale image and then the 128-dimensional SIFT descriptors (one for each key-point, per color) giving
a 384-dimensional SIFT descriptor per key-point. This step is achieved with the `index.py` script.

To extract Pokemons from a new image we first have to extract the rectangles containing Pokemons (which are placed on
a 5x6 grid) from the image. SIFT color descriptors as explained before are extracted for each subimage.
Each Pokemon is searched for in each subimage, computing the ratio of matching features over the maximum number of key-points
(maximum between the stored and query). Finally, matching Pokemons are sorted by the ratio in descending order; matches with
higher ratio are more likely to be the Pokemon in the subimage. This step is achieved in the `identify.py` script.
