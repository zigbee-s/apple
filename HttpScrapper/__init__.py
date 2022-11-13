from ast import keyword
from cProfile import run
import logging
import multiprocessing
import os
import azure.functions as func
from io import BytesIO

# Execute crawler in a new thread
# Version = v1.2.0

def runSpiderOnNewThread(keyword,url, taskid):
    from utils.run_spider import RunSpider
    print("Running spider on a new thread")
    spider = RunSpider()
    spider.execute_crawling(keyword, url, taskid)


# Http Triggered Function
def main(req: func.HttpRequest,  outputblob: func.Out[bytes]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    keyword = req.params.get('keyword')
    url = req.params.get('url')
    taskid = req.params.get('taskid')
   
    if not keyword:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            keyword = req_body.get('keyword')
            url = req_body.get('url')
            taskid = req.body('taskid')

    if keyword and url and taskid:
        filename = taskid + ".txt"
        
        logging.info("Creating a new thread to run spider and rector")
        pr1 = multiprocessing.Process(target=runSpiderOnNewThread,args=(keyword,url,taskid,))
        pr1.start()
        pr1.join()
        
        
        # Read from a file
        logging.info("Reading from the file")
        text = ""
        f = open(filename, "r")
        for x in f:
            text = text + x
        
        # Send file to blob storage
        logging.info("Sending file to blob storage")
        with open(filename, "rb") as fh:
            buf = BytesIO(fh.read())
            outputblob.set(buf.getvalue())

        # Delete a file 
        logging.info("Deleting file")
        os.remove(filename)
        return func.HttpResponse(f"{text}")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. make sure you provided keyword, url and taskid to get a personalized response.",
             status_code=200
        )
