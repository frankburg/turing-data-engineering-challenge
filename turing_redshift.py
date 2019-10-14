import boto3
import pandas as pd
import sqlalchemy as sa
from sqlalchemy.schema import CreateTable
from botocore.exceptions import ClientError
from io import StringIO
import uuid
from git.repo.base import Repo
import json
import pandas_redshift as pr
import s3fs
from botocore.client import Config


#access to the bucket and the file
config = Config(connect_timeout=5, retries={'max_attempts': 0})
client = boto3.client('s3', config=config)
obj = client.get_object(Bucket='turing-repo', Key='url_list.csv')
body = obj['Body']
csv_string = body.read().decode('utf-8')

repo_url = pd.read_csv(StringIO(csv_string))

s3_resource =boto3.resource('s3')

def create_bucket_name(bucket_prefix):
    # The generated bucket name must be between 3 and 63 chars long
    return ''.join([bucket_prefix, str(uuid.uuid4())])

def create_bucket(bucket_name, s3_connection):
    session = boto3.session.Session()
    current_region = session.region_name
    #bucket_name = create_bucket_name(bucket_prefix)
    bucket_response = s3_connection.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={
        'LocationConstraint': current_region})
    print(bucket_name, current_region)
    return bucket_name, bucket_response

#set up the SQLAchemy engine 
engine=sa.create_engine('redshift+psycopg2://awsuser:Redshift1@redshift-cluster-1.cug5ajtfsvsw.us-west-2.redshift.amazonaws.com:5439/dev')
metadata = sa.MetaData()

def create_json(bucket):
    #Creating a JSON file for each repo
    file_json=dict()
    for obj in bucket.objects.all():
        key = obj.key
        if key.endswith('.py'):
            body = StringIO(obj.get()['Body'].read())
            file_json.update({key:body})

            
access_key_id='AKIAX7S2O3HQFXIFAL55'
secret_access_key="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"
repo_list=repo_url['URLs']
redshift_tables=[]

fs = s3fs.S3FileSystem(anon=False) # accessing all buckets I have access to with my credentials
for url in repo_list[:3]:
    metadata = sa.MetaData()
    url=str(url)
    last=url.rsplit('/', 1)[-1] #get the repo name (last part) of the repository url
    try:
        print('### Processing Now ###')
        bucket_name = last + '-awjkmzz'
        print(bucket_name)
        if not fs.exists(bucket_name):
            print('### Resolving Bucket ###')
            bucket_name, response = create_bucket(bucket_name= bucket_name, s3_connection=s3_resource)         #Make folder for a repo if it does not exist
            print('BName: ',bucket_name)
            repo=str(url) + '.git'
            Repo.clone_from(repo,bucket_name)
            print('cloned ' , repo)
            #CLone repo in 
            for filename in glob.iglob(bucket_name + '/**/*.py', recursive=True):
                fs.put(filename, path=bucket_name+'/'+filename)
            os.rmdir(bucket_name)
        else:
            print('bucket existing: ',bucket_name)
    except:
        continue
        
    json_dict=create_json(bucket_name)
    json_name=last+'.json'
    print('### JSON Creation  ###')
    put_in = client.put_object(Bucket='repository-json', Body =json_dict, Key=json_name )
    
    repos = sa.Table(
    last,
    metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('data', sa.String),
    redshift_diststyle='KEY',
    redshift_distkey='id',
    redshift_interleaved_sortkey=['id', 'data'],
     )
    print('### Table Schema Created ###')
    bucket_name, response = create_bucket(bucket_prefix= last, s3_connection=s3_resource)
    
    CreateTable(repos)
    obj_name = client.get_object(Bucket='repository-json', Key=json_name)
 
    load=sa.commands.CopyCommand(repos,obj_name,access_key_id=access_key_id,secret_access_key=secret_access_key,path_file=obj_name)
    redshift_tables.append(last)
    print(str(repos.compile(dialect=RedshiftDialect(), compile_kwargs={'literal_binds': True})))
    print(dir(repos))
    

    connection = engine.connect()
    connection.execute(repos.execution_options(autocommit=True))
    connection.close()
    return file_json  


pr_redshift=pr.connect_to_redshift(dbname = 'dev',
                        host = 'redshift-cluster-1.cug5ajtfsvsw.us-west-2.redshift.amazonaws.com',
                        port = 5439,
                        user = 'awsuser',
                        password = 'Redshift1')

for table in redshift_tables: 
    data = pr.redshift_to_pandas('select * from table')
    data_ =data['data']
    
def get_modules_and_for_position(file):
    imports = []
        
    #Get all imported Modules

    result = re.findall(r"(?<!from)import (\w+)[\n.]|from\s+(\w+)\s+import", file)
#        imports=[i for imp in result for i in imp if len(i)and i not in imports]
    for imp in result:
        for i in imp:
            if len(i)and i not in imports:
                imports.append(i)

    # Get the position of all for loops in a script 

    for_position=[]
    for cnt, line in enumerate(file):
        p = re.compile("for")
#            for_position=[m.start() for m in p.finditer(line)]
        for m in p.finditer(line):
            for_position.append(m.start())

    return imports,for_position    
