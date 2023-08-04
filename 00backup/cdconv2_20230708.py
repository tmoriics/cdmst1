#!/usr/bin/env python
# -*- coding: utf-8 -*-

#######
#######
# cdconv2.py @tmoriics
#######
#######
# 2022-07-15T06:00
# 2022-07-27T12:30
# 2022-07-28T06:30
# 2022-07-29T21:00
# 2022-07-30T21:00
# 2022-08-01T12:30
# 2022-08-01T20:00
# 2022-08-02T22:00
# 2022-08-03T00:08
# 2022-08-03T17:40
# 2022-08-03T23:30
# 2022-08-05T20:56 templateId 8851
# 2022-08-06T17:30
# 2022-08-06T21:10
# 2022-08-07T21:30
# 2022-08-08T09:30 ソースコードの見た目の整頓のみ
# 2022-08-09T18:40 指標計算変更
# 2022-08-09T21:40 drop変更
# 2022-08-17T16:59 templateId both 8851 and narrower 9037 now 9037
#


###
# Imports
###
import os
import logging
import sys
import traceback
import argparse
import locale
import time
import math
import string
import datetime
import io
import uuid
import json
import base64
import tempfile
from pathlib import Path
# from urllib.request import Request, urlopen
import requests
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from PIL import Image, ImageDraw, ImageFilter
# from pdf2image import convert_from_path


#####
#####
# Locale, timezone and others
#####
#####

###
# Locale
###
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')  # for mac


###
# Timezone instance
###
tz_jst = datetime.timezone(datetime.timedelta(hours=9))


#####
#####
# Special Functions
#####
#####

###
# Calculate datetime from the special format date and time
###
#
# Wakeup and bed set
def calculate_datetime_from_date_and_time_strings(date_dt, hour_s, minute_s, pm_adjust_b):
    global tz_jst

#   time_tmp = datetime.time(hour=int(hour_s), minute=int(minute_s)) # without timezone
    time_tmp = datetime.time(
        hour=int(hour_s), minute=int(minute_s), tzinfo=tz_jst)
    # for check
    # mylogger.debug(time_tmp, time_tmp, time_tmp.tzinfo))
    if pm_adjust_b:
        ret = datetime.datetime.combine(
            date_dt, time_tmp) + datetime.timedelta(hours=12)
    else:
        ret = datetime.datetime.combine(date_dt, time_tmp)
    return ret


###
# Global
###
# df_today = df_today.rename({"Hokkaido":"北海道", "Aomori":"青森","Akita":"秋田",
#                            "Iwate":"岩手", "Miyagi":"宮城","Yamagata":"山形", "Fukushima":"福島",
#       "Ibaraki":"茨城", "Tochigi":"栃木", "Gunma":"群馬", "Saitama":"埼玉",
#       "Chiba":"千葉", "Tokyo":"東京", "Kanagawa":"神奈川",
#       "Niigata":"新潟", "Toyama":"富山", "Ishikawa":"石川",
#       "Fukui":"福井", "Yamanashi":"山梨", "Nagano":"長野",
#       "Gifu":"岐阜","Shizuoka":"静岡", "Aichi":"愛知", "Mie":"三重",
#       "Shiga":"滋賀", "Kyoto":"京都", "Osaka":"大阪","Hyogo":"兵庫",
#       "Nara":"奈良", "Wakayama":"和歌山",
#       "Tottori":"鳥取","Shimane":"島根", "Okayama":"岡山",
#       "Hiroshima":"広島", "Yamaguchi":"山口",
#       "Kagawa":"香川", "Tokushima":"徳島","Ehime":"愛媛", "Kochi":"高知",
#       "Fukuoka":"福岡", "Saga":"佐賀", "Nagasaki":"長崎",
#       "Kumamoto":"熊本", "Oita":"大分", "Miyazaki":"宮崎",
#       "Kagoshima":"鹿児島", "Okinawa":"沖縄"})
dic_corners = []
diary_image_filename = ""
diary_id = 0
diary_year_string = "2020"
diary_month_string = "1"
diary_day_string = "1"
diary_first_date = datetime.date(year=int(diary_year_string),
                                 month=int(diary_month_string),
                                 day=int(diary_day_string))
diary_date = datetime.date(year=int(diary_year_string),
                           month=int(diary_month_string),
                           day=(int(diary_day_string))) + datetime.timedelta(days=0)
diary_first_date = datetime.date(year=int(diary_year_string),
                                 month=int(diary_month_string),
                                 day=(int(diary_day_string))) + datetime.timedelta(days=0)
diary_page_string = "1"
diary_page = 1


#####
#####
# Usual Functions
#####
#####

###
# Log
###
def set_logger(name=None):
    # DEBUGログをファイル出力
    file_handler = logging.FileHandler('DEBUG.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.addFilter(lambda record: record.levelno <= logging.DEBUG)

    # INFOログを標準ー出力
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.addFilter(lambda record: record.levelno == logging.INFO)

    # WARNING以上のログを標準エラー出力
    stderr_handler = logging.StreamHandler(stream=sys.stderr)
    stderr_handler.setLevel(logging.WARNING)

    # ハンドラ設定
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)


###
# Get args
###
def get_args():
    parser = argparse.ArgumentParser(
        description='add the filename of the diary image')
    parser.add_argument("diary_image_filename",
                        help="Set the image filename", type=str)
    parser.add_argument("-id", help="Set the ID", type=int,
                        default=argparse.SUPPRESS)
    parser.add_argument("-day", help="Set the month and day as 0704 for July 4th",
                        type=int, default=argparse.SUPPRESS)
    args = parser.parse_args()
    return(args)


