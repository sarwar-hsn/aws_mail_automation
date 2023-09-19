import boto3
import time
import concurrent.futures
import queue

CHUNK_SIZE = 10
class Email:
    def __init__(self, mail_list, num_consumers=1):
        self.chunk_size = CHUNK_SIZE
        self.report_list= []
        self.start_index = 0
        self.end_index = CHUNK_SIZE
        self.mail_list = mail_list
        self.client = boto3.client('ses')
        self.queue = queue.Queue(maxsize=14)
        self.num_consumers = num_consumers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.num_consumers)
    
    def producer(self):
        while self.start_index < len(self.mail_list):
            chunk = self.mail_list[self.start_index:self.end_index]
            self.queue.put(chunk)
            self.start_index += len(chunk)
            self.end_index = min(self.end_index + 50, len(self.mail_list))
        
        # Add sentinel values for each consumer
        for _ in range(self.num_consumers):
            self.queue.put(None)
    def consumer(self,template_name,template_data):
        while True:
            chunk = self.queue.get()
            if chunk is None:  # If we encounter the sentinel value
                self.queue.task_done()  # Mark the task as done
                break
            print(f"sending mails to :{chunk}")
            self._send_bulk_mail(email_list=chunk,template_name=template_name,template_data=template_data)
            self.queue.task_done()
            time.sleep(1)

    def start_bulk_mail_sending(self,template_name,template_data):
        self.report_list = []
        self.executor.submit(self.producer)
        # Start the consumers in the specified number of threads
        for _ in range(self.num_consumers):
            self.executor.submit(self.consumer,template_name,template_data)
        
        self.executor.shutdown()  # Wait for all threads to finish
        #all email has been seent, now let's print report

        print(f"Falied mails:{self.report_list}")

    

    def _send_bulk_mail(self, template_name, email_list,template_data, sender_mail='"Clysterum" <noreply@clysterum.com>'):
        destinations = []
        for email in email_list:
            destinations.append({
                'Destination': {
                    'ToAddresses': [email]
                },
                'ReplacementTemplateData': template_data
            })
        try:
            response = self.client.send_bulk_templated_email(
                Source=sender_mail,
                Template=template_name,
                DefaultTemplateData="{'name':'User'}",
                Destinations=destinations
            )
            for e in response.get('Status'):
                if e.get('Status') == 'Success':
                    print(f"Email Sent:{e.get('MessageId')}")
                else:
                    self.report_list.append(e)
        except:
            print(f"sent failed for chuck: {destinations}")


    def get_quota(self):
        response = self.client.get_send_quota()
        max_24_hour_send = response.get('Max24HourSend')
        sent_last_24_hours = response.get('SentLast24Hours')
        sent_rate = response.get('MaxSendRate')
        left_in_24_hours = max_24_hour_send - sent_last_24_hours;
        res = {
            'max_24_hour_send':max_24_hour_send,
            'sent_last_24_hours':sent_last_24_hours,
            'left_in_24_hours':left_in_24_hours,
            'sent_rate/sec':sent_rate
        }
        return res

    def get_statistics(self):
        data_points = self.client.get_send_statistics().get('SendDataPoints')
        for i in range(len(data_points)):
            item = data_points[i]
            time = item.get('Timestamp')
            attempt = item.get('DeliveryAttempts')
            reject = item.get('Rejects')
            print(f"Time:{time}\tAttempt:{attempt}\tReject:{reject}")

    def create_template(self,template_name,subject,text_filename,html_filename):
        html_file_path = f"templates/{html_filename}"
        text_file_path = f"templates/{text_filename}"
        try:
            with open(html_file_path,'r') as fd:
                html_file = fd.read()
            with open(text_file_path,'r') as tfd:
                text_file = tfd.read()
            self.client.create_template(
                Template={
                    'TemplateName': template_name,
                    'SubjectPart': subject,
                    'TextPart': text_file,
                    'HtmlPart': html_file
                }
            )
            return True
        except:
            return False
        
    def get_template(self,template_name):
        try:
            response = self.response = self.client.get_template(
                TemplateName=template_name
            )
            res = response.get('Template')
            return {
                'name':res.get('TemplateName'),
                'subject':res.get('SubjectPart'),
                'text':res.get('TextPart'),
                'html':res.get('HtmlPart'),
            }
        except:
            return None
        

    def delete_template(self,tname):
        try:
            response = self.client.delete_template(TemplateName=tname)
            return True
        except:
            return False


    def list_verified_mails(self):
        verified_mails = self.client.list_verified_email_addresses()
        print(verified_mails.get('VerifiedEmailAddresses'))


    def list_templates(self):
        try:
            response = self.client.list_templates()
            response = response['TemplatesMetadata']
        except:
            return None
        return response


        