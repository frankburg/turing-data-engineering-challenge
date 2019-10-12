#! /usr/bin/env python3


import os
import glob
from git.repo.base import Repo
import pandas as pd
import pygount
import re
import numpy as np
import json
from getpass import getpass

#get the csv of the repositories and use gitpython to clone each of the repo

repo_url=pd.read_csv('url_list.csv')
repo_url.tail()
repo_list=repo_url['URLs']

#For the cloning the repo
def clone_repo(start=0,end=100000):
    """
    Clones the GitHub repositories if the repositories has not been cloned initially. 
    
    Parameters:
    start(int): This is an integer that specifies which URL cloning should start from in the CSV file  of     the GitHub repositories. Defaults to zero.
    end(int): This is an integer that specifies which URL cloning should end in the CSV file  of       the GitHub repositories. Defaults to 100000, which is the last URL.
    
    Returns:
    count(int): The number of repository cloned.
    
    """
    repo_list=repo_url['URLs']
    count=0

    for url in repo_list[start:end]:
        url=str(url)
        name=url.rsplit('/', 2) #get the repo name (last 2 part) of the repository url
        last=name[-2]+'-'+name[-1]
        try:
            if not os.path.exists(last):
                os.mkdir(last)         #Make folder for a repo if it does not exist
                repo=str(url) + '.git'
                folder= r'repos'
                project_dir = os.path.dirname(os.path.abspath(__file__))
                os.environ['GIT_ASKPASS'] = os.path.join(project_dir, 'askpass.py')
                os.environ['GIT_USERNAME'] = frankburg
                os.environ['GIT_PASSWORD'] = getpass()
                Repo.clone_from(repo,last)
                count+=1
                print('cloned ' , repo)
        except:
            continue
    return count
            
            
def unique(list1):
    """
    Fetches unique elements in a list.
    
    Parameters:
    list1(list): A list
    Returns:
    unique_list(list): List containing unique elements in the input list
    
    """
  
    # intilize a null list 
    unique_list = [] 
      
    # traverse for all elements 
    for x in list1: 
        # check if exists in unique_list or not 
        if x not in unique_list: 
            unique_list.append(x)
    return unique_list 

def imported_module(file):
    """
    Fetches all external libraries used in a Python script.
    
    Parameters:
    file(path): The path to the Python script.
    Returns:
    imports(list): A list of all external libraries used in a Python script.
    
    """
    imports = []
    with open( file,encoding="utf8",errors='ignore') as f:
        
        #Get all imported Modules
        
        lines = f.read()
        result = re.findall(r"(?<!from)import (\w+)[\n.]|from\s+(\w+)\s+import", lines)
        for imp in result:
            for i in imp:
                if len(i)and i not in imports:
                    imports.append(i)
        
    return imports

def for_loop_position(file): 
    """
    Returns the position of for loops  for each line in a Python script.
    
    Parameter:
    file(path): The path to the Python script.
    Returns:
    for_position(list): A list of the position of for loops  for each line in a Python script.
    
    """
    for_position=[]
    with open( file,encoding="utf8",errors='ignore') as f: 
        #Remove Comments
        f = filter(lambda x: not re.match(r'(?m)^ *#.*\n?', x), f)
        f=list(f)
        for_position=[]
        for cnt, line in enumerate(f):
            fn_match = re.search('^(?=.*for)(?!.*for\w+)(?!.*\[)(?!.*\{)(?!.*\*=)(?!.*\')(?!.*responseformat)(?!.*#).*', line)
            if fn_match:
                p = re.compile("for")
                for m in p.finditer(line):
                    for_position.append(m.start())
    return for_position 

def variable_count(file):
    """
    Returns the count of variables for a line that has variable(s) in a Python script.
    
    Parameters:
    file(path): The path to the Python script.
    Returns:
    var_count(list): A list of the count of variables for a line that has variable(s) in a Python script.
    
    """
    var_count=[]
    with open(file,encoding="utf8",errors='ignore') as f:
        for cnt, line in enumerate(f):
            #Get lines that have = but not ==, +=, -=,*=,etc.
            fn_match = re.search('^(?=.*=)(?!.*==)(?!.*-=)(?!.*\+=)(?!.*\*=)(?!.*import)(?!.*def)(?!.*;).*', line)
            if fn_match:
                var=line.split('=',1)[0]
                var_c=var.split(',')
                var_count.append(len(var_c))
    return var_count

def parameter_count(file):
    """
    Returns the counts of parameters in each function in a Python Script.
    
    Parameters:
    file(path): The path to a Python script.
    Returns:
    param_count(list): A list of the counts of parameters in each function in a Python Script.
    
    """
    param=[]
    param_count=[]
    with open(file,encoding="utf8",errors='ignore') as f:

        for cnt, line in enumerate(f):
            #Check if a line begins with def 
            if re.search("def", line):
                #Get the function name and parameter
                r=re.search('(?:def\s).*', line)
            else:
                continue
            if r:
                l=str(r.group())
                p=l.split(',')
                p[-1]=p[-1][:-1]
                r= p[0].split('(')
                
                if len(p)>1:
                    
                    first=r[-1]
                    last=p[-1][:-1]
                    param.append(first)
                    param.append(last)
               
                    for i in p[1:-1]:
                        param.append(i)
                else:
                    param.append(r[-1].split('(')[-1][:-1])
                if not param:
                    param_count.append(0)
                else:    
                    param_count.append(len(param))
                param=[]

    return param_count

