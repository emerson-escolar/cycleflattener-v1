# Summary

Code for angle optimal homologous cycle problem.

# Preliminaries

The instructions below assume the use of the Python package and project manager [uv](https://docs.astral.sh/uv/).

# Installation

0. Install [IBM ILOG CPLEX Optimization Studio 22.1.1](https://www.ibm.com/support/pages/downloading-ibm-ilog-cplex-optimization-studio-2211).

1. In the base directory of this project, create a symlink `cplex_python_3.10` to the cplex python directory.
   On macOS:
   ```bash
   ln -s /Applications/CPLEX_Studio2211/cplex/python/3.10/arm64_osx/ cplex_python_3.10
   ```

2. Run `uv sync`

3. Ensure that [optiperslp](https://github.com/emerson-escolar/optiperslp) is installed and available on the path.


# Usage

1. The main script is `aohcp_main.py`. You can run this by calling:
   ```
   uv run aohcp_main.py
   ```
   in the folder containing it (src/cycleflattener). Or,
   ```
   uv run -m cycleflattener
   ```
   anywhere within the project.


# Running the provided experiments

1. (On macOS) Install GNU "time" utility as gtime, for example by running:
   ```bash
   brew install gnu-time
   ```

2. Change into `replication` directory and run the scripts.

3. The main script for running the computational demonstrations in the paper is
   ```bash
   ./experiment_forpaper.sh
   ```

# Running tests.

Run
```
uv run pytest
```
in the base directory.



# Acknowledgements

Initial version of this code is based, with permission, on (unreleased) project "OptimizePlane" developed by
[Yuta Shimada](https://github.com/yut8a) for his Master's thesis.
In this project, the code has since been heavily modified with most parts completely rewritten and many new features added.
