def domain_whitelist(domain='https://codingblock.herokuapp.com'):
    post_message_url = "https://graph.facebook.com/v2.6/me/thread_settings?access_token=%s"%(PAGE_ACCESS_TOKEN)
    response_object =     {
                "setting_type" : "domain_whitelisting",
                "whitelisted_domains" : [domain],
                "domain_action_type": "add"
              }
    response_msg = json.dumps(response_object)

    status = requests.post(post_message_url, 
                headers={"Content-Type": "application/json"},
                data=response_msg)

    logg(status.text,symbol='--WHT--')              


def save_message(fbid='1160786967320970',message_text='hi'):  
    url = 'https://graph.facebook.com/v2.6/%s?fields=first_name,last_name,profile_pic,locale,timezone,gender&access_token=%s'%(fbid,PAGE_ACCESS_TOKEN)
    print url
    resp = requests.get(url=url)
    data = json.loads(resp.text)

    name = '%s %s'%(data['first_name'],data['last_name'])
    p = Messages.objects.get_or_create(name=name,
      profile_url = data['profile_pic'],
      fb_id = fbid,
      gender = data['gender'],
      locale = data['locale'],
      message = message_text
      )[0]
    p.save()

    return json.dumps(data)



def scrape_spreadsheet():
    sheet_id = '1EXwvmdQV4WaMXtL4Ucn3kwwhS1GOMFu0Nh9ByVCfrxk'
    url = 'https://spreadsheets.google.com/feeds/list/%s/od6/public/values?alt=json'%(sheet_id)

    resp = requests.get(url=url)
    data = json.loads(resp.text)
    arr =[]

    for entry in data['feed']['entry']:
        d = {}
        for k,v in entry.iteritems():
            if k.startswith('gsx'):
                key_name = k.split('$')[-1]
                d[key_name] = entry[k]['$t']

        arr.append(d)

    return arr


def set_greeting_text():
    post_message_url = "https://graph.facebook.com/v2.6/me/thread_settings?access_token=%s"%(PAGE_ACCESS_TOKEN)
    
    request_msg = {
        "setting_type":"greeting",
          "greeting":{
            "text":"Pokemon quiz bot"
          }
    }
    response_msg = json.dumps(request_msg)

    status = requests.post(post_message_url, 
                headers={"Content-Type": "application/json"},
                data=response_msg)

    logg(status.text,symbol='--GR--')


def index(request):
    #set_menu()
    #domain_whitelist()
    handle_postback('fbid','MENU_CALL')
    #post_facebook_message('1160786967320970','/ask hello')
    search_string = request.GET.get('text') or 'foo'
    output_text = save_message()
    return HttpResponse(output_text, content_type='application/json')


def set_menu():
    post_message_url = 'https://graph.facebook.com/v2.6/me/thread_settings?access_token=%s'%PAGE_ACCESS_TOKEN
    
    response_object =   {
                          "setting_type" : "call_to_actions",
                          "thread_state" : "existing_thread",
                          "call_to_actions":[
                            {
                              "type":"postback",
                              "title":"Help",
                              "payload":"MENU_HELP"
                            },
                            {
                              "type":"postback",
                              "title":"Course",
                              "payload":"MENU_COURSE"
                            },
                            {
                              "type":"postback",
                              "title":"Teachers",
                              "payload":"MENU_TEACHER"
                            },
                            {
                              "type":"postback",
                              "title":"Talk to a human",
                              "payload":"MENU_CALL"
                            },
                            {
                              "type":"postback",
                              "title":"Why CodingBlocks",
                              "payload":"MENU_WHY"
                            }
                          ]
                        }

    menu_object = json.dumps(response_object)
    status = requests.post(post_message_url,
          headers = {"Content-Type": "application/json"},
          data = menu_object)

    logg(status.text,'-MENU-OBJECT-')


def gen_response_object(fbid,item_type='course'):
    spreadsheet_object = scrape_spreadsheet()
    item_arr = [i for i in spreadsheet_object if i['itemtype'] == item_type]
    elements_arr = []

    for i in item_arr:
        sub_item = {
                        "title":i['itemname'],
                        "item_url":i['itemlink'],
                        "image_url":i['itempicture'],
                        "subtitle":i['itemdescription'],
                        "buttons":[
                          {
                            "type":"web_url",
                            "url":i['itemlink'],
                            "title":"Open"
                          },
                          {
                            "type":"element_share"
                          }              
                        ]
                      }
        elements_arr.append(sub_item)


    response_object = {
              "recipient":{
                "id":fbid
              },
              "message":{
                "attachment":{
                  "type":"template",
                  "payload":{
                    "template_type":"generic",
                    "elements":elements_arr
                  }
                }
              }
            }

    return json.dumps(response_object)