###
# Secret get ocr json from a jpeg file
###
def get_ocr_json_from_jpg_file(jpgfile, diaryid, diarydate, diarypage, diaryfirstdate):
    api_url = os.environ.get('CLOVA_API_URL')
    secret_key = os.environ.get('CLOVA_SECRET_KEY')
    name_str = "jpg_diary_"+str(diaryid)+"_" + \
        diarydate.strftime('%m%d')+'_p'+str(diarypage)
    requestId_str = str(uuid.uuid4())
    timestamp_int = int(round(time.time() * 1000))
    request_json = {
        "images": [
            {
                "format": "jpg",
                "templateIds": [9037],
                "name": name_str
            }
        ],
        "version": "V2",
        "requestId": requestId_str,
        "timestamp": timestamp_int,
        "lang": "ja"
    }
    # request_json = {
    #    "images": [
    #        {
    #            "format": "jpg",
    #            "name": "jpg_diary_"+str(diaryid)+"_"+diarydate.strftime('%Y%m%d'),
    #            "templateIds": JSON_ARRAY"
    #        }
    #    ],
    #    "version": "V2",
    #    "requestId": str(uuid.uuid4()),
    #    "timestamp": int(round(time.time() * 1000)),
    #    "lang":"ja"
    # }

    headers = {
        "X-OCR-SECRET": secret_key
    }
    payload = {"message": json.dumps(request_json).encode('UTF-8')}
    files = [
        ("file", open(jpgfile, 'rb'))
    ]
    response = requests.request(
        'POST', api_url, headers=headers, data=payload, files=files)
    if response.status_code == requests.codes.ok:
        mylogger.info(response.url)
        mylogger.info(response.status_code)
        mylogger.info(response.headers)
        mylogger.info(response.headers.get('content-type'))
        mylogger.info(response.encoding)
        # mylogger.info(response.text)
        # mylogger.info(response.text.encode('utf8'))
        # mylogger.info(type(response.content))
        # mylogger.info(response.content.decode(response.encoding))

        # response_json_fn = "res_"+str(diaryid)+"_"+diarydate.strftime('%Y%m%d')+'.json'
        response_json_fn = "res_" + \
            str(diaryid)+"_"+diaryfirstdate.strftime('%m%d') + \
            '_p'+str(diarypage)+'.json'
        with open("../output/"+response_json_fn, 'w') as f:
            json.dump(response.json(), f, indent=4, ensure_ascii=False)
            # response_json = convert_df_to_json(response.json())
            # with open("../output/"+response_json_fn, "w") as f:
            #   f.write(response_json)
    else:
        mylogger.info(response.status_code)
        res_code_str = str(response.json["code"])
        mylogger.info('ErrorCode: res_code_str'+str(res_code_str))
        res_message_str = str(response.json["message"])
        res_path_str = str(response.json["path"])
        res_timestamp_str = str(response.json["timestamp"])

    return response.json()


###
# Get ocr dataframe from a jpg file through json
###
def get_ocr_dataframe_from_jpg_file(jpgfile, diaryid, diarydate, diarypage, diaryfirstdate):
    global dic_corners

    res_json = get_ocr_json_from_jpg_file(
        jpgfile, diaryid, diarydate, diarypage, diaryfirstdate)

    # df_res = json.loads(res_json)
    # df_res = pd.read_json(res_json, orient='columns')
    df_res = res_json

    res_version_str = str(df_res['version'])
    res_requestId_str = str(df_res['requestId'])
    res_timestamp_str = str(df_res['timestamp'])
    res_uid_str = str(df_res['images'][0]['uid'])
    res_name_str = str(df_res['images'][0]['name'])
    res_inferResult_str = str(df_res['images'][0]['inferResult'])
    res_message_str = str(df_res['images'][0]['message'])
    res_matchedTemplate_id_int = int(
        df_res['images'][0]['matchedTemplate']['id'])
    res_matchedTemplate_name_str = str(
        df_res['images'][0]['matchedTemplate']['name'])
    res_validationResult_result_str = str(
        df_res['images'][0]['validationResult']['result'])
    res_title_name_str = str(df_res['images'][0]['title']['name'])
    res_title_inferText_str = str(df_res['images'][0]['title']['inferText'])
    res_title_inferConfidence_float = float(
        df_res['images'][0]['title']['inferConfidence'])

    dic_names = []
    dic_valueTypes = []
    dic_polys = []
    dic_inferTexts = []
    dic_inferConfidences = []
    dic_types = []
    for i, val in enumerate(df_res['images'][0]['fields']):
        dic_names.append(val['name'])
        dic_valueTypes.append(val['valueType'])
        dic_polys.append(val['boundingPoly'])
        dic_inferTexts.append(val['inferText'])
        dic_inferConfidences.append(val['inferConfidence'])
        dic_types.append(val['type'])
        for j, v in enumerate(val['boundingPoly']['vertices']):
            # mylogger.info('i'+str(i)+','+'j'+str(j)+': ('+str(v['x'])+','+str(v['y'])+')')
            dic_corners.append((v['x'], v['y']))
        # for j, v in enumerate(val['boundingPoly']['vertices']):
        #    mylogger.info('i'+str(i), 'j'+str(j), v['x'], v['y'])

    for i, itext in enumerate(dic_inferTexts):
        dic_inferTexts[i] = format_text(itext)

    ocr_infertext_df = pd.DataFrame(np.arange(13*14+2), columns=['inferText'])
    for i in range(0, 2+14*13):
        ocr_infertext_df['inferText'][i] = dic_inferTexts[i]

    month = ocr_infertext_df['inferText'][0]
    mylogger.info('from OCR: month='+str(month))
    day = ocr_infertext_df['inferText'][1]
    mylogger.info('from OCR: day=' + str(day))

    # ocr_text_df = pd.DataFrame(np.arange(13*14).reshape(13, 14),
    #                            columns = ['時', '分', '排尿量', 'もれ', '尿意', '切迫感', '残尿感', 'メモ'])
    ocr_text_df = pd.DataFrame(np.arange(13*14).reshape(13, 14),
                               columns=['時', '分', '排尿量', 'もれ無し', 'もれ少量', 'もれ中量', 'もれ多量', '尿意有り', '尿意無し', '切迫感有り', '切迫感無し', '残尿感有り', '残尿感無し', 'メモ'])

    for ii in range(0, 13):
        ocr_text_df.loc[ocr_text_df.index[ii],
                        '時'] = ocr_infertext_df['inferText'][2+ii*14]
        ocr_text_df.loc[ocr_text_df.index[ii],
                        '分'] = ocr_infertext_df['inferText'][3+ii*14]
        ocr_text_df.loc[ocr_text_df.index[ii],
                        '排尿量'] = ocr_infertext_df['inferText'][4+ii*14]
        ocr_text_df.loc[ocr_text_df.index[ii],
                        'もれ無し'] = ocr_infertext_df['inferText'][5+ii*14]
        ocr_text_df.loc[ocr_text_df.index[ii],
                        'もれ少量'] = ocr_infertext_df['inferText'][6+ii*14]
        ocr_text_df.loc[ocr_text_df.index[ii],
                        'もれ中量'] = ocr_infertext_df['inferText'][7+ii*14]
        ocr_text_df.loc[ocr_text_df.index[ii],
                        'もれ多量'] = ocr_infertext_df['inferText'][8+ii*14]
        ocr_text_df.loc[ocr_text_df.index[ii],
                        '尿意有り'] = ocr_infertext_df['inferText'][9+ii*14]
        ocr_text_df.loc[ocr_text_df.index[ii],
                        '尿意無し'] = ocr_infertext_df['inferText'][10+ii*14]
        ocr_text_df.loc[ocr_text_df.index[ii],
                        '切迫感有り'] = ocr_infertext_df['inferText'][11+ii*14]
        ocr_text_df.loc[ocr_text_df.index[ii],
                        '切迫感無し'] = ocr_infertext_df['inferText'][12+ii*14]
        ocr_text_df.loc[ocr_text_df.index[ii],
                        '残尿感有り'] = ocr_infertext_df['inferText'][13+ii*14]
        ocr_text_df.loc[ocr_text_df.index[ii],
                        '残尿感無し'] = ocr_infertext_df['inferText'][14+ii*14]
        # メモ特別扱いのため
        ocr_text_df.loc[ocr_text_df.index[ii],
                        'メモ欄'] = ocr_infertext_df['inferText'][15+ii*14]

    # ocr_text_df_pn = "../output/"+"ocr_text_df" + str(diaryid)+"_"+diaryfirstdate.strftime('%m%d')+'_p'+str(diarypage)+'.csv'
    # ocr_text_df.to_csv(ocr_text_df_pn, encoding='utf-8')

    ret_df = ocr_text_df
    return(ret_df)


