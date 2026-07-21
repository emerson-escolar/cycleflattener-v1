# Installation

1. In the base directory, create a symlink `cplex_python_3.10` to the cplex python directory.
   On macOS:
   ```bash
   ln -s /Applications/CPLEX_Studio2211/cplex/python/3.10/arm64_osx/ cplex_python_3.10
   ```

2. Run `uv sync`

3. Ensure that [optiperslp](https://github.com/emerson-escolar/optiperslp) is installed and available on the path.


# Usage

1. The main script is `aohcp_longest.py`. You can run this by calling:
   ```
   uv run aohcp_longest.py
   ```
   in the same folder. Or,
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



# Running tests.

Run
```
uv run pytest
```
in the base directory.
