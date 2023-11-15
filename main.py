#import asyncio
import uvicorn, os, requests, boto3, json, datetime
from dotenv import load_dotenv
from contextlib import suppress
load_dotenv()

os.environ["AWS_DEFAULT_REGION"] = os.getenv('AWS_REGION') or ""
print(" REGION:", os.getenv('AWS_REGION'))
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('weary-ox-ringCyclicDB')

#response = table.scan().get('Items') or {}
#for data in response:
#    if data['type'] == 'target':
#        print(data)
#        response = table.delete_item(Key={'pk': data['pk'],'sk':data['sk']})
#exit()
try:
    table_items = table.scan()['Items']
    print(table_items)
    targets = {x['pk']:x for x in table_items if x.get('type') == 'target'}
    receivers = {x['pk'] for x in table_items if x.get('type') == 'receiver'}
    table_items = None
except Exception as e:
    targets = {}
    receivers = []
    print(" Error:",e)
#print(targets)
#print(receivers)
#exit()
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
                url = 'https://api.henrikdev.xyz/valorant/v3/by-puuid/matches/ap/{}?size=1'.format(puuid)
                try:
                    response = requests.get(url, headers={'accept': 'application/json'}, timeout=10).json()['data'][0]
                    match_end_ts = response['metadata']['game_start']+response['metadata']['game_length']
                    if not match_end_ts == targets[puuid].get('last_match_ts'):
                        print(" match time not same")
                        try:
                            for _id in receivers:
                                _name_tag = str(targets[puuid].get('name'))+"#"+str(targets[puuid].get('tag'))
                                _dt_object = datetime.datetime.fromtimestamp(match_end_ts).strftime("%b %d, %I:%M %p")
                                _message = "{}\n{}".format(_name_tag,_dt_object)
                                print(" sending message:",_message)
                                if await send_message(_id, _message):
                                    table.update_item(Key={'pk': puuid,'sk': 'sort_key'},UpdateExpression='SET last_match_ts = :val1',ExpressionAttributeValues={':val1': match_end_ts})
                                    targets[puuid]['last_match_ts'] = match_end_ts
                        except Exception as e:
                            print(" Error:",e)
                    else:
                        print(" already sent.")
                except Exception as e:
                    print("Error:",e)
                print(puuid)

        elif scope['path'] == '/webhook':
            if query.get('hub.mode') == 'subscribe' and query.get('hub.challenge'):
                if query.get('hub.verify_token') == os.getenv('PASS'):
                    await send({'type': 'http.response.start','status': 200,'headers': [],})
                    await send({'type': 'http.response.body','body': query.get('hub.challenge').encode(),})
                else:
                    print(" Invalid Hub Token!")

        elif scope['path'] == '/delete':
            for _pk in targets:
                try:
                    table.delete_item(Key={'pk': _pk,'sk':'sort_key'})
                except Exception as e:
                    print(" Error:",e)
            targets = {}



    elif scope['method'] == 'POST':
        if scope['path'] == '/':
            print(" webroot post")
        elif scope['path'] == '/webhook' and 'facebook-api-version' in headers:
            print(" webhook post")
            with suppress(json.JSONDecodeError,TypeError): data={};data=json.loads(body)
            with suppress(KeyError): sender_id=None; sender_id = data['entry'][0]['messaging'][0]['sender']['id']
            with suppress(KeyError): sender_text=""; sender_text = data['entry'][0]['messaging'][0]['message']['text']
            if sender_id and sender_text:
                if sender_text == os.getenv('PASS'):
                    try:
                        table.put_item(Item={'pk': sender_id,'sk': "sort_key", 'type':'receiver'})
                        if not sender_id in receivers: receivers.append(sender_id)
                    except Exception as e:
                        print(" Error:",e)

                else:
                    url = None
                    if "#" in sender_text and len(sender_text.split("#")) == 2:
                        url = 'https://api.henrikdev.xyz/valorant/v1/account/{}/{}?force=true'.format(sender_text.split("#")[0],sender_text.split("#")[1])
                    if "-" in sender_text and len(sender_text.split("-")) == 5:
                        url = "https://api.henrikdev.xyz/valorant/v1/by-puuid/account/{}?force=true".format(sender_text)
                    if url:
                        print(" adding target:",url)
                        try:
                            response = requests.get(url, headers={'accept': 'application/json'}).json()['data']
                            table.put_item(Item={'pk': response['puuid'],'sk': "sort_key", 'type':'target', 'name':response.get('name'), 'tag':response.get('tag'), 'region':response.get('region')})
                            #targets.append(response['puuid'])
                            targets.update({response['puuid']:{'name':response['name'],'tag':response['tag'],'region':response['region']}})
                            print(" target added")
                        except Exception as e:
                            print(" Error:",e)





    await send({'type': 'http.response.start','status': 200,'headers': [[b'content-type', b'text/plain'],],})
    await send({'type': 'http.response.body','body': b'Hello, World!',})
















if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8181, log_level="critical")
































#
