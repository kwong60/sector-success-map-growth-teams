import pandas as pd
import os

def pandas_convert(path: str, file_name: str):
    """
    Converts Stata DTA file to pandas (Python library) dataframe.
    
    Input:
        path - path to DTA file 
        name - name of DTA file
    """
    # converts STATA DTA file to pandas dataframe
    df = pd.read_stata(path) 

    # saves pandas dataframe as a CSV (same name, same directory as 
    # original DTA file)
    directory = os.path.dirname(path)
    csv_path = os.path.join(directory, file_name + '.csv')
    df.to_csv(csv_path, index=False)

# extracts path of data folder 
# assumes DTA files are in folder titled "data", in same folder as preprocessing.py)
data_path = os.path.join(os.path.dirname(__file__), 'data')

for file in os.listdir(data_path):
    # extracts name and extension of each file
    base_name = os.path.basename(file)
    name, ext = os.path.splitext(base_name)

    # checks file type of each file in "data" folder
    if ext.lower() == '.dta':
        # extracts path name of given file and inputs into pandas conversion function
        file_path = os.path.join(data_path, file)
        pandas_convert(file_path, name)
