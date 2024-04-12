
# PHARMISA - Pharmacophoric Interaction Search & ADMET Integration System

## Installation

### Installing R Packages:
Go to the [pharmisa_download](https://drive.google.com/drive/folders/1nLe4NSui-AeI6XceHdFu2nbj4Mz-6CBE) and download the content of the "R package installation" folder. Follow the Guia.txt for the installation of R and the packages that pharmisa will use.


## Usage
```bash
pharmisa [PATH TO THE RECEPTOR] [PATH TO THE LIGAND] [OPTIONS] 
```
To perform only a processing of pharmit results:
```bash
pharmisa --process [PATH TO THE FOLDER] [OPTIONS]
``` 

### OPTIONS
- `-r, --rmsd`: RMSD limit for filtering results. Default = 20.0
- `--score`: Score limit for filtering results. Default = -9.0
- `-p, --pharma`: This option activates a menu to select pharmacophores interactively
- `-s, --session`: If you want to run a session already done in pharmit.
- `--plip_csv`:  PLIP csv file for pharmacophoric search optimized by the database.
- `--slow`: Performs the search in two parts to reduce memory load.
- `--process`: Only processes the results of a folder, without having to go back to pharmit.
- '--only_admet': Only run the admet analysis on a file with a list of SMILES.
- `-o, --output`: Name of the final folder that will contain the results. If absent, the program will create a random name for the folder.
- `--help`: Shows the help message.