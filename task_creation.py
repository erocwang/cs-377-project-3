import boto3 
import xmltodict 
import json 

create_hits_in_production = False
environments = {
  "production": {
    "endpoint": "https://mturk-requester.us-east-1.amazonaws.com",
    "preview": "https://www.mturk.com/mturk/preview"
  },
  "sandbox": {
    "endpoint": 
          "https://mturk-requester-sandbox.us-east-1.amazonaws.com",
    "preview": "https://workersandbox.mturk.com/mturk/preview"
  },
}
mturk_environment = environments["production"] if create_hits_in_production else environments["sandbox"]
session = boto3.Session(profile_name='mturk')
client = session.client(
    service_name='mturk',
    region_name='us-east-1',
    endpoint_url=mturk_environment['endpoint'],
)

print(client.get_account_balance()['AvailableBalance'])

# to finish, need to add text box and edit existing format, move images to s3

images = ["https://ids.si.edu/ids/deliveryService?max_w=800&id=SAAM-1951.14.92_1"]

html_layout = open('./arteval.html', 'r').read()
QUESTION_XML = """<HTMLQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2011-11-11/HTMLQuestion.xsd">
        <HTMLContent><![CDATA[{}]]></HTMLContent>
        <FrameHeight>650</FrameHeight>
        </HTMLQuestion>"""
question_xml = QUESTION_XML.format(html_layout)

temp = question_xml.replace('${content}',images[0])

TaskAttributes = {
    'MaxAssignments': 5,           
    # How long the task will be available on MTurk (1 hour)     
    'LifetimeInSeconds': 60*60,
    # How long Workers have to complete each item (10 minutes)
    'AssignmentDurationInSeconds': 60*10,
    # The reward you will offer Workers for each response
    'Reward': '0.05',                     
    'Title': 'Test 1',
    'Keywords': 'sentiment, tweet',
    'Description': 'Rate the sentiment of a tweet on a scale of 1 to 10.'
}

results = []
hit_type_id = ''
for image in images:
    response = client.create_hit(
        **TaskAttributes,
        Question=question_xml.replace('${content}',image)
    )
    hit_type_id = response['HIT']['HITTypeId']
    results.append({
        'image': image,
        'hit_id': response['HIT']['HITId']
    })
    
print("You can view the HITs here:")
print(mturk_environment['preview']+"?groupId={}".format(hit_type_id))