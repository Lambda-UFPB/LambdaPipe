
# PHARMISA - Pharmacophoric Interaction Search & ADMET Integration System

## Installation

### Installing R Packages:
Go to the [pharmisa_download](link) and download the content of the "R package installation" folder. Follow the Guia.txt for the installation of R and the packages that pharmisa will use.

### Installing Pharmisa:
```bash
pip install --trusted-host 192.168.0.14 -i http://192.168.0.14:3141/kdunorat/pharmisa_index pharmisa
```
After installation, do:  
```bash
pharmisa --version 
```
to check if the program has been installed correctly.

To update the program:
```bash
pip install --upgrade pharmisa
```

## Usage
```bash
pharmisa [PATH TO THE RECEPTOR] [PATH TO THE LIGAND] [OPTIONS] 
```

### OPTIONS
- `-r, --rmsd`: RMSD limit for filtering results. Default = 7.0
- `--score`: Score limit for filtering results
- `-p, --pharma`: This option activates a menu to select pharmacophores interactively
- `-s, --session`: If you want to run a session already done in pharmit.
- `--plip_csv`:  PLIP csv file for pharmacophoric search optimized by the database.
- `--slow`: Performs the search in two parts to reduce memory load.
- `--process`: Only processes the results of a folder, without having to go back to pharmit.
- `-o, --output`: Name of the final folder that will contain the results. If absent, the program will create a random name for the folder.
- `--help`: Shows the help message.