def duplicated_line(filename):
    """
    Returns the total numbers of four consecutive line repeated in a script.
    
    Parameters:
    filename(path): The path to a Python file
    Returns: 
    duplicate(int): Total numbers of four consecutive line repeated in a script.
    
    """
    duplicate=0
    with open(filename,encoding="utf8",errors='ignore') as f:
        scripts=f.readlines()
        #Removes whitespace and blank line 
        scripty = filter(lambda x: not re.match(r'^\s*$', x), scripts)
        #Removes Comments
        script = filter(lambda x: not re.match(r'(?m)^ *#.*\n?', x), scripty)
        script=list(script)
    with open(filename,encoding="utf8",errors='ignore') as f:
        files=f.readlines()
        #Removes whitespace and blank line 
        filey = filter(lambda x: not re.match(r'^\s*$', x), files)
        #Removes Comments
        file = filter(lambda x: not re.match(r'(?m)^ *#.*\n?', x), filey)
        file=list(file)
        for cnt, line in enumerate(file):
            if cnt <= len(file)-4:
                for i,item in enumerate(script):
                    #Dont compare with that same line and the next 3 line, and don't compare with the last 3 lines
                    if cnt != i and i!=cnt+1 and i!=cnt+2 and i!=cnt+3 and i<= len(script)-4  :
                        if line == item and file[cnt+1]==script[i+1] and file[cnt+2]==script[i+2] and file[cnt+3]==script[i+3]:
                            duplicate+=4
                            #delete the duplicates in file and script
                            del file[i:i+4]
                            del script[i:i+4]

    return duplicate

def nesting_factor(for_position):
    """
    Returns the depth of all for loops greater than one in a Python script.
    
    Parameters:
    for_position(list): The list of positions of for loop in a script.
    Returns:
    deg_list: list of degrees or depth of for loops in a script.
    
    """
    deg=1 
    deg_list=[]
    if for_position:
        for i,position in enumerate(for_position):
            #exempting the first item in the list of positions of for loops in a script
            if i !=0:
                #increases the depth by 1 if the difference btw current position and the previous is 4 
                if position - for_position[i-1] ==4:
                    deg+=1
                    continue
                #Update the degree list and degree when difference btw current position and the previous >= -(degree -1)X 4    
                if position - for_position[i-1] >= (1-deg)*4:
                    deg_list.append(deg)
                    deg=1
                    continue
                if for_position[-1] and deg>1:
                    deg_list.append(deg)
    return deg_list  

def str_to_raw(s):
    """
    Convert a string to a raw string, needed for conversion of file paths to raw. 
    
    Parameters:
    s(string): A string.
    Returns:
    raw value of the string.
    
    """
    raw_map = {8:r'\b', 7:r'\a', 12:r'\f', 10:r'\n', 13:r'\r', 9:r'\t', 11:r'\v'}
    return r''.join(i if ord(i) > 32 else raw_map.get(ord(i), i) for i in s)

def execute(root_dir):
    """
    Returns a dictionary containing the URL of a repository, number of lines, external libraries used , average nesting factor, percentage of code duplication, average number of parameters and average number of variables of the repository.
    
    Parameter:
    root_dir(path): Path to the local repository.
    Return:
    A dictionary containing the URL of a repository, number of lines, external libraries used , average nesting factor, percentage of code duplication, average number of parameters and average number of variables of the repository.
    
    """
    
    
    #Getting all the file recursively that py files
    lenght=[]
    libraries=[]
    nesting_factors=[]
    param_count=[]
    total_var=[]
    duplicate_for_the_repo=[]
    average_nesting_factor=0
    average_param=0
    code_duplication=0
    avg_var=0

    urls=[ repo for repo in repo_list  if root_dir in repo ]
    if urls:
        url=urls[0]
    else:
        url=root_dir

    for filename in glob.iglob(root_dir + '/**/*.py', recursive=True):
        filename=filename.replace(" ", "\\ ")
        filename=str_to_raw(filename)
         
        count=pygount.source_analysis(filename, 'pygount') # counting the line of codes for the py files
        l=count.code
        lenght.append(l)
        library =imported_module(filename)
        for lib in library:
            libraries.append(lib)
        deg_list=nesting_factor(for_loop_position(filename))    
        for deg in deg_list:
            nesting_factors.append(deg)

        
        
        for param in parameter_count(filename):
            param_count.append(param)
        for var in variable_count(filename):
            total_var.append(var)
        duplicate_for_the_repo.append(duplicated_line(filename))
        
    if len(nesting_factors) !=0:    
            average_nesting_factor= np.mean(nesting_factors)
    if param_count:        
        average_param= np.mean(param_count)    
    libraries=unique(libraries)
    repo_count=sum(lenght)
    if total_var:
        avg_var=np.mean(total_var)
    if repo_count and duplicate_for_the_repo:
        code_duplication=(sum(duplicate_for_the_repo)/repo_count)*100
    
    return {'repository_url': url, 
        'number of lines': repo_count, 
        'libraries': libraries,
        'nesting factor': average_nesting_factor,
        'code duplication': code_duplication,
        'average parameters':average_param,
        'average variables':avg_var}


result=[]
if __name__ == "__main__":
    clone_repo(start=0,end=34000)
    cloned_repo=next(os.walk('.'))[1]
    for repo in cloned_repo:
        result.append(execute(repo))
        results=json.dumps(result)
    with open('results.json','a') as f:
        f.write(results)
    print('Process successfully completed')     