def gen_answer_object(fbid,keyword='index error'):
    api_url = 'http://soapi1.herokuapp.com/api/?q=%s'%(keyword)
    resp = requests.get(url=api_url)
    item_arr = json.loads(resp.text)

    elements_arr =[]
    for i in item_arr[:5]:
        sub_item = {
                        "title":"Question #%s"%(item_arr.index(i)),
                        "item_url": "http://stackoverflow.com/q/%s"%(i['id']),
                        "image_url":i['image'],
                        "subtitle":i['title'],
                        "buttons":[
                          {
                            "type":"web_url",
                            "url":i['answers'][0],
                            "title":"Answer 1"
                          },
                          {
                            "type":"web_url",
                            "url":i['answers'][1],
                            "title":"Answer 2"
                          },
                          {
                            "type":"element_share"
                          }              
                        ]
                      }
        elements_arr.append(sub_item)


    response_object = {
              "recipient":{
                "id":fbid
              },
              "message":{
                "attachment":{
                  "type":"template",
                  "payload":{
                    "template_type":"generic",
                    "elements":elements_arr
                  }
                }
              }
            }

    return json.dumps(response_object)



def post_facebook_message(fbid,message_text):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    message_text = message_text.lower()

    save_message(fbid,message_text)


    if message_text in 'teacher,why,course'.split(','):
        response_msg = gen_response_object(fbid,item_type=message_text)
    
    elif message_text.startswith('/ask'):
        query = message_text.replace('/ask','')
        response_msg = gen_answer_object(fbid,query)
    
    else:
        output_text = "Hi, how may I help you"
        response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":output_text}})
    
    requests.post(post_message_url, 
                    headers={"Content-Type": "application/json"},
                    data=response_msg)


def handle_postback(fbid,payload):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    output_text = 'Payload Recieved: ' + payload
    logg(payload,symbol='*')

    if payload == 'MENU_COURSE':
        return post_facebook_message(fbid,'course')
    elif payload == 'MENU_TEACHER':
        return post_facebook_message(fbid,'teacher')
    elif payload == 'MENU_WHY':
        response_object = {
                        "recipient":{
                          "id":fbid
                        },
                        "message":{
                          "attachment":{
                            "type":"template",
                            "payload":{
                              "template_type":"button",
                              "text":"What do you want to do next?",
                              "buttons":[
                                  {
                                                  "type":"web_url",
                                                  "url":"http://codingblocks.herokuapp.com/login?fb_id=%s"%(fbid),
                                                  "title":"Select Criteria",
                                                  "webview_height_ratio": "compact"
                                                }
                              ]
                            }
                          }
                        }
                      }
        response_msg = json.dumps(response_object)
        requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
        


    elif payload == "MENU_HELP":
        output_text = 'Welcome to CodingBlocks chatbot, you can se this chatbot to ...'
        response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":output_text}})
        status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    
    elif payload == 'MENU_CALL':

        response_object =   {
                              "recipient":{
                                "id":fbid
                              },
                              "message":{
                                "attachment":{
                                  "type":"template",
                                  "payload":{
                                    "template_type":"button",
                                    "text":"Need further assistance? Talk to one of our representative",
                                    "buttons":[
                                      {
                                                "type":"phone_number",
                                                "title":"Call Us",
                                                "payload":"+919599586446"
                                      }
                                    ]
                                  }
                                }
                              }
                            }
        response_msg = json.dumps(response_object)
        requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    

    #return

def logg(message,symbol='-'):
    print '%s\n %s \n%s'%(symbol*10,message,symbol*10)


def handle_quickreply(fbid,payload):
    if not payload:
        return
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    logg(payload,symbol='-QR-')
    if payload.split(':')[0] == payload.split(':')[-1]:
         logg("COrrect Answer",symbol='-YES-')
         output_text = 'Correct Answer'
         giphy_image_url = giphysearch(keyword='Yes,right,correct')
    else:
        logg("Wrong Answer",symbol='-NO-')
        output_text = 'Wrong answer'
        giphy_image_url =giphysearch(keyword='NO,wrong,bad')
    response_msg = json.dumps({"recipient":{"id":fbid}, 
        "message":{"text":output_text}})
    response_msg_image = {

            "recipient":{
                "id":fbid
              },
              "message":{
                "attachment":{
                  "type":"image",
                  "payload":{
                    "url": giphy_image_url
                  }
                }
              }

    } 
    response_msg_image = json.dumps(response_msg_image)
    status = requests.post(post_message_url, 
        headers={"Content-Type": "application/json"},
        data=response_msg)
    status = requests.post(post_message_url, 
        headers={"Content-Type": "application/json"},
        data=response_msg_image)
    return

class MyChatBotView(generic.View):
    def get (self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Oops invalid token')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        incoming_message= json.loads(self.request.body.decode('utf-8'))
        
        logg(incoming_message)

        for entry in incoming_message['entry']:
            for message in entry['messaging']:

                try:
                    if 'postback' in message:
                        handle_postback(message['sender']['id'],message['postback']['payload'])
                        return HttpResponse()
                    else:
                        pass
                except Exception as e:
                    logg(e,symbol='-315-')

                try:
                    if 'quick_reply' in message['message']:
                        handle_quickreply(message['sender']['id'],
                            message['message']['quick_reply']['payload'])
                        return HttpResponse()
                    else:
                        pass
                except Exception as e:
                    logg(e,symbol='-325-')
                
                try:
                    sender_id = message['sender']['id']
                    message_text = message['message']['text']
                    post_facebook_message(sender_id,message_text) 
                except Exception as e:
                    logg(e,symbol='-332-')

        return HttpResponse() 