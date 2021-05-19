# TDA for Water-Ice Phase Changes

I use Python 3.8.
3D plotting with [PyVista](https://docs.pyvista.org/) requires [VTK](https://vtk.org/).
I installed it with conda, I think.
All other requirements can be installed by running

    pip install -r requirements.txt

## Usage

Running

    python main.py

Will run the program with the default behavior:
load frames 30025-30075,
select points within distance 1 of the bounds (assumed to be cube 8x8x8 cube),
compute relative persistent homology using the alpha (Delaunay) filtration.
Without any additional arguments the program will quit upon completion.

#### Caching

The input data (the frames specified) and the results from the persistence computation are saved in a binary format in the directory specified by `--cache` (default: `./cache`).
Given a set of parameters the program will check if there exists a cached version of any stage of the computation, and load it.
The `--force` flag will force override any cached data, with `--force input` and `--force persist` overwriting only the cached input in persistence data, respectively.

#### Plotting

Running

    python main.py --show

will run the program (or load the data) with the default parameters and plot the total persistence curve.

**TODO** `--save` option.

## Interaction

Running

    python main.py --interact

will run the program (or load the data) with the default parameters and plot the total persistence curve in interactive mode.

#### TPers Interaction

Click on any point on any curve to plot the corresponding persistence diagram, and simplicial complex.
Pressing the right and left arrow keys (with the TPers plot selected) will plot the next (or previous) point on the curve.
Pressing `t` will enable a point trajectory trace starting at the currently selected frame.
Moving to another frame (either using arrow keys or clicking on the TPers plot) will plot the trajectory of each point in the simulation between the selected and starting frames.
Pressing `t` again will disable trajectory tracing.

**TODO** `--nocomplex` and `--nodiagram` options.

#### Diagram Interaction

Clicking on a point on the persistence diagram will plot the (co)chains corresponding to the birth and death of the feature selected (green:birth, red: death).
There are a number of keyboard commands that can be used while either the persistence diagram or complex plot are selected.