###
# Convert a DataFrame to JSON
###
# @st.experimental_memo
def convert_df_to_json(df):
    df_to_json = df.to_json(orient='columns', force_ascii=False)
    return df_to_json


###
# Convert a DataFrame to CSV with utf-8-sig
###
# @st.experimental_memo
def convert_df_to_csv(df):
    df_to_cfv = df.to_csv().encode('utf-8-sig')
    return df_to_cfv


###
# Formate text for punctuation etc.
###
def format_text(intext):
    table = str.maketrans('', '', string.punctuation + '¥')
    intext = intext.translate(table)
    intext.strip()
    text1 = intext.replace('\n', '_')
    text2 = text1.replace('€', '')
    ret_text = text2.replace(' ', '')
    return ret_text


#####
#####
# Main script
#####
#####
def main(args):
    global dic_corners
    global diary_image_filename, diary_id
    global diary_year_string, diary_month_string, diary_day_string
    global diary_date
    global diary_first_date
    global diary_page_string
    global diary_page

    try:
        ###
        # Title
        ###
        mylogger.info('========  ========  ========  ========  ======== |')
        mylogger.info('排尿日誌コンバータ（産褥期）')
        mylogger.info('Copyright (c) 2022 tmoriics (2022-08-09T18:40)')

        ###
        # Setting
        ###
        graph_background_color = "#EEFFEE"

        ###
        # Diary ID, date and page
        ###
        mylogger.info('日誌対象者IDは'+str(diary_id)+'です。')
        mylogger.info('日誌対象日初日は'+diary_first_date.strftime('%Y年%m月%d日'+'です。'))
        mylogger.info('日誌ページは'+str(diary_page)+'です。')
        mylogger.info('なお日誌対象日は'+diary_date.strftime('%Y年%m月%d日'+'です。'))

        ###
        # Wakeup and bed set
        ###
        #
        # Wakeup and bedtime default set
        wakeup_hour_string = '6'
        wakeup_minute_string = '00'
        wakeup_pm_adjust_boolean = False
        wakeup_datetime = calculate_datetime_from_date_and_time_strings(diary_date,
                                                                        wakeup_hour_string,
                                                                        wakeup_minute_string,
                                                                        wakeup_pm_adjust_boolean)
        bed_hour_string = '9'
        bed_minute_string = '00'
        bed_pm_adjust_boolean = True
        bed_datetime = calculate_datetime_from_date_and_time_strings(diary_date,
                                                                     bed_hour_string,
                                                                     bed_minute_string,
                                                                     bed_pm_adjust_boolean)
        next_wakeup_hour_string = '5'
        next_wakeup_minute_string = '55'
        next_wakeup_pm_adjust_boolean = False
        next_wakeup_datetime = calculate_datetime_from_date_and_time_strings(diary_date + datetime.timedelta(days=1),
                                                                             next_wakeup_hour_string,
                                                                             next_wakeup_minute_string,
                                                                             next_wakeup_pm_adjust_boolean)
        next_bed_hour_string = '9'
        next_bed_minute_string = '05'
        next_bed_pm_adjust_boolean = True
        next_bed_datetime = calculate_datetime_from_date_and_time_strings(diary_date + datetime.timedelta(days=1),
                                                                          next_bed_hour_string,
                                                                          next_bed_minute_string,
                                                                          next_bed_pm_adjust_boolean)
        #
        # Wakeup time display
        # mylogger.info('### 起床時刻：')
        # mylogger.info('対象日の起床時刻は' + wakeup_datetime.strftime("%Y-%m-%dT%H:%M") + 'です。')

        ###
        # Diary read
        ###
        #
        # Diary image(s)
        # mylogger.info("日誌画像読み込み")
        ##########
        with open("../input/"+diary_image_filename, "rb") as input_jpg_file:
            with tempfile.NamedTemporaryFile(delete=False) as jpg_tmp_file:
                fp = Path(jpg_tmp_file.name)
                # fp.write_bytes(input_jpg_file.getvalue()) xxxxx
                fp.write_bytes(input_jpg_file.read())
                input_jpg_file.seek(0)
                bytes_data = input_jpg_file.read()
                dimg = Image.open(io.BytesIO(bytes_data))
                # dimg.show()
                fig = plt.figure(figsize=(7, 10))
                fig.patch.set_facecolor('white')
                fig.patch.set_edgecolor('black')
                ax = fig.add_subplot(1, 1, 1)
                ax.set_xlabel("X")
                ax.set_ylabel("Y")
                ax.set_xlim(0, 210)
                ax.set_ylim(0, 297)
                ax.grid()
                ax.set_title(diary_image_filename)
                timg = Image.open(jpg_tmp_file.name)
                tdraw = ImageDraw.Draw(timg)
                xlim = ax.get_xlim()
                ylim = ax.get_ylim()
                timg_array = np.asarray(timg)
                # # mylogger.info(timg_array)
                # # mylogger.info(timg_array.shape)
                # # ax.imshow(timg, extent=[*xlim, *ylim], aspect='auto', alpha=0.9)
                ax.imshow(timg_array, extent=[
                          *xlim, *ylim], aspect='auto', alpha=0.9)
                buf = io.BytesIO()
                fig.savefig(buf, format="png", dpi=300)
                # # plt.show()
                plt.close(fig)
                buf.seek(0)
                timgs = Image.open(buf).convert('RGB')
                # timgs_pn = "../output/"+str(diary_id)+"_"+diary_date.strftime('%m%d')+'_p'+diary_page_string+'.png'
                timgs_pn = "../output/" + \
                    str(diary_id)+"_"+diary_first_date.strftime('%m%d') + \
                    '_p'+diary_page_string+'.png'
                # timgs.save(timgs_pn)
                # timgs.show()

        ###
        # Diary recognition
        ###
        #
        # Diary image recognition by OCR
        #
        # Dummy OCR READ FROM DIARY_FIRST_DATE string
        # ocr_data_df = pd.read_csv('../input/'+str(diary_id)+"_"+diary_date.strftime('%m%d')+'_p'+diary_page_string+'.csv', encoding='shift-jis')
        # ocr_data_df = pd.read_excel('../input/'+str(diary_id)+"_"+diary_first_date.strftime('%m%d')+'_p'+diary_page_string+'.xlsx', index_col=None)
        # Actual OCR
        # ocr_data_df = get_ocr_dataframe_from_jpg_file(jpg_tmp_file.name, diary_id, diary_date, diary_page)
        ocr_data_df = get_ocr_dataframe_from_jpg_file(
            jpg_tmp_file.name, diary_id, diary_date, diary_page, diary_first_date)

        ###
        # OCR image with squares based on corners
        ###
        fig_ocr = plt.figure(figsize=(7, 10))
        fig_ocr.patch.set_facecolor('white')
        fig_ocr.patch.set_edgecolor('black')
        ax_ocr = fig_ocr.add_subplot(1, 1, 1)
        ax_ocr.set_xlabel("X")
        ax_ocr.set_ylabel("Y")
        timg_ocr = Image.open(jpg_tmp_file.name)
        w = timg_ocr.width
        h = timg_ocr.height
        ax_ocr.set_xlim(0, w)
        ax_ocr.set_ylim(0, h)
        ax_ocr.grid()
        ax_ocr.set_title("ocr_"+str(diary_id)+"_" +
                         diary_first_date.strftime('%m%d')+'_p'+diary_page_string+'.png')
        tdraw_ocr = ImageDraw.Draw(timg_ocr)
        xlim_ocr = ax_ocr.get_xlim()
        ylim_ocr = ax_ocr.get_ylim()
        p_num = int(len(dic_corners) / 4)
        for i in range(p_num):
            tdraw_ocr.line(
                (dic_corners[4*i+0], dic_corners[4*i+1]), fill=(55, 255, 2), width=5)
            tdraw_ocr.line(
                (dic_corners[4*i+1], dic_corners[4*i+2]), fill=(55, 255, 2), width=5)
            tdraw_ocr.line(
                (dic_corners[4*i+2], dic_corners[4*i+3]), fill=(55, 255, 2), width=5)
            tdraw_ocr.line(
                (dic_corners[4*i+3], dic_corners[4*i+0]), fill=(55, 255, 2), width=5)
        timg_ocr_array = np.asarray(timg_ocr)
        ax_ocr.imshow(timg_ocr_array, extent=[
                      *xlim_ocr, *ylim_ocr], aspect='auto', alpha=0.9)
        buf_ocr = io.BytesIO()
        fig_ocr.savefig(buf_ocr, format="png", dpi=300)
        # # plt.show()
        plt.close(fig_ocr)
        buf_ocr.seek(0)
        timgs_ocr = Image.open(buf_ocr).convert('RGB')
        timgs_ocr_pn = "../output/"+"ocr_" + \
            str(diary_id)+"_"+diary_first_date.strftime('%m%d') + \
            '_p'+diary_page_string+'.png'
        timgs_ocr.save(timgs_ocr_pn)
        # timgs_ocr.show()

        ###
        # Create ocr_urination_data_df from ocr_data_df (raw ocr image based dataframe)
        ###
        # ocr_urination_data_dfを8列版，ocr_data_dfを14列版とする
        ocr_urination_data_df = ocr_data_df.copy()
        #
        # Add a column
        ocr_urination_data_df['もれ'] = '無・少量・中量・多量'
        ocr_urination_data_df['尿意'] = '有・無'
        ocr_urination_data_df['切迫感'] = '有・無'
        ocr_urination_data_df['残尿感'] = '有・無'
        ocr_urination_data_df['メモ'] = ocr_urination_data_df['メモ欄']
        for index, row in ocr_urination_data_df.iterrows():
            if row['もれ無し'] == '無':
                row['もれ'] = '無'
            elif row['もれ少量'] == '少量':
                row['もれ'] = '少量'
            elif row['もれ中量'] == '中量':
                row['もれ'] = '中量'
            elif row['もれ多量'] == '多量':
                row['もれ'] = '多量'
            else:
                row['もれ'] = '無・少量・中量・多量'

            if row['尿意有り'] == '有':
                row['尿意'] = '有'
            elif row['尿意無し'] == '無':
                row['尿意'] = '無'
            else:
                row['尿意'] = '有・無'

            if row['切迫感有り'] == '有':
                row['切迫感'] = '有'
            elif row['切迫感無し'] == '無':
                row['切迫感'] = '無'
            else:
                row['切迫感'] = '有・無'

            if row['残尿感有り'] == '有':
                row['残尿感'] = '有'
            elif row['残尿感無し'] == '無':
                row['残尿感'] = '無'
            else:
                row['残尿感'] = '有・無'
        #
        # Drop some temporal columns
        ocr_urination_data_df.drop(columns=['もれ無し', 'もれ少量', 'もれ中量', 'もれ多量', '尿意有り',
                                   '尿意無し', '切迫感有り', '切迫感無し', '残尿感有り', '残尿感無し', 'メモ欄'], inplace=True)
        # for check
        mylogger.debug("========  ========")
        mylogger.debug(str(diary_id)+"_" +
                       diary_first_date.strftime('%m%d')+'_p'+diary_page_string)
        mylogger.debug(ocr_urination_data_df)
        mylogger.debug("========  ========")

        ###
        # Diary document csv
        ###
        ocr_urination_data_csv = convert_df_to_csv(ocr_urination_data_df)
        # ocr_urination_data_csv_fn = "ocr_"+str(diary_id)+"_"+diary_date.strftime('%Y%m%d')+'.csv'
        ocr_urination_data_csv_fn = "ocr_" + \
            str(diary_id)+"_"+diary_first_date.strftime('%m%d') + \
            '_p'+diary_page_string+'.csv'
        with open("../output/"+ocr_urination_data_csv_fn, "wb") as f:
            f.write(ocr_urination_data_csv)
        # XLSX出力除きここまででocr_urination_data_df使用終了

        # df creation from ocr_data_df (not ocr_urination_data_df) by deep copy
        urination_data_df = ocr_data_df.copy()  # ocr_data_dfの14列版から作ることに注意
        urination_data_df['メモ'] = urination_data_df['メモ欄']
        urination_data_df.drop(columns=['メモ欄'], inplace=True)

        ###
        # Date and time adjustment (Day and hour)
        ###
        ##########
        # 2022-07-14T16:00 修正
        #  st.write("<font color='red'>最初の行が深夜０時以降だと日付けがおかしくなる｡</font>", unsafe_allow_html=True)
        # 2022-07-14T17:15 修正
        #  st.write("<font color='red'>零時以降が翌日日付けにならない｡</font>", unsafe_allow_html=True)
        ##########
        #
        # Add some English name columns for urination_data_df
        urination_data_df['year'] = diary_date.strftime("%Y")
        urination_data_df['month'] = diary_date.strftime("%m")
        urination_data_df['day'] = diary_date.strftime("%d")
        urination_data_df['時'].replace('', np.nan, inplace=True)
        urination_data_df['分'].replace('', np.nan, inplace=True)
        urination_data_df['hour'] = urination_data_df['時'].astype(float)
        urination_data_df['minute'] = urination_data_df['分'].astype(float)
        urination_data_df['排尿量'].replace('', np.nan, inplace=True)
        urination_data_df['micturition'] = urination_data_df['排尿量'].astype(
            float)
        # urination_data_df['catheterization'] = urination_data_df['導尿量'].astype(float)
        urination_data_df['no_leakage'] = [True if b ==
                                           '無' else False for b in urination_data_df['もれ無し']]
        urination_data_df['leakage'] = [1.0 if b !=
                                        '無' else 0.0 for b in urination_data_df['もれ無し']]
        # urination_data_df['leakage'] = [3.0 if b =='多量' else 2.0 for b in urination_data_df['もれ多量']]
        # urination_data_df['leakage'] = [2.0 if b =='中量' else 1.0 for b in urination_data_df['もれ中量']]
        # urination_data_df['leakage'] = [1.0 if b =='少量' else 0.0 for b in urination_data_df['もれ少量']]
        urination_data_df['desire'] = [False if b ==
                                       '無' else True for b in urination_data_df['尿意無し']]
        urination_data_df['urgency'] = [True if b ==
                                        '有' else False for b in urination_data_df['切迫感有り']]
        urination_data_df['remaining'] = [True if b ==
                                          '有' else False for b in urination_data_df['残尿感有り']]
        urination_data_df['memo'] = urination_data_df['メモ']

        # for check
        # mylogger.debug(urination_data_df[['year', 'month', 'day', 'hour', 'minute']])
        urination_data_df['datetime_tmp'] = pd.to_datetime(
            urination_data_df[['year', 'month', 'day', 'hour', 'minute']]).dt.tz_localize('Asia/Tokyo')
        # COERCE  urination_data_df[['year', 'month', 'day', 'hour', 'minute']], errors='coerce')
        urination_data_df['datetime_tmp_before'] = urination_data_df['datetime_tmp'].shift(
            1)
        urination_data_df['datetime_tmp_after_check'] = urination_data_df['datetime_tmp'] > urination_data_df['datetime_tmp_before']
        # for check
        # mylogger.debug(urination_data_df['datetime_tmp_after_check'])

        #
        # datetime tmp COPY
        urination_data_df['datetime'] = urination_data_df['datetime_tmp']

        # erase line without datetime
        urination_data_df_tmp = urination_data_df.copy()
        urination_data_df = urination_data_df_tmp.dropna(subset=['datetime'])
        
        for index, row in urination_data_df.iterrows():
            if row['もれ無し'] == '無':
                row['no_leakage'] = True
            elif row['もれ無し'] == '有':
                row['no_leakage'] = False
            else:
                row['no_leakage'] = False
            if row['もれ無し'] == '無':
                row['leakage'] = 0.0
            elif row['もれ少量'] == '少量':
                row['leakage'] = 1.0
            elif row['もれ中量'] == '中量':
                row['leakage'] = 2.0
            elif row['もれ多量'] == '多量':
                row['leakage'] = 3.0
            else:
                row['leakage'] = np.nan
            if row['尿意有り'] == '有':
                row['desire'] = True
            elif row['尿意無し'] == '無':
                row['desire'] = False
            else:
                row['desire'] = True
            if row['切迫感有り'] == '有':
                row['urgency'] = True
            elif row['切迫感無し'] == '無':
                row['urgency'] = False
            else:
                row['urgency'] = False
            if row['残尿感有り'] == '有':
                row['remaining'] = True
            elif row['残尿感無し'] == '無':
                row['remaining'] = False
            else:
                row['remaining'] = False

        #
        # After midnight adjustment
        after_midnight = False
        after_midnight_state = ''
        for index, row in urination_data_df.iterrows():
            if (after_midnight == False) and (row['datetime_tmp_after_check'] == False):
                if index == 0:
                    if row['datetime_tmp'] < wakeup_datetime:
                        after_midnight = True
                        # 24, 25時以降にhourをいじり, datetimeをつくる
                        urination_data_df.at[index,
                                             'hour'] = urination_data_df.at[index, 'hour'] + 24
                        urination_data_df.at[index, 'datetime'] = urination_data_df.at[index,
                                                                                       'datetime_tmp'] + datetime.timedelta(hours=24)
                        after_midnight_state = "Line 0 and the first after midnight"
                    else:
                        after_midnight_state = "Line 0"
                        urination_data_df.at[index,
                                             'datetime'] = urination_data_df.at[index, 'datetime_tmp']
                else:
                    after_midnight = True
                    # 24, 25時以降にhourをいじり, datetimeをつくる
                    after_midnight_state = "First after midnight"
                    #
                    # rowhour = rowhour + 24
                    # rowdatetime = rowdatetime_tmp + datetime.timedelta(hours=24)
                    urination_data_df.at[index,
                                         'hour'] = urination_data_df.at[index, 'hour'] + 24
                    urination_data_df.at[index, 'datetime'] = urination_data_df.at[index,
                                                                                   'datetime_tmp'] + datetime.timedelta(hours=24)
            elif after_midnight == True:
                # 24, 25時以降ということであるので，hourをいじり, datetimeをつくる
                after_midnight_state = "Second or later after midnight"
                urination_data_df.at[index,
                                     'hour'] = urination_data_df.at[index, 'hour'] + 24
                urination_data_df.at[index, 'datetime'] = urination_data_df.at[index,
                                                                               'datetime_tmp'] + datetime.timedelta(hours=24)
                # rowhour = rowhour + 24
                # rowdatetime = rowdatetime_tmp + datetime.timedelta(hours=24)
            else:
                after_midnight_state = "Before midnight"
                urination_data_df.at[index,
                                     'datetime'] = urination_data_df.at[index, 'datetime_tmp']
            # for check
            # mylogger.debug(after_midnight_state)
        # for check
        # mylogger.debug(urination_data_df[['datetime', 'datetime_tmp_after_check', 'day', 'hour']])

        #
        # Calculate time difference
        urination_data_df['time_difference'] = urination_data_df['datetime'].diff()
        urination_data_df['time_difference'] = urination_data_df['time_difference'].dt.total_seconds(
        ) / 60.0

        #
        # Time phase
        first_after_wakeup_found = False
        # WIP
        # 最初の行が９時以降ならfirst_after_wakeup_found = Trueにしてしまうことにするかどうか。
        first_after_next_wakeup_found = False
        urination_data_df['time_phase'] = urination_data_df['datetime']
        for index, row in urination_data_df.iterrows():
            if row['datetime'] < wakeup_datetime:
                urination_data_df.at[index, 'time_phase'] = 'before_wakeup'
            elif row['datetime'] < bed_datetime:
                if first_after_wakeup_found == False:
                    first_after_wakeup_found = True
                    urination_data_df.at[index,
                                         'time_phase'] = 'first_after_wakeup'
                else:
                    urination_data_df.at[index, 'time_phase'] = 'day_time'
            elif row['datetime'] < next_wakeup_datetime:
                urination_data_df.at[index, 'time_phase'] = 'after_bed'
            else:
                if first_after_next_wakeup_found == False:
                    first_after_next_wakeup_found = True
                    urination_data_df.at[index,
                                         'time_phase'] = 'first_after_next_wakeup'
                else:
                    urination_data_df.at[index, 'time_phase'] = 'next_day_time'
        #
        #  first after bed datetime for FIST SLEEP CALCULATION
        first_after_bed_found = False
        for index, row in urination_data_df.iterrows():
            if row['datetime'] >= bed_datetime:
                if first_after_bed_found == False:
                    first_after_bed_found = True
                    first_after_bed_datetime = row['datetime']

        #
        # Drop some temporal English name columns
        urination_data_df.drop(columns=[
            'datetime_tmp', 'datetime_tmp_before', 'datetime_tmp_after_check'], inplace=True)
        # for check
        # st.write(urination_data_df)

        ###
        # Recognized diary
        ###
        # mylogger.info("日誌データ（認識結果）")
        # mylogger.info("テーブル（認識結果）")
        # Recognized image(s)
        ##### resimg = Image.open('images/diary_form1_sample1_virtually_recognized.png')
        ##### st.image(resimg, caption='認識された日誌画像', width=240)

        ###
        # recognized document (=data) Type A
        ###
        #
        # recognized document preparation Type A
        ud_df1_tmp = urination_data_df.drop(columns=['時', '分'])
