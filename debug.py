import boto3, os, requests
from dotenv import load_dotenv
load_dotenv()
#print(os.getenv('AWS_ACCESS_KEY_ID'))


#url = 'https://api.henrikdev.xyz/valorant/v3/by-puuid/matches/ap/97aa9366-45c5-5188-988c-a21d86b8aa30?size=1'

url = "http://localhost:8181/add"
data = {"name":"JUNJUN","tag":"2393"}
response = requests.post(url, headers={'accept':'application/json'}, json=data, timeout=10)
print(response.content)

exit()
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('amaranth-hippopotamus-sariCyclicDB')
put_response = table.put_item(Item={'pk': "new_sample_puuid",'sk': "sort_key", 'last_active':2})
print(put_response)
#exit()


response = table.scan().get('Items') or {}
for data in response:
    print(data)
    #response = table.delete_item(Key={'pk': data['pk'],'sk':data['sk']})
    #print(response)
    #response = table.delete_item(Key={'pk': d['pk']})
    #print(response)
#print(data)
exit()
# create an item in the database with key "leo"

# get an item at key "partition_key", "sort_key" from the database
#get_response = table.get_item(Key={'pk': "partition_key", 'sk': "sort_key"})
get_response = table.get_item(Key={'pk': "new_sample_puuid", 'sk': "sort_key"})
print(get_response)
