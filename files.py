import pandas as pd
import os
import re

class File:
    def __init__(self):
        self.dir_name = 'mail_lists';

    #include name True will look for name column in excel files
    def read(self,filename,include_name=False):
        name,ext = os.path.splitext(filename)
        file_path = f"{self.dir_name}/{filename}"     
        
        try:
            if ext == ".csv":
                data = pd.read_csv(file_path).drop_duplicates()
            elif ext == '.xls':
                data = pd.read_excel(file_path).drop_duplicates()
            else:
                print("Error: only .csv and .xls are supported")
                return None
        except:
            data = None
            return None
        data = data.to_dict()
        emails =data.get('email')
        names =data.get('name')
        if include_name:
            try:
                mail_list = list(zip(emails.values(),names.values()))
                return mail_list
            except:
                return None
        else:
            return list(emails.values())
        

    #this function will extract variable from file `{{}}`
    #and will return a set . Set to discard duplicate items
    def extract_variables(self,filename):
        variables = set()
        pattern = r'{{(.*?)}}'
        matches = re.findall(pattern, filename)
        for match in matches:
            variables.add(match)
        return list(variables)
        
        