#   ud_df1_tmp = urination_data_df.drop(columns=['時', '分',
#                                                 'micturition',
#                                                 'leakage', 'desire', 'urgency', 'remaining',
#                                                 'memo'])
#   ud_df1_tmp = urination_data_df.drop(columns=['時', '分',
#                                                 'year', 'month', 'day',
#                                                 'hour', 'minute',
#                                                 'micturition',
#                                                 'leakage', 'desire', 'urgency', 'remaining',
#                                                 'memo'])
        ud_df1 = ud_df1_tmp.dropna(subset=['datetime'])
        #
        # recognized document display Type A by st.table
        # ud_df1.style.highlight_max(axis=0))
        #
        # recognized document CSV (=data CSV)
        ud_df1_csv = convert_df_to_csv(ud_df1)
        # ud_df1_csv_fn = "ud_"+str(diary_id)+"_"+diary_date.strftime('%Y%m%d')+'.csv'
        ud_df1_csv_fn = "ud_" + \
            str(diary_id)+"_"+diary_first_date.strftime('%m%d') + \
            '_p'+diary_page_string+'.csv'

        with open("../output/"+ud_df1_csv_fn, "wb") as f:
            f.write(ud_df1_csv)

        ###
        # Wakeup time and bed time display
        ###
        # mylogger.info('起床時刻・就寝時刻・翌日起床時刻・翌日就寝時刻：')
        # mylogger.info('対象日の起床時刻は' + wakeup_datetime.strftime("%Y-%m-%dT%H:%M") + 'です。')
        # mylogger.info('対象日の就寝時刻は' + bed_datetime.strftime("%Y-%m-%dT%H:%M") + 'です。')
        # mylogger.info('対象日の就寝時刻と起床時刻の差は' + str(bed_datetime-wakeup_datetime) + 'です。')
        # mylogger.info('翌日の起床時刻は' + next_wakeup_datetime.strftime("%Y-%m-%dT%H:%M") + 'です。')
        # mylogger.info('翌朝の起床時刻と対象日の就寝時刻の差（つまり睡眠時間）' +
        #              str(next_wakeup_datetime - bed_datetime) + 'です。')
        # mylogger.info('翌日の就寝時刻は' + next_bed_datetime.strftime("%Y-%m-%dT%H:%M") + 'です。')
        # mylogger.info('翌日の就寝時刻と起床時刻の差は' +
        #              str(next_bed_datetime - next_wakeup_datetime) + 'です。')

        
        ###
        # Indices
        ###
        # mylogger.info('排尿関連指標：')
        if first_after_bed_found == True:
            first_sleep_time = (first_after_bed_datetime -
                                bed_datetime).total_seconds() / 60
        else:
            first_sleep_time = 0
        ########## 2022/8/9に変更。起床後初回排尿以降を「一日」とみなす。 start
        number_of_urination = len(urination_data_df[ (urination_data_df['time_phase'] == 'first_after_wakeup') | (urination_data_df['time_phase'] == 'day_time') | (urination_data_df['time_phase'] == 'after_bed') ])
        number_of_daytime_urination = len(
            urination_data_df[ (urination_data_df['time_phase'] == 'first_after_wakeup') | (urination_data_df['time_phase'] == 'day_time')])
        number_of_nocturnal_urination = len(urination_data_df[ urination_data_df['time_phase'] == 'after_bed'] )
        ########## 2022/8/9に変更。起床後初回排尿以降を「一日」とみなす。 end
        
        daytime_urination_volume = urination_data_df[urination_data_df['time_phase'] == 'day_time'].micturition.sum(
        )
        nocturnal_urination_volume = urination_data_df[(urination_data_df['time_phase'] == 'after_bed') | (
            urination_data_df['time_phase'] == 'first_after_next_wakeup')].micturition.sum()
        urination_volume = urination_data_df[(urination_data_df['time_phase'] == 'after_bed') | (
            urination_data_df['time_phase'] == 'first_after_next_wakeup') | (urination_data_df['time_phase'] == 'day_time')].micturition.sum()
        
        if np.isnan(daytime_urination_volume) == True:
            daytime_urination_volume = 0.0
        if np.isnan(nocturnal_urination_volume) == True:
            nocturnal_urination_volume = 0.0
        if np.isnan(urination_volume) == True:
            urination_volume = 0.0
        if number_of_urination != 0:
            urination_volume_per_cycle = urination_volume / number_of_urination # 悩むところだが差し引き1-1=0でこれでわる
        else:
            urination_volume_per_cycle = 0

        
        minimum_single_urination_volume = urination_data_df[(urination_data_df['time_phase'] == 'after_bed') | (
            urination_data_df['time_phase'] == 'first_after_next_wakeup') | (urination_data_df['time_phase'] == 'day_time')].micturition.min()
        maximum_single_urination_volume = urination_data_df[(urination_data_df['time_phase'] == 'after_bed') | (
            urination_data_df['time_phase'] == 'first_after_next_wakeup') | (urination_data_df['time_phase'] == 'day_time')].micturition.max()
        minimum_single_nocturnal_urination_volume = urination_data_df[(urination_data_df['time_phase'] == 'after_bed') | (
            urination_data_df['time_phase'] == 'first_after_next_wakeup')].micturition.min()
        maximum_single_nocturnal_urination_volume = urination_data_df[(urination_data_df['time_phase'] == 'after_bed') | (
            urination_data_df['time_phase'] == 'first_after_next_wakeup')].micturition.max()

        average_urination_interval = urination_data_df.mean(
            numeric_only=True).time_difference
        minimum_urination_interval = urination_data_df.min(
            numeric_only=True).time_difference
        maximum_urination_interval = urination_data_df.max(
            numeric_only=True).time_difference

        if np.isnan(average_urination_interval) == True:
            average_urination_interval = 0.0
        if np.isnan(minimum_urination_interval) == True:
            minimum_urination_interval = 0.0
        if np.isnan(maximum_urination_interval) == True:
            maximum_urination_interval = 0.0

        if np.isnan(maximum_single_urination_volume) == True:
            maximum_single_urination_volume = 0.0
        if np.isnan(minimum_single_urination_volume) == True:
            minimum_single_urination_volume = 0.0
        if np.isnan(maximum_single_nocturnal_urination_volume) == True:
            maximum_single_nocturnal_urination_volume = 0.0
        if np.isnan(minimum_single_nocturnal_urination_volume) == True:
            minimum_single_nocturnal_urination_volume = 0.0
        if urination_volume != 0:
            noctural_plyuria_index = float(
                nocturnal_urination_volume * 100.0 / urination_volume)
        else:
            noctural_plyuria_index = 0.0

        # WIP
        # maximum_voided_volumeに漏れや導尿をいれてない
        maximum_voided_volume = maximum_single_urination_volume
        if maximum_voided_volume != 0:
            nocturia_index = math.ceil(
                float(nocturnal_urination_volume / maximum_voided_volume))
        else:
            nocturia_index = int(1)
        pnv = nocturia_index - 1
        nbci = number_of_nocturnal_urination - pnv
        #
        number_of_urinary_tracts = 0
        urinary_tract_volume = 0
        urinary_tract_volume_per_cycle = 0
        minimum_single_urinary_tract_volume = 0
        maximum_single_urinary_tract_volume = 0
        # 昼間排尿回数 8回以上 昼間頻尿
        # 夜間排尿回数 1回以上 夜間頻尿 Nocturia episodesという
        # 最大一回排尿量 maximum voided volume MVV という
        # 夜間多尿指数(NPi) 夜間排尿量/一日尿量 （若年20％，高齢33％のスレショルド）
        #
        # 夜間頻尿指数(Ni) 夜間排尿量/最大一回排尿量 （Ni>1が夜間頻尿。切り上げ）
        # 予測夜間排尿回数(PNV)  (夜間排尿量/最大一回排尿量) - 1
        # 夜間膀胱容量指数(NBCi) 実際の夜間排尿回数-予測夜間排尿回数 （NBCi>0を機能的膀胱容量低下での夜間頻尿）
        # 多尿 一日尿量が40ml/kg以上というスレショルド
        # 初回睡眠時間 Hours of undisturbed sleep
        #
        # 体重
        # 最大排尿量/体重 （4ml/kg以下が機能的膀胱容量低下のスレショルド）
        # 残尿回数
        # 一日残尿量
        # 尿失禁回数
        # 尿失禁量(g/日)

        ###
        # indices
        ###
        #
        # indices preparation
        diary_first_date_int = int(diary_first_date.strftime('%Y%m%d'))
        diary_date_int = int(diary_date.strftime('%Y%m%d'))
        indices_df = pd.DataFrame(columns=['指標', '値', '単位'],
                                  data=[
                                      ['日誌対象者ID', int(diary_id), ''],
                                      ['日誌初回日付', int(
                                          diary_first_date_int), ''],
                                      ['日誌ページ', int(diary_page), ''],
                                      ['日誌日付', int(diary_date_int), ''],
                                      ['初回睡眠時間(HUS)', int(
                                          first_sleep_time), '分'],
                                      ['最大尿量(MVV)', int(
                                          maximum_voided_volume), 'ml'],
                                      ['夜間多尿指数(NPi)', int(
                                          noctural_plyuria_index), '％'],
                                      ['夜間頻尿指数(Ni)', int(nocturia_index), ''],
                                      ['予測夜間排尿回数(PNV)', int(pnv), '回'],
                                      ['夜間膀胱容量指数(NBCi)', int(nbci), '回'],
                                      ['昼間排尿回数', int(
                                          number_of_daytime_urination), '回'],
                                      ['夜間排尿回数', int(
                                          number_of_nocturnal_urination), '回'],
                                      ['一日排尿回数', int(
                                          number_of_urination), '回'],
                                      ['昼間排尿量', int(
                                          daytime_urination_volume), 'ml'],
                                      ['夜間排尿量(NUV)', int(
                                          nocturnal_urination_volume), 'ml'],
                                      ['一日排尿量', int(urination_volume), 'ml'],
                                      ['一回排尿量', int(
                                          urination_volume_per_cycle), 'ml / 回'],
                                      ['最小一回排尿量', int(
                                          minimum_single_urination_volume), 'ml'],
                                      ['最大一回排尿量', int(
                                          maximum_single_urination_volume), 'ml'],
                                      ['最小一回夜間排尿量', int(
                                          minimum_single_nocturnal_urination_volume), 'ml'],
                                      ['最大一回夜間排尿量(NBC)', int(
                                          maximum_single_nocturnal_urination_volume), 'ml'],
                                      ['平均排尿間隔', int(
                                          average_urination_interval), '分'],
                                      ['最小排尿間隔', int(
                                          minimum_urination_interval), '分'],
                                      ['最大排尿間隔', int(
                                          maximum_urination_interval), '分'],
                                      ['一日導尿回数', int(
                                          number_of_urinary_tracts), '回'],
                                      ['一日導尿量', int(
                                          urinary_tract_volume), 'ml'],
                                      ['一回導尿量', int(
                                          urinary_tract_volume_per_cycle), 'ml / 回'],
                                      ['最小一回導尿量', int(
                                          minimum_single_urinary_tract_volume), 'ml'],
                                      ['最大一回導尿量', int(
                                          maximum_single_urinary_tract_volume), 'ml'],
        ])

        #
        # indices
        # mylogger.info(indices_df)
        #
        # indices CSV
        indices_csv = convert_df_to_csv(indices_df)
        # indices_csv_fn = "indices_" +  str(diary_id)+"_"+diary_date.strftime('%Y%m%d')+'.csv'
        indices_csv_fn = "indices_" + \
            str(diary_id)+"_"+diary_first_date.strftime('%m%d') + \
            '_p'+diary_page_string+'.csv'
        with open("../output/"+indices_csv_fn, "wb") as f:
            f.write(indices_csv)

        #
        # composite
        #
        ud_df1.insert(0, 'date_time', ud_df1['datetime'].apply(
            lambda d: pd.Timestamp(d).isoformat()))
        ud_df1_for_composite = ud_df1.drop(columns='datetime')
        composite_xlsx_fn = "composite_" + \
            str(diary_id)+"_"+diary_first_date.strftime('%m%d') + \
            '_p'+diary_page_string+'.xlsx'
        with pd.ExcelWriter("../output/"+composite_xlsx_fn) as composite_writer:
            ud_df1_for_composite.to_excel(
                composite_writer, sheet_name=ud_df1_csv_fn)
            indices_df.to_excel(composite_writer, sheet_name=indices_csv_fn)
            ocr_urination_data_df.to_excel(
                composite_writer, sheet_name=ocr_urination_data_csv_fn)

    ###
    ###
    ###
    except Exception:
        mylogger.exception("Exception from app. ")
        mylogger.exception("-"*30)
        mylogger.exception(traceback.format_exc())
        mylogger.exception("-"*30)


