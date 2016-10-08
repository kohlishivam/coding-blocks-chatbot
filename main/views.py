#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse

from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import requests
import re
import random
import pprint
# Create your views here.


VERIFY_TOKEN = '7thseptember2016'
PAGE_ACCESS_TOKEN = 'EAAYO3MZBoz10BAN7mWot28ysn3YyJhnNPSIwJiFCzwi5k39M0FnEKkEZCkjZA5rYCnmSI0ikiQVKxycLKc5dc415D4vOPBaA4Y2WpfiOTPd0UNHiDjwivZCZCc404Xrrtam6NQq4OKpFZBE9hMeidP3CZAUHQqcLY7gn4ng9OdTOQZDZD'


def scrape_spreadsheet():
    sheet_id = '1_4NKNJ5_f82RYqwYmv3FqX8w-_6TuGHgDHrA5dTVGUg'
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
    post_facebook_message('asd','asdasd')
    search_string = request.GET.get('text') or 'foo'
    output_text = gen_response_object('fbid',item_type='teacher')
    return HttpResponse(output_text, content_type='application/json')


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

def post_facebook_message(fbid,message_text):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    message_text = message_text.lower()

    output_text = message_text

    if message_text in 'teachers,teacher,professors,professor'.split(','):
        item_type = 'teacher'
    
    elif message_text in 'why,features,points'.split(','):
        item_type = 'why'

    elif message_text in 'course,courses,lectures,batch,next batch'.split(','):
        item_type = 'course'


    response_msg = gen_response_object(fbid,item_type='teacher')

    #response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":output_text}})
    requests.post(post_message_url, 
                    headers={"Content-Type": "application/json"},
                    data=response_msg)


def handle_postback(fbid,payload):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    output_text = 'Payload Recieved: ' + payload
    logg(payload,symbol='*')

    if payload == 'RANDOM_JOKE':
        post_facebook_message(fbid,'foo')

    #response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":output_text}})
    #status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    return

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