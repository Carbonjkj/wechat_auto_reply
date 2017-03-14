#! python2
# coding: utf-8
import itchat as wc
import copy
import time
import threading
import logging
# 获取信息的线程
class get_text_msg(threading.Thread):
    # 初始化 收到的信息，收到小冰的信息，小冰的用户名
    def __init__(self, msg_in, msg_out, xiaobing_name):
        threading.Thread.__init__(self)
        self.mi = msg_in
        self.mo = msg_out
        self.xb = xiaobing_name

    def run(self):
        autoreply = False
        while True:
            try:
                # 获取信息
                msgs = wc.get_msg()
                if msgs:
                    # 按次序提取信息
                    for msg in msgs[0]:
                        time.sleep(0.2)
                        try:
                            # 找到自己的发言，‘开始你的表演’，‘停止你的表演’ 作为开始和结束的指令
                            if msg['MsgType'] == 1:
                                if msg['FromUserName'] == wc.originInstance.storageClass.userName:
                                    if '开始你的表演' in msg['Content']:
                                        autoreply = True
                                        logging.info('表演开始咯')
                                        wc.send_msg('表演开始', self.xb)
                                    if '停止你的表演' in msg['Content']:
                                        autoreply = False
                                        logging.info('表演谢幕了')
                                        wc.send_msg('表演谢幕', self.xb)
                                elif '@@' not in msg['FromUserName'] and '@' in msg['FromUserName'] :
                                    # 获取不是小冰的信息
                                    if autoreply:
                                        if msg['FromUserName'] != self.xb:
                                            # 添加到接收列表
                                            self.mi.append(copy.deepcopy(msg))
                                        # 小冰的信息
                                        else:
                                            # 添加到回复列表
                                            self.mo.append(copy.deepcopy(msg))
                        except IndexError:
                            pass
            except:
                logging.warning('Getting module face a problem')
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
                    user = wc.search_friends(userName=msg['FromUserName'])
                    logging.info('[%s] %s - %s' % (
                        time.ctime(time.time()), msg['Content'], user['NickName']))
                    wc.send_msg(msg['Content'], self.xb)
                    del self.mo[:]
                    timeout = time.time()
                    replied = False
                    while len(self.mo) == 0:
                        time.sleep(1)
                        if time.time() - timeout > 10:
                            wc.send_msg('一声叹息，我没get到你的point啊~', msg['FromUserName'])
                            replied = True
                            break
                    if replied == False:
                        last_reply = copy.deepcopy(self.mo[-1])
                        wc.send_msg('%s' % last_reply['Content'], msg['FromUserName'])
                        logging.info('[%s] %s - 小冰' % (
                            time.ctime(time.time()), last_reply['Content']))
                else:
                    time.sleep(0.2)
            except:
                time.sleep(0.2)
                logging.warning('reply module face a problem')
                pass


def find_xiaobing():
    time_out = time.time()
    xiaobing_name = ''
    while True:
        try:
            xiaobing_name = wc.search_mps(name='小冰')[0]['UserName']
            logging.info('小冰找到啦！')
            break
        except:
            if time.time() - time_out > 15:
                logging.info('小冰不见啦！请关注小冰公众号，20秒后重试')
                time.sleep(20)
            pass
    return xiaobing_name

if __name__ == '__main__':
    MSGIN = []
    MSGOUT = []
    logging.basicConfig(filename='autoreply.log', level=logging.INFO)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    wc.auto_login(enableCmdQR=2)
    XB = find_xiaobing()
    logging.info('开始自动回复，请在随意对话框输入，开始你的表演')
    logging.info('结束自动回复，请在随意对话框输入，结束你的表演')
    t1 = get_text_msg(MSGIN, MSGOUT, XB)
    t1.start()

    t3 = reply_msg(MSGIN, MSGOUT, XB)
    t3.start()
    wc.start_receiving()
