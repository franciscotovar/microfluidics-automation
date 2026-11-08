# Tecan Cavro XE1000 — Python Setup (Windows)

This folder contains Python tools for communicating with and controlling Tecan Cavro XE1000 syringe pumps. Follow the instructions below to set up a dedicated Conda environment named `research` and run the scripts in Visual Studio Code (VS Code).

## 1. Install the required software

Install the following if they are not already available on your computer:

- **Miniforge (Windows):** https://github.com/conda-forge/miniforge
- **Git:** https://git-scm.com/downloads/win
- **Visual Studio Code:** https://code.visualstudio.com/
- **Python extension for VS Code** (publisher: Microsoft)

You do **not** need to install Python separately: Miniforge will create the Python environment for this project.

## 2. Clone or update the repository

Open **Miniforge Prompt** from the Windows Start menu.

If you have not cloned the repository, choose a folder where you want to keep the project and run:

```bat
git clone https://github.com/franciscotovar/microfluidics-automation.git
cd microfluidics-automation\tecan
```

If you already have a local copy, open Miniforge Prompt, navigate to the repository folder, update it, and then enter `tecan`:

```bat
cd path\to\microfluidics-automation
git pull
cd tecan
```

All remaining setup commands assume that the current directory is **`microfluidics-automation\tecan`**.

## 3. Create the Conda environment

The following files should be in this `tecan` directory:

```text
tecan/
├── README.md
├── environment.yml
├── setup_windows.bat
└── python/
    ├── xe1000_controller.py
    └── ...
```

From **Miniforge Prompt**, run:

```bat
setup_windows.bat
```

The installer uses `environment.yml` to create a Conda environment called **`research`**, installs Python and the required packages (including `tecancavro` and `pyserial`), and checks that `tecancavro` can be imported.

**If `research` already exists:** the setup script stops without changing it. Do not delete an existing environment just to rerun setup; first check which packages it contains.

## 4. Activate and verify the environment

In **Miniforge Prompt**:

```bat
conda activate research
python -c "import sys; print(sys.executable)"
python -c "from tecancavro.models import XE1000; print('tecancavro OK')"
```

The Python path should end in something similar to `miniforge3\envs\research\python.exe`, and the second command should print:

```text
tecancavro OK
```

## 5. Configure VS Code

1. Open VS Code and choose **File → Open Folder…**.
2. Open the local `microfluidics-automation` repository folder.
3. Make sure the Microsoft **Python** extension is installed and enabled.
4. Press **Ctrl+Shift+P** and run **Python: Select Interpreter**.
5. Select the interpreter for **`research`**. If it is not listed, select **Enter interpreter path… → Find…** and locate `python.exe` inside your local `miniforge3\envs\research` directory.
6. Open a `.py` file in `tecan/python/` and choose **Run Python File in Terminal**.

If a VS Code terminal does not recognise `conda` or `python`, open **Miniforge Prompt** for the setup and verification commands above. Selecting an interpreter in VS Code and activating an environment in a shell are separate settings.

## 6. Before connecting to a pump

The COM port numbers can differ between computers or after USB reconnection. **Do not assume that COM7 or COM10 identifies a particular physical pump on your PC.**

The configuration used during the initial tests was:

| Pump | Syringe capacity | Reservoir / input port | Output port | COM port during initial tests |
|---|---:|---|---|---|
| Pump 1 | 250 µL | Right | Left | COM10 |
| Pump 2 | 1000 µL | Left | Right | COM7 |

Verify the physical syringe, tubing connections, valve orientation and assigned serial port before running any motion script. Connecting to a pump and querying its firmware does not identify its syringe capacity.

**Important:** XE1000 initialization moves the syringe plunger and valve. Only initialize when the fluidic connections are ready for that sequence. The control library may also attempt automatic reinitialization after certain errors; do not run unattended experiments until this behavior has been reviewed.

## 7. Run the project scripts

For a script inside `tecan/python/`, use the activated `research` environment and run it from that folder. For example:

```bat
cd python
python xe1000_first_move.py
```

**Note:** This example communicates with hardware and may cause motion. Run it only after checking its contents and confirming the connected pump configuration. For a software-only package check, use the import command in Section 4 instead.

## Troubleshooting

**`ModuleNotFoundError: No module named 'tecancavro'`**

Check that the terminal or VS Code is using the `research` interpreter. In the same terminal, run:

```bat
python -c "import sys; print(sys.executable)"
python -m pip show tecancavro
```

**`python` opens the Microsoft Store / is not found**

The current shell is not using the Conda environment. Activate `research` in Miniforge Prompt or select the correct interpreter in VS Code.

**The pump cannot be contacted**

Check the actual serial port in Windows Device Manager, confirm that the pump is powered and connected, and ensure no other program has opened the same COM port. Do not change the configured syringe capacity merely to address a communication error.

## Project links

- Repository: https://github.com/franciscotovar/microfluidics-automation
- Tecan folder: https://github.com/franciscotovar/microfluidics-automation/tree/main/tecan
- Python scripts: https://github.com/franciscotovar/microfluidics-automation/tree/main/tecan/python
