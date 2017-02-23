# LUT-making instructions

(Only applies to Stage 2. Be warned this _is_ complex, and not super trivial)

Stage 2 JEC requires 3 LUTs (lookup-tables):

1) PT compression
2) ETA compression
3) Correction LUT

The script [`bin/correction_LUT_plot.py`](bin/correction_LUT_plot.py) will produce these as **human-readable (HR) txt files**.

To apply to hardware, these must be converted to different formats:

- The firmware requires files with hex values. Use [`bin/mif_maker.py`](bin/mif_maker.py) to produce these.
- The online software requires a XML file ("programmable LUTs"). Use [`bin/programmable_lut_maker.py`](bin/programmable_lut_maker.py) to produce this.


## Brief overview of human-readable LUT making

_Check these values!_
The PT compression LUT compresses the PT from 11 bits to 4 bits (i.e. 2048 possible values down to 16 possible values).

The ETA compression LUT compresses the ETA from 7 bits to 4 bits (i.e. 128 possible values down to 16 possible values).

When a jet gets processed, its raw (uncorrected) pt and eta are translated into compressed pt and eta "indices" using the above LUTs.
These are combined to form an "address":

```
address = eta_index << 4 | pt_index
```

The correction LUT maps an address to a number.
This number contains both the addend & multiplier.
These are used to apply the correction:

```
corrected jet ET = uncorrected ET * multiplier + addend
```

