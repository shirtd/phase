# TDA for Water-Ice Phase Changes

I use Python 3.8.
3D plotting with [PyVista](https://docs.pyvista.org/) requires [VTK](https://vtk.org/).
I installed it with conda, I think.
All other requirements can be installed by running

    pip install -r requirements.txt

## Usage

Running

    python main.py --default-frames

Will run the program with the default behavior for the default dataset (lennard-jones, melt.xyz).
For a given dataset and file the `--default-frames` flag will automatically load frames surrounding the phase transition:

- `lennard-jones/melt.xyz`: 30038-30062
- `water-first-order/ih_hda.xyz`: 126-138
- `water-first-order/lda_hda.xyz`: 87-99.

The default behavior is as follows:

1. load frames,
2. select points "close" to the boundary of the simulation (proportional to bounding box width, multiplicative factor set with `--delta`),
3. compute relative persistent homology using the alpha (Delaunay) filtration.

Without any additional arguments the program will quit upon completion.

#### Caching

The input data (the frames specified), the filtration, and the results from the persistence computation are each saved separately in a binary format in the directory specified by `--cache` (default: `./cache`).
Given a set of parameters the program will check if there exists a cached version of any stage of the computation, and load it.
The `--force` flag will force override any cached data, with `--force input`, `--force filt`, `--force persist` overwriting only the cached input, filtration, or persistence data, respectively.
The largest of these is always the filtration.
If a computation is cached you can load the persistence diagram without the filtration by passing `--nofilt`.
This functionality is encapsulated by the `tpers` preset (see below).
In this case, interaction is limited to the total persistence curve and persistence diagrams.
This should be used to quickly load the total persistence curve from a large number of frames.

#### Additional arguments

The following is displayed by running `python main.py --help`

    usage: tpers [-h] [--directory DIRECTORY] [--dataset DATASET] [--file FILE] [--preset {generate,tpers,reps}]
                 [--default-frames] [--frames FRAMES FRAMES] [--cache CACHE] [--force [FORCE]] [--parallel] [--nofilt]
                 [--nopers] [--verbose] [--nocache] [--agg] [--dim DIM] [--thresh THRESH] [--lim LIM] [--reps]
                 [--clearing] [--delta DELTA] [--coh] [--dual] [--show] [--interact] [--histo {birth,death,tpers}]
                 [--pmin PMIN] [--pmax PMAX] [--bmin BMIN] [--bmax BMAX] [--dmin DMIN] [--dmax DMAX] [--average] [--count]

    optional arguments:
      -h, --help            show this help message and exit
      --directory DIRECTORY
                            data directory.
      --dataset DATASET     data set
      --file FILE           data file
      --preset {generate,tpers,reps}
                            generate: generate data. adds --parallel --clearing, tpers: lightweight plot for potentially
                            many frames. adds --agg --interact, reps: interactive complex plot (slow for many large
                            frames). adds --reps --interact.
      --default-frames      choose frames based on dataset/file
      --frames FRAMES FRAMES
                            frames to load
      --cache CACHE         cache directory
      --force [FORCE]       force module cache override
      --parallel            compute in parallel
      --nofilt              do not compute complexes or persistence
      --nopers              do not compute persistence
      --verbose             verbose progress bars
      --nocache             ignore cache
      --agg                 attempt to agrregate cached persistence data
      --dim DIM             max persistence dimension
      --lim LIM             diagram plot limit multiplier (multiplied by max bounds)
      --reps                compute (co)cycle representatives
      --clearing            clearing optimization.
      --delta DELTA         distance to boundary multiplier (multiplied by max bounds, relative homology)
      --coh                 do persistent cohomology
      --dual                do dual voronoi persistence
      --show                show plot
      --interact            interactive plot
      --histo {birth,death,tpers}
                            histogram value
      --pmin PMIN           minimum total persistence
      --pmax PMAX           maximum total persistence
      --bmin BMIN           minimum birth
      --bmax BMAX           maximum birth
      --dmin DMIN           minimum death
      --dmax DMAX           maximum death
      --average             average total persistence
      --count               count persistence

For most cases using `--preset` with `--default-frames` should suffice.
The presets are each intended for a specific application:

- `generate`: populating the cache.
- `tpers`: loading only persistence diagram and viewing the persistence curve (uses `--agg`, see below).
- `reps`: load all data and interact with 3D simplicial complex (see discussion and warnings below).

In any of these cases are effectively four different computations that can take place on two different filtrations.
The default is ordinary persistence on the alpha complex, no flags required:

    python main.py --preset {generate,tpers,reps} --default-frames

The `--dual` flag will compute the dual Voronoi filtration.

    python main.py --preset {generate,tpers,reps} --default-frames --dual

Note that the current implementation computes and stores the alpha filtration as well, so the computation is longer and the cached files will be larger.

The `--coh` flag will compute persistent cohomology.

    python main.py --preset {generate,tpers,reps} --default-frames --coh
    python main.py --preset {generate,tpers,reps} --default-frames --dual --coh

The persistence diagrams of homology and cohomology are identical, however the representative cocycles are different.
Because of the duality of homology and cohomology the representatives of alpha homology persistence and dual voronoi cohomology persistence will be exact duals in complementary dimensions.

#### Aggregating cached data

If you would like the view the entire total persistence curve the recommended approach is to use the `generate` preset to break up the computation into small chunks and then quickly aggregate the cached persistence diagrams using the `--agg` flag.
The `water-first-order/lda_hda.xyz` test is a good example of where this might be useful as the phase transition is much slower, and therefore cannot be seen in a short sequence of frames.
I have 6 cores on my machine so I choose a multiple of 6 frames in each chunk.
I like 12.
There are 300 frames total in this dataset.
The following bash command will generate all of the data for alpha homology persistence:

    for n in {0..299..12}
    do
        python main.py --preset generate --frames $n $((n+12)) --dataset water-first-order --file lda_hda.xyz
    done

This will take some time.
Once completed, you can load any sequence of frames using the `--agg` command, which is included in the `tpers` preset.
Not specifying any frames will load all 300 frames:

    python main.py --preset tpers --dataset water-first-order --file lda_hda.xyz

To select a smaller range of frames, say 50 to 150, add `--frames 50 150`.

#### Plotting

Running

    python main.py --show --default-frames

will run the program (or load the data) with the default parameters and plot the total persistence curve.

<!-- **TODO** `--save` option. -->

## Interaction

Running

    python main.py --interact --default-frames

will run the program (or load the data) with the default parameters and plot the total persistence curve in interactive mode.

#### TPers Interaction

Click on any point on any curve to plot the corresponding persistence diagram, and simplicial complex.
Pressing the right and left arrow keys (with the TPers plot selected) will plot the next (or previous) point on the curve.
Pressing `t` will enable a point trajectory trace starting at the currently selected frame.
Moving to another frame (either using arrow keys or clicking on the TPers plot) will plot the trajectory of each point in the simulation between the selected and starting frames.
Pressing `t` again will disable trajectory tracing.
The following help is displayed by the program.

    Total persistence interactive plot
      * The following keyboard commands are available in the TPers context:
    	[left]	previous diagram
    	[right]	next diagram
    	[t]	toggle trace: turn on point trajectory plot starting at current frame

Note: the trace functionality is only available with representatives (`--reps` or `--preset reps`).

<!-- **TODO** `--nocomplex` and `--nodiagram` options. -->

#### Diagram Interaction

Clicking on a point on the persistence diagram will plot the (co)chains corresponding to the birth and death of the feature selected (green:birth, red: death).
There are a number of keyboard commands that can be used while either the persistence diagram or complex plot are selected.
The following help is displayed by the program.

    Cycle representative plot
      * The following keyboard commands are available in the complex (3D) and persistence diagram contexts:
    	[x]	reset plot: remove all reps, leaving only the complex.
    	[z]	reset view: return to default side view.
    	[p]	primal: toggle primal representatives (default: True).
    	[d]	dual: toggle dual representatives (default: False).
    	[c]	fill/complete: toggle filled death chains (default: False).
    	[0]	primal 0: toggle primal 0 simplices (default: True).
    	[6]	dual 0: toggle dual 0 simplices (default: False).
    	[1]	primal 1: toggle primal 1 simplices (default: True).
    	[5]	dual 1: toggle dual 1 simplices (default: False).
    	[2]	primal 2: toggle primal 2 simplices (default: True).
    	[4]	dual 2: toggle dual 2 simplices (default: False).
    	[8]	primal on: show all primal simplices.
    	[9]	primal off: hide all primal simplices.
    	[7]	dual off: hide all dual simplices.
    	[right]	next feature (sorted by total persistence)
    	[left]	previous feature (sorted by total persistence)

A note: the context referred to by the help simply refers to which window is currently selected.
That is, cycle representative plot commands are only available when either the 3D complex or persistence diagram window is selected, and TPers plot commands are only available when the TPers plot window is selected.

#### A few warnings

Do not attempt to plot too many large frames, such as the water-first-order dataset.
The 3D interaction is intended to get a closer look at a small number of frames surrounding a phase transition (around 10-20 is ok).
The cached filtration objects for larger sets of frames will take much longer to load, and the required memory will slow down the plotting.

Each plot element is added to the plot window lazily.
After an object has been plotted it is not removed, only hidden.
Using this feature you can step through each frame to load all of the plots first, reducing load time between frames after.

The dual complex is also initialized lazily (when d, 6, 5, 4, or 7 are pressed).
For alpha complex data this requires computing the dual complex, which may take some time for larger datasets.
For dual complex data (when the `--dual` flag is passed) the alpha complex is already computed, and stored as a member of the dual complex object.
However, because the dual complex stores more data it will take longer to load initially, and take up more space in memory.

I would like to eventually factor the 3D complex plot functionality out of the cycle representative plot.
This way you can only load the data required for the simplicial complex, with the option of loading additional persistence diagram, and cycle representative data.


## TODO

#### Interaction

- Plot complex as one mesh: figure out how to toggle visibility of faces, points, and edges.
- Filtration value slider.
- Factor complex plot out of `--reps`. Should be possible to only load and view complexes. Representative interaction would inherit from this.
- Plot quality options.
- Toggle clear reps override.
- Caching meshes?

#### Frontend

- Smart caching at the object level.
- Proper database of individual frames.
- Dispatch class.
- Fix bounds.

#### Backend

- Redo everything with simplex trees.
- Limit complex dimension. Should be done at the complex level to reduce file size as much as possible.
- Implement alpha and dual filtration by hand. Don't store alpha complex in dual complex.
