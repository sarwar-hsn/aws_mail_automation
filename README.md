# aws_mail_automation

#install requirements
pip install -r requirements.txt

#for help 
python main.py --help

#mail list
your mail list can be in either .csv or .xls format
it should be present under mail_lists directory
the program will look for file under mail_lists

create folder named mail_lists under root directory: 
command:mkdir mail_lists
then put your mail list here

#templates
to create a template your template file should be under templates directory.
create a folder named templates under root directory
command:mkdir templates
then put your templates here to use create a template

#credentials
-linux
    your aws crdentials for linux should be in 
    ~/.aws/credentials file
    command: 
    mkdir ~/.aws
    touch credentials
-windows
    create follow the same process as linux but under 
    C:\Users\YourUserName directory

-file format
[default]
aws_access_key_id = 'AWS_ACCESS_KEY_ID'
aws_secret_access_key = 'AWS_SECRET_ACCESS_KEY'
region = 'REGION'

#aws bucket 
there is a bucket program to use that create a .env file under root directory and place your credentials
-format
AWS_BUCKET_REGION_NAME='REGION_NAME'
AWS_BUCKET_NAME='BUCKET_NAME'
AWS_BUCKET_ACCESS_KEY_ID='AWS_ACCESS_KEY_ID'
AWS_BUCKET_SECRET_ACCESS_KEY='AWS_SECRET_ACCESS_KEY'
AWS_BUCKET_ENDPOINT_URL='AWS_ENDPOINT_URL'

#file handling for bucket
create folder called upload under root directory
your files will be processed from here