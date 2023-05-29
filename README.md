# Canadian Covid Peaks

Analysis of Canadian covid hospitalization data: extraction of Gaussians and fitting them to SEIR model

Downloading requires requests:

> pip install requests

Data are from Health Canada. They can be pulled down and extracted using:

> cd download
> python download_covid_data.py
> python extract_hospitalized.py

This will create files canada-covid-data.cvs and can_hosp_patients.csv, the latter of which
contains two columns: the day number from 2020-01-23 and the number of people in hospital
in Canada who tested positive for covid on that day, according to our not-entirely-trustworthy
government agencies.

Copy can_hosp_patients.csv to the peak_fit directory:

> cp can_hosp_patients.csv ../peak_fit

Extracting the peaks requires my simple minimizer:

> pip install simple-minimizer

Then:

> cd ../peak_fit
> python detrend.py

This will take a while, and generate a bunch of files:

1. can_hosp_patients_parameters.csv contains: Peak Date Height SDev Area Spacing

2. can_hosp_patients_fit.csv contains: Day Date Fit Peak1 Peak2 Peak3 ... Peak10

3. can_hosp_patients.dat: the data in YYYY-MM-DD Number format.

The fit is really quite good. It's slow because it's a robust non-linear fit in 30 parameters.
The objective function is the RMS error between the data and the sum of Gaussian peaks.

At this point I got to wondering if I could get any insight from finding SEIR model parameters
that would fit each peak individually. I'd previously done modelling on the whole dataset,
but it gets a little murky.

Copy the file can_hosp_patients_fit.csv to the seir_fit directory and switch to it:

> cp can_hosp_patients_fit.csv ../seir_fit
> cd ../seir_fit

The fitter in this case runs a SEIR model with just two free parameters: the infection
probability and the risk of hospitalization once infected. The latter is just a fraction of 
the infectious cases on the assumption that no one gets hospitalized outside the acute 
phase. There is also the implicit assumption that hospitalization only lasts as long as the
accute phase, which is false and might be material. I've not looked into it yet.

Also: the model has no death rate. This should not affect the major outcomes, and putting
it in would just depress me. It should be modelled by adding a term to the dS/dt equation
that has the same timing as the recovery term, but disappears people from the model.

The SEIR model runs on a slow and robust adaptive RK4 solver, which I originally wrote in Perl
a million years ago to solve a system that had a truly hideous cusp which no other approach
could handled, and have kept using it since because while it's slow I generally don't have
to care very much about its ability to deal with unpleasantness.

Minimization is done on the RMS error between the SEIR model and each individual peak.

To fit all peaks, run:

> python seir_fit.py -1

To fit individual peaks just give the one-based peak number. For example to fit the first
omicron peak:

> python seir_fit.py 5

If you want to explore the paraemter space you can give the full set of parameters to use
on the command line and the system will use them rather than run the minimizer, where
the parameters are:

- Fraction Hospitalized
- Infection Probability per Encounter
- Days from exposed to infectious 
- Days from exposed (not infectious) to recovered

> python seir_fit.py 5 0.01 0.001 3 12

As part of the simple minimizer package there is a logistic constraint that can be used to
force effective parameters to be positive if you want to keep things from getting into 
unphysical parts of the paraemeter space. Have a look at the peaks_objective.py file
in the peak_fit directory to see how this is used to enforce positivity while still allowing
for smooth variation so the minimizer will work.

Running the SEIR fit will produce an output file per peak fitted with names like:

seir_model_fit_5.csv

and so on.

The files have the format:

Day Susceptible Exposed Infectious Recoverd Fit Data

where Day is a nominal day number (the peaks are shifted around during fitting to
make the SEIR model peak line up with the extracted Gaussian). The rest are
numbers of people. Since we are modelling Canada's population, 38 million is
a reasonable value for the overall population.

The seir_fit.py program will spit out a line giving the found parameters and the
RMS error for each peak it fits. For some badly choosen initial values of the 
parameters it will run away into either unphysical domains (negative times
or probabiltiies) or trade off between parameters (the full four interact quite
a lot) such that you eventually wind up with a domain error in computing
the next value.

The SEIR model equations are somewhat documented  on [World of Wonders](https://worldofwonders.substack.com/p/what-can-a-seirs-model-tell-us-about)
in a series of posts starting with the one linked. That's for the full SEIRS model,
the SEIR model is modified from it.

One feature of the minimizer is the ability to turn off or reorder the axes along
which minimization is done. This has been used to suppress the time parameters
in seir_fit.py on the line:

>             lstOrder = [0, 1, -1, -1]

To turn the times back on change this to:

>             lstOrder = [0, 1, 2, 3]

Scales can also make a difference to minimization. Currently they are set to:

>            lstScales = [0.001, 0.005, 0.5, 0.5]

and this works pretty well. The scale affects how the algorithm searches during
the bracketing phase, and twiddling with them can help with local minima.

I'll be writing up the results of this analysis in World of Wonders this week, and
will link it here when it's published.
