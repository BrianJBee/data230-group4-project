# DATA 230 Group 4 Project

## Project Environment Setup

This project uses **Conda** to manage its Python environment and dependencies. The required packages and their versions are specified in [`environment.yml`](environment.yml).

Following the instructions below will create a reproducible environment so that the project's Python files and Jupyter notebooks can be run correctly.

## Prerequisites

Before setting up the project, make sure you have **Conda** installed.

You can install either:

- [Miniconda](https://docs.conda.io/projects/miniconda/en/latest/)
- [Anaconda](https://www.anaconda.com/download)

After installation, verify that Conda is available:

```bash
conda --version
````

 You should see a version number, for example:

```
conda 26.1.1
```

 ## 1\. Clone or Download the Repository

 If you are using Git, clone the repository and navigate into the project directory:

```
git clone https://github.com/BrianJBee/data230-group4-project.git
cd data230-group4-project
```

 Alternatively, download the repository as a ZIP file and extract it to a location of your choice.

 Make sure that `environment.yml` is located in the project's root directory.

 For example:

```
data230-group4-project/
├── environment.yml
├── README.md
├── notebooks/
│   └── ...
├── src/
│   └── ...
└── data/
    └── ...
```

 ## 2\. Create the Conda Environment

 From the project's root directory, run:

```
conda env create -f environment.yml
```

 Conda will read `environment.yml` and install the required Python version and dependencies.

 The environment name is normally specified in the `name:` field of `environment.yml`.

 For example, if the file contains:

```
name: data230-group4-project-env
```

 Conda will create an environment named `data230-group4-project-env`.

 ### Check the Environment Name

 You can view the available Conda environments with:

```
conda env list
```

 The newly created environment should appear in the list.

 ## 3\. Activate the Environment

 Activate the environment using its name:

```
conda activate data230-group4-project-env
```

 You should see the environment name displayed in your terminal prompt:

```
(data230-group4-project-env) $
```

 All subsequent Python commands should be run while this environment is activated.

 ## 4\. Verify the Installation

 Confirm that Python is available:

```
python --version
```

 You can also verify that Conda is using the expected environment:

```
conda info --envs
```

 The active environment will be marked with an asterisk (`*`).

 To verify that the project's dependencies are installed, run:

```
conda list
```

 This will display the packages installed in the environment.

 ## 5\. Running Python Files

 Make sure the Conda environment is activated:

```
conda activate data230-group4-project-env
```

 You can then run Python scripts normally:

```
python path/to/script.py
```

 For example:

```
python src/ingest.py
```

 ## 6\. Running Jupyter Notebooks

 If Jupyter is included in `environment.yml`, you can start Jupyter from the activated environment:

```
jupyter notebook
```

 Alternatively, you can use JupyterLab:

```
jupyter lab
```

 Your browser should open automatically. Navigate to the desired notebook and open the `.ipynb` file.

 ### Selecting the Correct Kernel

 When opening a notebook, make sure it is using the Conda environment created for this project.

 In Jupyter, the kernel should correspond to:

```
data230-group4-project-env
```

 If the environment does not appear as a selectable kernel, install the Jupyter kernel package into the environment:

```
conda activate data230-group4-project-env
conda install ipykernel
```

 Then register the environment as a Jupyter kernel:

```
python -m ipykernel install --user --name data230-group4-project-env --display-name "Python (data230-group4-project-env)"
```

 Restart Jupyter and select:

```
Python (data230-group4-project-env)
```

 as the notebook kernel.

 ## 7\. Running the Project

 Once the environment has been created and activated, project files should be run from the project's root directory.

 For example:

```
conda activate data230-group4-project-env
cd data230-group4-project
```

 Then run scripts or notebooks as needed.

 Running the project from the repository root is recommended because some files may rely on relative paths to project data, modules, or other resources.

 ## 8\. Updating the Environment

 If `environment.yml` is updated with additional dependencies, update the existing environment rather than creating a new one:

```
conda env update -f environment.yml --prune
```

 The `--prune` option removes packages that are no longer specified in `environment.yml`.

 After updating, verify the environment:

```
conda list
```

 ## 9\. Recreating the Environment

 If the environment becomes corrupted or you want to start from a clean installation, you can remove and recreate it.

 First, deactivate the environment:

```
conda deactivate
```

 Then remove it:

```
conda env remove -n data230-group4-project-env
```

 Recreate it using:

```
conda env create -f environment.yml
```

 Finally, activate it:

```
conda activate data230-group4-project-env
```

 ## 10\. Troubleshooting

 ### Conda cannot find `environment.yml`

 Make sure you are running the command from the directory containing the file:

```
ls
```

 You should see:

```
environment.yml
```

 If the file is located elsewhere, provide its path:

```
conda env create -f path/to/environment.yml
```

 ### The environment already exists

 If you see an error indicating that the environment already exists, activate it:

```
conda activate data230-group4-project-env
```

 If you need to recreate it from scratch, remove the existing environment first:

```
conda deactivate
conda env remove -n data230-group4-project-env
conda env create -f environment.yml
```

 ### A package is missing

 First make sure the correct environment is active:

```
conda activate data230-group4-project-env
```

 Then update the environment:

```
conda env update -f environment.yml
```

 If a package is still missing, check that it is listed in `environment.yml`.

 ### Jupyter is using the wrong Python environment

 Check which Python executable is being used:

```
which python
```

 On Windows, use:

```
where python
```

 The path should point to the Conda environment created for this project.

 You can also check the active Conda environment:

```
conda info --envs
```

 Make sure the intended environment has the `*` next to it.

 ## 11\. Recommended Workflow

 For each new session, activate the project environment before running any code:

```
cd data230-group4-project
conda activate data230-group4-project-env
```

 Then run the desired script or launch Jupyter:

```
jupyter lab
```

 or:

```
python path/to/script.py
```

 ## Quick Start

 For users who already have Conda installed, the basic setup is:

```
# Navigate to the project
cd data230-group4-project

# Create the environment
conda env create -f environment.yml

# Activate the environment
conda activate data230-group4-project-env

# Launch Jupyter
jupyter lab
```

 Once the environment is activated, the project's Python files and Jupyter notebooks should use the dependencies specified in `environment.yml`.

 ## Notes

 - Always activate the project's Conda environment before running project code.
- Run commands from the project's root directory when possible.
- Use the Jupyter kernel associated with the project environment when running notebooks.
- Do not manually install additional packages unless necessary. If a dependency is required by the project, consider adding it to `environment.yml` so that other users can reproduce the same environment.
- If `environment.yml` changes, update the environment with:

```
conda env update -f environment.yml --prune
```
- Although Jupyter is not included in `environment.yml`, you can use **Visual Studio Code** to edit project files. If you would like to use Jupyter, simply install the library:
```
conda activate data230-group4-project-env   # Make sure the environment is active
conda install jupyter
```
