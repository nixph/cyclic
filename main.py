#import asyncio
import uvicorn, os, requests, boto3, json, datetime, pyhenrik, pytz
from dotenv import load_dotenv
from contextlib import suppress
load_dotenv()
old_timezone = pytz.timezone("UTC")
new_timezone = pytz.timezone("Asia/Manila")

os.environ["AWS_DEFAULT_REGION"] = os.getenv('AWS_REGION') or ""
print(" REGION:", os.getenv('AWS_REGION'))
try:
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('weary-ox-ringCyclicDB')
except Exception as e:
    pass

try:
    targets = {x['pk']:x for x in table.scan()['Items']}
except Exception as e:
    targets = {}
print(targets)
#targets = {"0e475dc9-80fd-5133-aa64-644982b84caa":{'name':'JUNJUN','tag':'2393'}}

#table_items = [{'pk':'0e475dc9-80fd-5133-aa64-644982b84caa'}]
async def send_message(_id, _message):
    url = "https://graph.facebook.com/{}/{}/messages".format(os.getenv('MESSENGER_GRAPH_VERSION'),os.getenv('MESSENGER_PAGE_ID'))
    data = {'recipient':{'id':_id},'messaging_type':'RESPONSE','message':{'text':_message},'access_token':os.getenv('MESSENGER_TOKEN')}
    try:
        response = requests.post(url, json=data)
        if response.ok: return True
    except Exception as e:
        print(" Error Sending Message:",e)
        return
    print(response.content)

async def parse_query(_query):
    return {x.split("=")[0]:x.split("=")[1] for x in _query.decode('utf-8').split("&") if len(x.split("=")) == 2}

async def parse_headers(_headers):
    return {x[0].decode():x[1].decode() for x in _headers if len(x) == 2}

async def main():
    query_string = await parse_query(scope['query_string'])
    print(query_string)

#asyncio.run(main())
async def read_body(receive, more_body=True):
    body = b''
    while more_body:
        message = await receive()
        body += message.get('body', b'')
        more_body = message.get('more_body', False)
    return body

async def app(scope, receive, send):
    print(" Found! Path:",scope['path'],"Method:",scope['method'])
    body = await read_body(receive)
    query = await parse_query(scope['query_string'])
    headers = await parse_headers(scope['headers'])

    if scope['method'] == 'GET':
        if scope['path'] == '/':
            print(" webroot get")
            for puuid in targets:
                print(" PUUID:",puuid)
                last_match_ts = pyhenrik.get_last_match_ts(puuid)
                if last_match_ts and not last_match_ts == targets[puuid].get('last_match_ts'):
                    print(" sending message.")
                    _name_tag = targets[puuid].get('name')+"#"+targets[puuid].get('tag')
                    #_dt_object = datetime.datetime.fromtimestamp(last_match_ts).strftime("%b %d, %I:%M %p")
                    _dt_object = datetime.datetime.fromtimestamp(last_match_ts).astimezone(new_timezone).strftime("%b %d, %I:%M %p")
                    if await send_message(os.getenv('MESSENGER_ID'), "{}\n{}".format(_name_tag, _dt_object)):
                        table.update_item(Key={'pk': puuid,'sk': 'sort_key'},UpdateExpression='SET last_match_ts = :val1',ExpressionAttributeValues={':val1': last_match_ts})
                        targets[puuid].update({'last_match_ts':last_match_ts})
                #print(last_match_ts)
        elif scope['path'] == '/del':
            deleted_puuid = []
            for puuid in targets:
                try:
                    table.delete_item(Key={'pk': puuid,'sk':"sort_key"})
                    deleted_puuid.append(puuid)
                except Exception as e:
                    print(" Error:",e)
            for puuid in deleted_puuid:
                with suppress(KeyError): targets.pop(puuid)


    elif scope['method'] == 'POST':
        if scope['path'] == '/add':
            with suppress(json.JSONDecodeError,TypeError): data={}; data=json.loads(body)
            url = "https://api.henrikdev.xyz/valorant/v1/by-puuid/account/{}?force=true".format(data['puuid']) if 'puuid' in data else None
            url = "https://api.henrikdev.xyz/valorant/v1/account/{}/{}?force=true".format(data['name'],data['tag']) if not url and 'name' in data and 'tag' in data else url
            print(" add target:",url)
            response = pyhenrik.get_account(url)
            if response.get('puuid'):
                table.put_item(Item={'pk': response['puuid'],'sk': "sort_key", 'name':response.get('name'), 'tag':response.get('tag'), 'region':response.get('region')})
                targets.update({response['puuid']:{'name':response['name'],'tag':response['tag'],'region':response['region']}})
            #print(response)

    await send({'type': 'http.response.start','status': 200,'headers': [[b'content-type', b'text/plain'],],})
    await send({'type': 'http.response.body','body': b'Hello, World!',})



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8181, log_level="critical")
































#
