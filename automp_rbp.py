#! python2
# coding: utf-8
import itchat as wc
import logging
import copy
import time
import threading

# 获取信息的线程
class get_text_msg(threading.Thread):
    # 初始化 收到的信息，收到小冰的信息，小冰的用户名
    def __init__(self, msg_in, msg_out, xiaobing_name):
        threading.Thread.__init__(self)
        self.mi = msg_in
        self.mo = msg_out
        self.xb = xiaobing_name

    def run(self):
        while True:
            try:
                # 获取信息
                msgs = wc.get_msg()
                if msgs:
                    # 按次序提取信息
                    for msg in msgs[0]:
                        time.sleep(0.2)
                        try:
                            # 检测信息的发件人， 这里过滤掉自己和群信息，只接受文本信息
                            if msg['MsgType'] == 1 \
                                    and msg['FromUserName'] != wc.originInstance.storageClass.userName \
                                    and '@@' not in msg['FromUserName'] \
                                    and '@' in msg['FromUserName']:
                                # 获取不是小冰的信息
                                if msg['FromUserName'] != self.xb:
                                    # print('%s: %s: %s - %s' % (
                                    # time.ctime(time.time()), msg['MsgId'], msg['Content'], msg['FromUserName']))
                                    # 添加到列表
                                    self.mi.append(copy.deepcopy(msg))
                                # 小冰的信息
                                else:
                                    # print('%s: %s: %s - %s' % (
                                    # time.ctime(time.time()), msg['MsgId'], msg['Content'], msg['FromUserName']))
                                    # 添加到回复列表
                                    self.mo.append(copy.deepcopy(msg))
                        except IndexError:
                            pass
            except:
                logging.WARNING('Getting module face a problem')
                pass


class reply_msg(threading.Thread):

    def __init__(self, msg_in, msg_out, xiaobing_name):
        threading.Thread.__init__(self)
        self.mi = msg_in
        self.mo = msg_out
        self.xb = xiaobing_name

    def run(self):
        while True:
            try:

                if len(self.mi) != 0:
                    msg = copy.deepcopy(self.mi[0])
                    self.mi.pop(0)
                    logging.INFO('%s: %s: %s - %s' % (
                        time.ctime(time.time()), msg['MsgId'], msg['Content'], msg['FromUserName']))
                    wc.send_msg(msg['Content'], self.xb)
                    del self.mo[:]
                    timeout = time.time()
                    replied = False
                    while len(self.mo) == 0:
                        time.sleep(1)
                        if time.time() - timeout > 10:
                            wc.send_msg('(自动)一声叹息，我没get到你的point啊~', msg['FromUserName'])
                            replied = True
                            break
                    if replied == False:
                        last_reply = copy.deepcopy(self.mo[-1])
                        wc.send_msg('(自动)%s' % last_reply['Content'], msg['FromUserName'])
                        logging.INFO('%s: %s: %s - %s' % (
                            time.ctime(time.time()), last_reply['MsgId'], last_reply['Content'], last_reply['FromUserName']))
                else:
                    time.sleep(0.2)
            except:
                time.sleep(0.2)
                logging.WARNING('reply module face a problem')
                pass


def find_xiaobing():
    time_out = time.time()
    xiaobing_name = ''
    while True:
        try:
            logging.DEBUG(wc.search_mps(name='小冰'))
            xiaobing_name = wc.search_mps(name='小冰')[0]['UserName']
            logging.INFO('小冰找到啦！')
            break
        except:
            if time.time() - time_out > 15:
                logging.WARNING('小冰不见啦！20秒后重试')
                time.sleep(20)
            pass
    return xiaobing_name

if __name__ == '__main__':
    MSGIN = []
    MSGOUT = []
    wc.auto_login(enableCmdQR=2)
    XB = find_xiaobing()
    t1 = get_text_msg(MSGIN, MSGOUT, XB)
    t1.start()
    t3 = reply_msg(MSGIN, MSGOUT, XB)
    t3.start()
    wc.start_receiving()