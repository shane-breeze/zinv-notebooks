# Z invisible width analysis

This markdown file will go through the tools and notebooks available to run the full analysis to measure the Z invisible width.

It primarily written in python3 and heavily depends on numpy's ndarray and pandas' Dataframe.


## Setup the code

The code's dependencies are kept on pypi and ROOT built from conda. Follow the [miniconda instructions](https://docs.conda.io/en/latest/miniconda.html) to install conda on your system with the relevant executable with the python version currently installed on your system. Follow the on-screen instructions and add lines to your `.bashrc` as needed.

After miniconda is setup, you can install the relevant dependencies with the `environment.yaml` file in the top directory of the repository
```bash
conda env create -f environment.yaml -n zinv37
```
This may take a while to install all the dependencies.

We will also be working with ipython notebooks, best dealt with jupyterlab (already installed). Run the following commands to setup jupyterlab extensions
```bash
jupyter labextension install @jupyter-widgets/jupyterlab-manager
#jupyter labextension install jupyter_vim # vim bindings in jupyterlab
```

To open up the notebooks, either open a local jupyterlab instance or a headless version and SSH tunnel to it. To open it locally run
```bash
jupyter lab
```
and in headless mode
```bash
jupyter lab --no-browser --port=8889
```
and SSH tunnel with the following command on some external machine:
```bash
ssh -N -f -L localhost:8889:localhost:8889 remote_user@remote_host
```
where `remote_user` and `remote_host` are replaced by those where the notebook is running.

After the initial setup is finished, only running jupyterlab (with the SSH tunnel) is required.


## Code layout

Various notebooks are separated into different directories to represent different aspects of the analysis. Results are typically shared between these directories through HDF5 files. Dependencies are taken from conda/pip, including some written specifically for this analysis. However, if one of these repositories requires editing, this can be achieved by cloning the repository and installing with pip in an editable mode. The relevant commands (from the top directory of this repository) are
```bash
mkdir external
cd external
git clone remote_repository
cd repository_directory
pip install -e .
```
where `remote_repository` and `repository_directory` are replaced with the relevant names.

The most important external packages are: (pysge)[https://github.com/shane-breeze/pysge], (dftools)[https://github.com/shane-breeze/dftools], (zinv-analysis)[https://github.com/shane-breeze/zinv-analysis] and (zdb-analysis)[https://github.com/shane-breeze/zdb-analysis].

Directory and notebook names are labelled with numbers to represent their relevant order to execute the analysis.

## Generated ntuples

Results already generated (full processing of the NanoAOD and a subsequent skim) may be found at

```
/vols/cms/sdb15/Analysis/ZinvWidth/databases/
```