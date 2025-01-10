# CDL_FireSeverity
Repository for CDL Guatemala Fire Severity Analysis Nov 2024

## Setup

The code in this repo is dependent on both R packages and Python libraries. Follow the below instructions to setup your machine after cloning.

**Note: these setup instructions only need to be run once when the repo is first cloned**

### Install Reticulate

In an R console, run the following command to install `reticulate`, a package that allows R and Python to work together. More info about `reticulate` can be found [here](https://rstudio.github.io/reticulate/index.html)

```
install.packages("reticulate")
```

#### Connect Reticulate to Python

There are two options for this section. First, if you already have a Python version setup that you'd like to use you can tell R to use that. Second, if you do not have Python version setup, we will use [miniconda](https://docs.anaconda.com/miniconda/), a miniature install of Anaconda.

##### Existing Python Version

To use an existing version of Python on your machine, follow the instructions found [here](https://rstudio.github.io/reticulate/index.html#python-version) to tell `reticulate` which version to use.

##### Using Miniconda

To install and use `miniconda` with reticulate, simply run the following commands in an R console:

```
reticulate::install_miniconda()
```

For more info on this install, see their documentation [here](https://rstudio.github.io/reticulate/reference/install_miniconda.html).
