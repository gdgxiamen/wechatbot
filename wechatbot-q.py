#!/usr/bin/env python
# coding: utf-8
# 厦门GDG小助手微信机器人，功能：
# 1.自动接受好友，并根据消息自动将朋友加群
# 2.为避免超过消息限额，采用了队列，并随机延迟消息处理的机制
# @Author Lingxiang Zheng, email:lxzheng@gmail.com

from wxpy import *
import os
import time
import random

import threading
import Queue

try:
    bot = Bot(os.getcwd() + '/bot.pkl', qr_path=os.getcwd() + '/qr.png')
except IOError: 
    print "Sorry,the file cannot be accessed."    

mps=bot.mps()
i=0;

msg_q=Queue.Queue()

#使用前先调试，确保能找到这个群
group =  bot.groups().search(u'GDG_厦门')[0]

google_mps = bot.mps().search(u'谷歌')


class Process_thread(threading.Thread):
    def run(self):
	while True:
	    msg=msg_q.get()
            print(msg)
            if msg.type==FRIENDS:
                # 接受好友请求
	        time.sleep(random.randint(1,60))
                new_friend = msg.card.accept()
                # 向新的好友发送消息
                new_friend.send('哈哈，我接受了你的好友请求,我是厦门GDG小助手机器人，回复"I love GDG"可以帮你加入厦门GDG群')
	    elif valid_msg(msg):
                invite(msg)
	    elif (msg.member is None) and (msg.chat not in mps):
	        time.sleep(random.randint(5,30))
                msg.chat.send('Hello {} ，回复"I love GDG"可以帮你加入厦门GDG群'.format(msg.chat.name))
            elif msg.chat in google_mps:
	        group.send('{}\n{}'.format(msg.raw['Text'],msg.raw['Url']))
	    if msg.chat is not None:
	    	msg.chat.mark_as_read()


def valid_msg(msg):
    if msg.text is None:
	return False
    print(msg.text.lower())
    if "i love gdg" in msg.text.lower():
	return True
    else:
	return False

def invite(msg):
    #群用户或是朋友
    if (msg.member==None):
	user=msg.chat
    else:
	user=None
    #用户为空或是公众号则不处理
    if (user is None) or (user in mps):
	print("No user")
	return False

    time.sleep(random.randint(5,30))
    try:
        if user in group:
	    user.send('hi, 你已在{}中!'.format(group.name))
        elif len(group) < 40:
	    group.add_members(user, use_invitation=False)
            group.send('欢迎@{} 加入厦门GDG!'.format(user.name))
        else:
	    group.add_members(user, use_invitation=True)
    except ResponseError as e:
            print(e.err_code, e.err_msg)
            #如果超限，随机休眠10-17分钟,共重试5次
            if e.err_code==1205:
                time.sleep(random.randint(600,1000))
		if i<5:  
		    i=i+1  
		    invite(msg)
                else:
	            return False    
    #正常退出，计数器重置为0
    i=0
    return True

@bot.register()
def new_msg(msg):
    if msg is not None:
	msg_q.put(msg)

msg_process=Process_thread()
msg_process.start()



embed()



