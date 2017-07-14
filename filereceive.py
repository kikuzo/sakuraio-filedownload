"""This is a file download program via sakura.io."""
# -*- coding: utf-8 -*-
import sys
import time
import os
from datetime import datetime
from sakuraio.hardware.rpi import SakuraIOGPIO
#from sakuraio.hardware.rpi import SakuraIOSMBus
import led_flash

FILEID_PATH = 1
FILEID_CONTENT = 2

def get_file_via_sakuraio(channel):
    """ Single file downlod function. """
    CHUNK_SIZE = [16]
    DELAY = 1
    DOWNLOAD_DELAY_INTERVAL = 0.5
    filesize = 0
    receivedsize = 0
    filedata = []

    # インスタンス作成
    sakuraio = SakuraIOGPIO()
    #sakuraio = SakuraIOSMBus

    # 一連のファイルダウンロード処理を開始(センター側でダウンロードファイルを取得)
    sakuraio.start_file_download([channel])

    time.sleep(DELAY)

    # メタデータ(ファイルサイズ等)を取得
    try:
        response = sakuraio.get_file_metadata()
    except:
        #sakuraio.cancel_file_download()
        #del sakuraio
        #sys.exit()
        raise
    else:
        print('Get_file_metadata: Status: {0:x}'.format(response["status"]))
        if response["status"] == 0x81 or response["status"] == 0x82:
            del sakuraio
            return filedata

        filesize = response["size"]
        print('Get_file_metadata: Filesize: {0}'.format(filesize))
        print('Get_file_metadata: Timestamp: {0}'.format(datetime.utcfromtimestamp(response["timestamp"]/1000)))
    
    # ファイルの実体を取得
    while receivedsize < filesize:
        time.sleep(DOWNLOAD_DELAY_INTERVAL)
        try:
            result = sakuraio.get_file_data(CHUNK_SIZE)
        except:
            #sakuraio.cancel_file_download()
            #del sakuraio
            #sys.exit()
            raise
        else:
            filedata.extend(result["data"])
            receivedsize += len(result["data"])
            #print('Get_file_data: Length: {0}'.format(len(result["data"])))
            #print('Get_file_data: Receivedsize: {0}'.format(receivedsize))
            print('.', end='', flush=True)
        '''
        try:
            response = sakuraio.get_file_download_status()
        except:
            print('Get_file_download_status: Error.')
            raise
        else:
            print('Get_file_download_status: Status: {0:x}'.format(response["status"]))
            print('Get_file_download_status: Receivedsize: {0}'.format(response["size"]))
        '''
    print('')

    #print('Get_file_data: Received_data: {0}'.format(filedata))

    del sakuraio

    return filedata

if __name__ == "__main__":

    # まずファイルID1で、パス名を取得
    response = []
    response = get_file_via_sakuraio(FILEID_PATH)
    if response == []:
        # ファイルパスが取得できなかった場合は何もしないで終了
        print('ERROR: No file configured.')
        sys.exit()
    filepath = ""
    filepath = bytes(response).decode('utf-8').strip()
    print('FilePath: {0}'.format(filepath))

    # 次にファイルID2でファイルの中身を取得
    content = []
    content = get_file_via_sakuraio(FILEID_CONTENT)
    if content == []:
        # 中身の取得ができなかったらやはり何もしないで終了
        print('ERROR: No file configured.')
        sys.exit()

    # 内容が更新されているかチェックする
    try:
        with open(filepath, "r") as fin:
            original_file = []
            original_file = fin.read()
            if original_file == bytes(content).decode('utf-8') :
                print('{0} is not updated.'.format(filepath))
                sys.exit()
    except IOError:
        # 元ファイルばない場合　→　そのままファイル書き込み
        pass

    print('{0} is updated.'.format(filepath))

    # 取得したファイルの中身を、パス名で書き込み
    with open(filepath, "wb") as fout:
        fout.write(bytearray(content))

    # パーミッション変更
    os.system("sudo chmod go-rwx " + filepath)
    
    # LEDを点滅させてファイルを書き換えたことを表明
    led_flash.led_flash()

    # 端末をリブート
    os.system("sudo shutdown -r now")
