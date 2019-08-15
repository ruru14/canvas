import os
import datetime

curdate = datetime.datetime.now().strftime('%Y_%m_%d')
curtime = datetime.datetime.now().strftime('%H:%M:%S')

dirname = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
filename = os.path.join(dirname, 'log', curdate)


def logging(e, text):
    os.makedirs(os.path.join(dirname,'log'), exist_ok=True)
    f = open(filename, mode='at', encoding='utf-8')
    f.write(curtime + " " + text + '\n')
    f.write(str(e) + '\n\n')

    f.close()