i.e. `y = mx + c` (although the actual maths is slightly different as we're working with bits).

The multiplier is 10 bits unsigned, the addend is 8 bits signed.

These are combined into one number by:

```
addend << 10 | multiplier
```

**The aim is to capture the ideal pre-correction Vs post-correction curve (calculated using the "ideal" correction functions), whilst meeting the limitations of the number of bins available.**

This means we have to bin (quantise) PT and the effective correction factors.

What the `correction_LUT_plot.py` script does roughly is:

- Read in the correction curves, and make them "fancy": i.e. add low-pT and high-pT plateaus

- Writes an ETA compression LUT

- If desired, make a PT compression LUT (alternatively can use an existing one)

- Generates a mapping of pre and post corrected ET for each ETA bin.

- Figures out the best multiplier/addends for each bin, based on # bits available, and the rightshift in the hardware (see later). These are the "hardware" corrections

- Make some plots comparing function correction vs hardware corrections

- Write the addend and multiplier to LUTs: each separately (for checking), and one combined one (to give to the firmware)


### Running

- Do `python` [`bin/correction_LUT_plot.py`](bin/correction_LUT_plot.py) `<input> <output> --stage2 --lowPtPlateau --constantHF --plots`

- Use `-h` or `--help` to elucidate options.

- This script will (a) make LUTs, (b) make plots about said LUTs.

- **Input**: either (a) a ROOT file output by `runCalibration.py` or (b) a text file with the function parameters in it

    * If using the plain text file it assumes each line is of the format

    ```
    <func param 0> <func param 1> ... <func param 6> <low pT plateau correction factor> <highest pT at which low pT plateau correction is applicable> <high pT plateau correction factor> <lowest pT at which the high-pT plateau becomes applicable>
    ```

    * If you change this schema, you will need to update the  `get_functions_params_textfile()` method. It isn't psychic!

- **ETA compression**: look in the `calo_ieta_to_index()` method of [`bin/correction_LUT_stage2.py`](bin/correction_LUT_stage2.py)

- **PT compression**: you can either calculate a new "optimum" PT compression (using the correction functions), or use an existing human-readable PT compression LUT. To do the latter, use the `--ptCompressionFile` option. The current LUT is here: [https://github.com/cms-l1t-offline/L1Trigger-L1TCalorimeter/blob/master/lut_pt_compress.txt](https://github.com/cms-l1t-offline/L1Trigger-L1TCalorimeter/blob/master/lut_pt_compress.txt).
**NB** if the number of possible PT indices changes from 2^4, you **must** update this in the code here

- **Addend/multiplier**:

- **Output**: the output name is a base name, used to create a folder of plots, and several LUTs.

    * An ETA compression LUT
    * A PT compression LUT
    * A LUT with the multipliers and addends combined
    * A LUT with the addends (for debugging)
    * A LUT with the multipliers (for debugging)

- NB the script might take a little time to run - I believe this is because matplotlib is not the fastest...

### An example

If you run

```
python bin/correction_LUT_plot.py \
example_stage2lut/example_output.root \
example_stage2lut/example_lut.txt \
--stage2 --lowPtPlateau --constantHF --plots
```

you will produce the following in `example_stage2lut/example_lut`:

- `example_lut_pt.txt`: PT compression LUT
- `example_lut_eta.txt`: ETA compression LUT
- `example_lut_add_mult.txt`: Multiplier+addend correction LUT
- `example_lut_mult.txt`, `example_lut_add.txt`: Individual multiplier and addend LUTs (for debugging)

There are also a plethora of plots:

- `all_raw_fits.pdf`, `all_raw_fits_ptZoomed.pdf`: all the function fits from the input file

- `fancy_fit_all_*.pdf`: one big plot of all fit functions/graphs/functions+graphs

For each eta bin, you will also get:

- `fancy_fit_*.pdf`: plot of graph + fit, useful to check results of low pt plateau or constant HF

- `corr_vs_pt_*.pdf`: plots the overall correction as a function of PT, for both the ideal function, and the LUT correction (= post-corrected / pre-corrected).

- `corr_vs_pt_cluster_*.pdf`: plots the ideal correction, with each colour representing a PT bin.

- `lut_vs_func_*.pdf`: plot the function-corrected PT vs LUT-corrected PT (i.e. ideal result vs LUT result).

- `pt_pre_vs_post_*.pdf`: post-corrected PT vs pre-corrected PT, for both ideal function correction, as well as LUT correction.

- `pt_pre_vs_post_clusters_*.pdf`: post-corrected PT vs pre-corrected PT using the ideal function, with each colour representing a PT bin.

- `means_hist_*_*_myjackknife.pdf`, `means_hist_*_*_root_jackknife.pdf`: for HF bins, we use a jack-knifing technique to calculate a constant function fit. These plots show the jack-knife results, along with peak and mean (to cross-check jack-knifing worked OK).

Since these plots cover a large PT range, they can hide features, especially at low-PT. Therefore most of the above plots have variations that focus on low-PT, based on what's in the filename:

- `*_zoomX_*`: limit PT-axis to small PT values
- `*_logX_*`: use logarithmic PT axis

**IMPORTANT**: you should check these plots for each ETA bin to ensure the binnings look sensible, and the LUT multiplier/addends produce sensible results. e.g. if you have a correction factor of 4, it is unlikely the multiplier/addend will be able to cope with this!

## Firmware LUT making

These are for the PT and ETA compressions.
These are known as "MIF" files, machine-interpretable format (file?).
These are plain text files with one hex value per line.
Use [`bin/mif_maker.py`](bin/mif_maker.py) to do this, e.g.

```
python bin/mif_maker.py \
example_stage2lut/example_lut/example_lut_pt.txt \
example_stage2lut/example_lut/example_lut_pt.mif
```

Briefly, if our human-readable LUT is of the form `{key: value}`, then the MIF file is just the values in hex. The firmware assumes that the key is the index of the value (so the first value is index 0, etc).

## Programmable (XML) LUT making

This is only for the multiplier/addends.
Use [`bin/programmable_lut_maker.py`](bin/programmable_lut_maker.py) to do this, e.g.

```
python bin/programmable_lut_maker.py \
example_stage2lut/example_lut/example_lut_add_mult.txt \
example_stage2lut/example_lut/example_lut_add_mult.xml
```

Note that this also includes other settings including jet seed threshold, and thresholds for jet sums.
The multiplier/addends are stored in a vector of hex values (like the MIF format), in the `<param id="jetEnergyCalibLUT" type="vector:uint">...</param>` element.

**IMPORTANT!!!**: you should always check that the settings such as jet seed threshold are correct. These are set at the top of [`bin/programmable_lut_maker.py`](bin/programmable_lut_maker.py), e.g.

```
SETTINGS['jetSeedThreshold'] = 8  # IN HW PT NOT GeV
SETTINGS['jetMaxEta'] = 40
SETTINGS['HTMHT_maxJetEta'] = 28
SETTINGS['HT_jetThreshold'] = 60
SETTINGS['MHT_jetThreshold'] = 60
```

## Some details

### Low PT plateau correction

(Historically referred to as "fancy")
At low PT, the fitted curve continue to larger correction factors, whilst the graph point "turnover" and actually indicate smaller correction values are needed.
However, computing an accurate correction value at low PT is very difficult given the non-Gaussian nature of the response.
Additionally, sometimes the curve does odd things.
To combat this, a constant correction factor is used for values of PT less than that at the turnover.
Whilst this is not the most "correct" method, it is simple and caps the corrections to a safe factor.

### HF bin constant corrections

In HF, it was observed that the correction curve is significantly different to in the barrel/endcap, and had greater dependence on pileup.
This made it harder to fit a function (and it often failed).
The curve (especially at higher PU) was fairly close to a constant value, and thus we decided to use a constant correction factor across the PT range.
However, a straight line fit is affected by low-stats points at high PT (which are less critical anyway).
In order to calculate a reasonable fit value, I used a so-called "jack knife" method.
Essentially, you remove a point from the curve, then calculate the mean of all the leftover points.
You then repeat this procedure: you do every possible mean removing only 1 point, then do every possible mean having removed any 2 points, etc etc until you get to removing N-1 points.
From this you will have a whole series of means.
You then either figure out the mean of these, or bin them and calculate the mode.

### ETA compression

This is determined by the user in `calo_ieta_to_index()` method of [`bin/correction_LUT_stage2.py`](bin/correction_LUT_stage2.py).
NB the FW doesn't "see" ieta = 29, so what we call 30 is actually 29 in the FW, etc.

### PT compression derivation

The optimum way to divide up the PT range of 0 - 1024 into 2^4=16 bins depends on the corrections, since we want to assign more bins to where the correction changes fastest. For example, it makes little sense to assign a lot of bins at high pT when the correction is ~ constant.

So we need a way to derive the bin edges.
There are 2 methods included in the code:

1. "Greedy" binning
2. k-means clustering

(NB, the binning only has to be "good enough" to capture the pre- vs post-corrected curve fairly accurately.)

To change binning method, use the `merge_algorithm` arg of `print_Stage2_lut_files()`, either `"greedy"` or `"kmeans"`.

#### "Greedy" binning

This works by clustering pT values together, provided the correction they need is ~ similar.
Starting at high pT (where the correction changes slowest), pT values are grouped together until some condition (maximum correction factor = merge_criterion * minimum correction factor) is no longer satisfied.
Then, that bin is complete, and a new bin started, again descending in pT.
This continues until (a) the number of bins exceeds the user's specification, in which case the grouping condition must be loosened, or (b) the number of discrete pT values remaining is small enough that they can be assigned to an individual bin.

This clustering therefore assigned the most bins to the lowest pT, where the correction curve changes fastest.
However, it (arguably) compromises at higher pT.

#### k-means clustering

An alternate strategy would be to ask for N groups, such that the variation in each group, and also across groups, is minimal.
This is known as "k-means clustering" (see [wiki](https://en.wikipedia.org/wiki/K-means_clustering)).
It is implemented using the scikit-learn package.
This clustering is therefore (arguably) most accurate across the whole pT spectrum, but may not capture the lower-pT case as well as the "greedy" binning.
This requires the `scikit-learn` Python package.

### Addend/multiplier derivation

Here the actual correction factors are calculated.
Whilst these will be assigned **per PT bin**, these are actually applied to the _raw_ jet PT (the full 11 bits).
The aim is to find the best multiplier and addend for each PT bin.
Since the multiplication is not entirely trivial, it is not easy to just subtract and divide.
Therefore, a matrix is calculated, where the indices correspond to the pre-correction HW PT values and multiplier integers, and entries in the matrix are the "corrected" values, for a given right-shift:

```
corrected = (uncorrected * multiplier) >> right_shift
```

For each pt bin, we then do the following. We assume that the correction factor is ~ constant, and thus we can use `y = mx + c`.

**A note about high PT** Since there are


### Configuration

The main business happens when `print_Stage2_lut_files()` is called, e.g.

```
print_Stage2_lut_files(fit_functions=fits,
                       eta_lut_filename=eta_lut_filename,
                       pt_lut_filename=pt_lut_filename,
                       mult_lut_filename=mult_lut_filename,
                       add_lut_filename=add_lut_filename,
                       add_mult_lut_filename=add_mult_lut_filename,
                       right_shift=9,
                       num_corr_bits=10,
                       num_add_bits=8,
                       plot_dir=out_dir,
                       read_pt_compression=args.ptCompressionFile,
                       target_num_pt_bins=2**4,
                       merge_criterion=1.05,
                       merge_algorithm='greedy')  # greedy or kmeans

```

The arguments are:

- `fit_functions: list[TF1]`
    List of correction functions to convert to LUT

- `eta_lut_filename: str`
    Filename for output LUT that converts eta to compressed index

- `pt_lut_filename: str`
    Filename for output LUT that converts pt to compressed index

- `mult_lut_filename: str`
    Filename for output LUT that converts address to multiplicative factor

- `add_lut_filename: str`
    Filename for output LUT that converts address to correction addend

- `corr_mult_lut_filename: str`
    Filename for output LUT that converts address to addend + multiplier

- `right_shift: int`
    Right-shift factor needed in hardware for multiplication

- `num_corr_bits: int`
    Number of bits to represent correction multiplicative factor.

- `num_add_bits: int`
    Number of bits to represent correction addend.

- `plot_dir : str`
    Directory to put checking plots.

- `read_pt_compression : str or None`
    Can read in PT compression table from existent human-readable LUT.
    If not None, the target_num_pt_bins/merge_criterion/merge_algorithm
    args are ignored. If None, a PT compression table will be devised.

The following args are only for calculating the PT compression LUT:

- `target_num_pt_bins: int`
    Number of bins to compress pt bin range into. If you have N bits for pt,
    then target_num_pt_bins = 2**N - 1

- `merge_criterion: float`
    Criterion factor for compressing multiple pt values into one bin. Values will
    be combined if the maximum correction factor = merge_criterion * minimum
    correction factor for those pt values.

- `merge_algorithm : {'greedy' , 'kmeans'}`
    Merge algorithm to use to decide upon compressed ET binning.

    greedy: my own algo, that merges bins within a certain tolerance until
        you either meet the requisite number of bins, or clustering fails.

    kmeans: use k-means algorithm in scikit-learn


### Multi-function objects

As a cheap "hack" to have 1 function object that uses different functions for different input ranges, I created the `MultiFunc` object (see [bin/multifunc.py](bin/multifunc.py)).
(This could/should also be done in RooStats/Fit!).
Basically, at heart it has a dict, with the key as a tuple marking a lower and upper limit, and the value is a TF1 object.
Example usage:

```
lin = ROOT.TF1("lin", "x")
quad = ROOT.TF1("quad", "x*x")

functions_dict = {
    (0, 1): lin,
    (1, np.inf): quad
}
f = MultiFunc(functions_dict)
f.Eval(0.5) # 0.5
f.Eval(3) # 9
f.SetTitle("My cool function)
f.Draw()
```