###
###
###
if __name__ == "__main__":
    ## sys.stderr.write('__name__ = '+str(__name__)+'\n')
    ## sys.stderr.write('__file__ = '+str(__file__)+'\n')

    set_logger(__name__)
    mylogger = logging.getLogger(__name__)
    # mylogger.debug('Debug log test.')
    # mylogger.info('Info log test.')
    # mylogger.warning('Warning log test.')
    # mylogger.error('Error log test.')
    # mylogger.critical('Critical log test.')

    # basename = os.path.basename(__file__)
    # mylogger.debug(basename); mylogger.debug(os.path.splitext(basename))

    args = get_args()
    # mylogger.debug(args)
    if hasattr(args, 'diary_image_filename'):
        # mylogger.debug("The diary image filename is " + args.diary_image_filename)
        diary_arg_image_filename = args.diary_image_filename
        if hasattr(args, 'id'):
            # mylogger.debug("The ID is "+str(args.id))
            diary_arg_id = args.id
            if hasattr(args, 'day'):
                # mylogger.debug("Month and day as 0704 for July 4th: "+str(args.day))
                diary_arg_day = args.day
                diary_arg_idday_string = '{:0=4}'.format(
                    diary_arg_id) + '_' + '{:0=4}'.format(diary_arg_day)
            else:  # default DAY=0101 if only the ID is given
                diary_arg_idday_string = '{:0=4}'.format(
                    diary_arg_id) + '_' + '{:0=4}'.format(101)
        else:
            diary_arg_idday_string = diary_arg_image_filename
    diary_image_filename = diary_arg_image_filename
    diary_id = int(diary_arg_idday_string[0:4])
    diary_year_string = '2021'
    diary_month_string = diary_arg_idday_string[5:7]
    diary_day_string = diary_arg_idday_string[7:9]
    diary_page_string = diary_arg_idday_string[11:12]
    diary_first_date = datetime.date(year=int(diary_year_string),
                                     month=int(diary_month_string),
                                     day=int(diary_day_string))
    diary_page = int(diary_page_string)
    #    diary_date = datetime.date(year=int(diary_year_string),
    #                               month=int(diary_month_string),
    #                               day=(int(diary_day_string) + int(diary_page) - 2))
    delta = diary_page - 1
    diary_date = datetime.date(year=int(diary_year_string),
                               month=int(diary_month_string),
                               day=(int(diary_day_string))) + datetime.timedelta(days=delta)
    # mylogger.debug(diary_id)
    # mylogger.debug(diary_first_date)
    # mylogger.debug(diary_page)
    # mylogger.debug(diary_date)

    main(args)


#######
#######
#######
#######
#######

# ErrorCode	Description
# 0001	URL is invalid.
# 0002	Secret key validate failed.
# 0011	Request body invalid.
# 0021	Protocol version not support.
# 0022	Request domain invalid.
# 0023	API request count reach the upper limit.
# 0025	Calls to this api have exceeded the rate limit.
# 0500	Unknown service error.
# 0501	OCR Service error.
# 1021	Not found deploy infomation.Please confirm the template is released
