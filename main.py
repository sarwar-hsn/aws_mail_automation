from mail import Email
from files import File
from bucket import Bucket
import json
import argparse
from dotenv import load_dotenv
load_dotenv()


def send_function(args, send_parser, file_processor, mail_processor):
    if args.individual:
        print("individual mail not supported yet")
    else: #this is for bulk mail
        data = file_processor.read(args.file,include_name=args.name)
        if args.start:
            args.start-=2;
        if args.end:
            args.end-=1;
    
        if args.start and args.end:
            data = data[args.start:args.end]
        elif args.start:
            data = data[args.start:]
        elif args.end:
            data = data[:args.end]    

        if not data:
            print("Error: email list is empty")
            send_parser.print_help()
            exit(1)
        else:
            mail_processor.mail_list = data
            template = mail_processor.get_template(template_name=args.template)

            #looking for template
            if template is None:
                print(f"Error: no template named {args.template}")
                exit(1)
            else:
                template_data ={}

                print("Extracting template variable")
                print(f"subject:{template.get('subject')}")
                html = template.get('html')
                text_part = template.get('text')
                #looking for template variables
                html_variables =file_processor.extract_variables(html)
                text_file_variables = file_processor.extract_variables(text_part)
                variable_list = list(set(html_variables + text_file_variables))

                if variable_list:
                    print("Please Enter following placeholder values:\n")
                for var in variable_list:
                    try:
                        value = input(f"{var} : ")
                        template_data[var] = value
                    except:
                        print("Error: Invalid value")
                        exit(1)
            template_data = json.dumps(template_data)
            # if args.worker:
            #     mail_processor.num_consumers = args.worker
            mail_processor.start_bulk_mail_sending(template_name=args.template,template_data=template_data)

def template_function(args,template_parser,file_processor, mail_processor):
    if args.list:
        templates = mail_processor.list_templates()
        if templates:
            for t in templates:
                print(t)
        else:
            print('[]')
    elif args.create:
        template_name = input("Enter template name: ")
        subject = input("Enter subject of the mail: ")
        text_file_name= input("Enter Text file name (under templates dir): ")
        html_file_name = input("Enter html file name (under templates dir):")
        res = mail_processor.create_template(
            template_name,subject,text_file_name,html_file_name
        )
        if res is True:
            print(f"Template {template_name} created")
        else:
            print("Failed to create template")
    elif args.delete:
        if args.name is None:
            template_parser.print_help()
            template_parser.error("template name missing")
        else:
            isDeleted = mail_processor.delete_template(args.name)
            if isDeleted:
                print("template deleted")
            else:
                print("failed to delete template")

    elif args.name:
        info = mail_processor.get_template(template_name=args.name)
        for key,value in info.items():
            if key!='html':
                print(f"{key}\t\t: {value}")
            if key == 'html':
                print(f"var\t\t: {file_processor.extract_variables_from_html(value)}")



def main():
    file_processor = File()
    mail_processor = Email(mail_list=None)

    parser = argparse.ArgumentParser(description="Welcome to Clysterum mail processor")
    parser.add_argument('-s', '--stat', action='store_true', help='Show statistics')  
    subparsers = parser.add_subparsers(dest="command") 

    template_parser = subparsers.add_parser('template', help='Template Information')
    template_parser.add_argument('-n','--name',help="Get details of a template by name")
    template_parser.add_argument('-l','--list',action="store_true",help="List of email templates")
    template_parser.add_argument('-d','--delete',action="store_true", help="Delete template")
    template_parser.add_argument('-c','--create',action="store_true", help="Create a template")

    send_parser = subparsers.add_parser('send', help='Send bulk emails.')
    send_parser.add_argument('-i','--individual',action='store_true',help="If -i flag is set then it mails will be sent individually")
    send_parser.add_argument('-f', '--file', required=True, help='Filename of email list unser mail_lists directory', type=str)  # Made file required
    send_parser.add_argument('-t','--template',required=True,help="Template name"),
    send_parser.add_argument('-s', '--start', help='Start row num. Specifiy the start row num from specified file', type=int)
    send_parser.add_argument('-e', '--end', help='End row num. Specifiy the end row num from specified file', type=int)
    send_parser.add_argument('-n', '--name', action='store_true', help='If -n flag is used, the program will look for name column in specified file')
    # send_parser.add_argument('-w', '--worker',choices=range(1, 11), help='Number of worker threads.Max is 10 as of now. Default is 2.', type=int)
    

    args = parser.parse_args()


    if args.stat:
        print(mail_processor.get_quota())
        mail_processor.get_statistics()

    if args.command == 'template':
        template_function(args,template_parser,file_processor,mail_processor)

    if args.command == "send":
        send_function(args,send_parser,file_processor,mail_processor)
    
if __name__ == '__main__':
    #email main program
    try:
        main()
    except Exception as e:
        print(f"program initialization falied:{e}")


    ##comment out main and uncomment this section to use bucket functionalities
    # try:
    #     bucket = Bucket()
    #     # bucket.upload_image(local_file_name='app_overview_1.png',uploaded_file_name='app_overview_1.png')
    #     print(bucket.get_image_urls())
    # except Exception as e:
    #     print(f"Failed to initialize bucket:{e}")
