from Wallboard.models import *
from .models import *
from zoho.models import ZohoContactsSyncSettings, ZohoSyncErrorLogs
import time
import datetime
from datetime import datetime, timezone, date,timedelta
import zcrmsdk
import pymysql
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,JsonResponse
from sshtunnel import SSHTunnelForwarder
import mysql.connector
from .serializer import *
import json
from json import loads
from django.db.models import Count, Max, Min
from rest_framework import serializers
from django.views.decorators.http import require_http_methods
import pandas as pd
from django.conf import settings
from sqlalchemy import create_engine
import pytz



def londonTimeConvert(normalDatetime):
    tz = pytz.timezone('UTC')
    london_tz = pytz.timezone('Europe/London')
    london_time = normalDatetime.astimezone(london_tz)
    return london_time

# def logg(dt):
#     ZohoSyncErrorLogs.objects.create(module_type='Wallboard - extensions_sync', added_on=datetime.now(),  error_message="london europe time"+st

def extensions_sync():
    try:
        naive = datetime.now()
        print("Current default format",datetime.now())
        UTC = pytz.UTC
        IST = pytz.timezone('Europe/London')
        print("UTC in default format",datetime.now(UTC))
        print("IST in defualt format",datetime.now(IST))
        ZohoSyncErrorLogs.objects.create(module_type='Wallboard - extensions_sync', added_on=datetime.now(),  error_message="utc time"+str(datetime.now(UTC)))
        ZohoSyncErrorLogs.objects.create(module_type='Wallboard - extensions_sync', added_on=datetime.now(),  error_message="london europe time"+str(datetime.now(IST)))
        ZohoSyncErrorLogs.objects.create(module_type='Wallboard - extensions_sync', added_on=datetime.now(),  error_message="datetime"+str(datetime.now()))
        # server = SSHTunnelForwarder(('94.228.41.183', 22),ssh_password="gSuvzREVdW7Ptjse",ssh_username="testuser",remote_bind_address=('94.228.41.183', 3306))
        # server.start()
        month = date.today().month
        year = date.today().year
        sYear = str(year)+"-"+str(month)+"-"+"1"
        eYear = str(year)+"-"+str(month)+"-"+"31"
        print(month)
        dbsync = DBSync.objects.all().first()
        if dbsync.enable_call_sync == True:
            db = mysql.connector.connect(host=dbsync.hostname,user=dbsync.username,password=dbsync.password,database=dbsync.database_name)
            print("successfully connected")
            cursor = db.cursor()
            wbcdrInfo = wbcdr.objects.all()
            if not wbcdrInfo.exists():
                cursor.execute("select * from cdr where calldate >= %s and calldate <= %s and dcontext = %s and lastapp = %s",[sYear,eYear,"from-internal","Dial"])
                classVideo = cursor.fetchall()
                print(classVideo)
                for i in classVideo:
                    # saveWcdr = wbcdr(calldate=i[0],cid=i[1],src=i[2],dst=i[3],dcontext=i[4],channel=i[5],dstchannel=i[6],lastapp=i[7],lastdata=i[8],duration=i[9],billsec=i[10],disposition=i[11],amaflags=i[12],accountcode=i[13],uniqueid=i[14],userfield=i[15],did=i[16],recordingfile=i[17],cnum=i[18],cnam=i[19],outbound_cnum=i[20],outbound_cnam=i[21],dst_cnam=i[22],linkedid=i[23],peeraccount=i[24],sequence=i[25])
                    # saveWcdr.save()
                    # var = {"calldate":i[0],"cid":i[1],"src":i[2],"dst":i[3],"dcontext":i[4],"channel":i[5],"dstchannel":i[6],"lastapp":i[7],"lastdata":i[8],"duration":i[9],"billsec":i[10],"disposition":i[11],"amaflags":i[12],"accountcode":i[13],"uniqueid":i[14],"userfield":i[15],"did":i[16],"recordingfile":i[17],"cnum":i[18],"cnam":i[19],"outbound_cnum":i[20],"outbound_cnam":i[21],"dst_cnam":i[22],"linkedid":i[23],"peeraccount":i[24],"sequence":i[25]}
                    print("mysql normal datetime",i[0])
                    tz = pytz.timezone('UTC')
                    tz_time = tz.localize(i[0])
                    print("mysql datetime to UTC timezone",tz_time)
                    london_time = londonTimeConvert(i[0])
                    print("mysql datetime to london timezone",london_time)
                    ZohoSyncErrorLogs.objects.create(module_type='Wallboard - extensions_sync', added_on=datetime.now(),  error_message="mysql normal datetime: "+str(i[0]))
                    ZohoSyncErrorLogs.objects.create(module_type='Wallboard - extensions_sync', added_on=datetime.now(),  error_message="mysql datetime to UTC timezone"+str(tz_time))
                    ZohoSyncErrorLogs.objects.create(module_type='Wallboard - extensions_sync', added_on=datetime.now(),  error_message="mysql datetime to london timezone"+str(london_time))
                    var = {"calldate":london_time,"cid":i[1],"src":i[2],"dst":i[3],"dcontext":i[4],"channel":i[5],"dstchannel":i[6],"lastapp":i[7],"lastdata":i[8],"duration":i[9],"billsec":i[10],"disposition":i[11],"amaflags":i[12],"accountcode":i[13],"uniqueid":i[14],"userfield":i[15],"did":i[16],"recordingfile":i[17],"cnum":i[18],"cnam":i[19],"outbound_cnum":i[20],"outbound_cnam":i[21],"dst_cnam":i[22],"linkedid":i[23],"peeraccount":i[24],"sequence":i[25]}
                    seri = wbcdrInfoSerializer(data=var)
                    if seri.is_valid():
                        seri.save()
                    else:
                        return JsonResponse({"status":"failure","message":str(seri.errors)})
            else:
                wbcdrInfo = wbcdr.objects.aggregate(Max('calldate'))
                callDate = wbcdrInfo["calldate__max"]
                # cursor.execute("select * from cdr where calldate > %s",[callDate])
                cursor.execute("select * from cdr where calldate >= %s and dcontext = %s and lastapp = %s",[callDate,"from-internal","Dial"])
                x = cursor.fetchall()
                if len(x) > 0:
                    for i in x:
                        lDatetime = londonTimeConvert(i[0])
                        print("mysql datetime to london timezone",lDatetime)
                        print("mysql normal datetime",i[0])
                        tz = pytz.timezone('UTC')
                        tz_time = tz.localize(i[0])
                        print("mysql datetime to UTC timezone",tz_time)
                        ZohoSyncErrorLogs.objects.create(module_type='Wallboard - extensions_sync', added_on=datetime.now(),  error_message="mysql normal datetime"+str(i[0]))
                        ZohoSyncErrorLogs.objects.create(module_type='Wallboard - extensions_sync', added_on=datetime.now(),  error_message="mysql datetime to UTC timezone"+str(tz_time))
                        ZohoSyncErrorLogs.objects.create(module_type='Wallboard - extensions_sync', added_on=datetime.now(),  error_message="mysql datetime to london timezone"+str(lDatetime))
                        valCheck = wbcdr.objects.filter(calldate=i[0],uniqueid=i[14])
                        if valCheck.exists():
                            pass
                            print("nothing")
                        else:
                            # saveWcdr = wbcdr(calldate=i[0],cid=i[1],src=i[2],dst=i[3],dcontext=i[4],channel=i[5],dstchannel=i[6],lastapp=i[7],lastdata=i[8],duration=i[9],billsec=i[10],disposition=i[11],amaflags=i[12],accountcode=i[13],uniqueid=i[14],userfield=i[15],did=i[16],recordingfile=i[17],cnum=i[18],cnam=i[19],outbound_cnum=i[20],outbound_cnam=i[21],dst_cnam=i[22],linkedid=i[23],peeraccount=i[24],sequence=i[25])
                            # saveWcdr.save()
                            tz = pytz.timezone('UTC')
                            london_tz = pytz.timezone('Europe/London')
                            london_time = i[0].astimezone(london_tz)
                            var = {"calldate":london_time,"cid":i[1],"src":i[2],"dst":i[3],"dcontext":i[4],"channel":i[5],"dstchannel":i[6],"lastapp":i[7],"lastdata":i[8],"duration":i[9],"billsec":i[10],"disposition":i[11],"amaflags":i[12],"accountcode":i[13],"uniqueid":i[14],"userfield":i[15],"did":i[16],"recordingfile":i[17],"cnum":i[18],"cnam":i[19],"outbound_cnum":i[20],"outbound_cnam":i[21],"dst_cnam":i[22],"linkedid":i[23],"peeraccount":i[24],"sequence":i[25]}
                            seri = wbcdrInfoSerializer(data=var)
                            if seri.is_valid():
                                seri.save()
                            else:
                                return JsonResponse({"status":"failure","message":str(seri.errors)})
                else:
                    return JsonResponse({"status":"failure","message":"records not there"})
                db.commit()
            db.close()
            return JsonResponse({"status":"success","message":"successfully saved"})
    except Exception as ex:
        return JsonResponse({"status":"failure","message":str(ex)})
        # ZohoSyncErrorLogs.objects.create(module_type='Wallboard - extensions_sync', added_on=datetime.now(),  error_message=str(ex))
         
from django.db.models import Sum

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds)


def stats_week_1():
    try:
        vWCdate  = datetime.now() - timedelta(days=datetime.today().weekday() % 7 )
        vWCdate = londonTimeConvert(vWCdate)
        expData = vWCdate + timedelta(days=6)
        print(expData,"=======",vWCdate.date())
        startDay = wbcdr.objects.filter(calldate__gte=vWCdate.date(),calldate__lte=expData.date(),process_field=0).values('cnum').annotate(Sum('duration'),Sum('billsec'),total=Count('cnum'))
        for i in startDay:
            print(i,"111111111111111")
            weekCheck = stats_week.objects.filter(wcdate=vWCdate.date(),extension=i["cnum"])
            # print(weekCheck,"11111111111111111222222222222222222222222")
            if weekCheck.exists():
                update = 1
                print("already there")
                startWeek = stats_week.objects.get(wcdate=vWCdate.date(),extension=i["cnum"])
                print(startWeek.callqty,"-----------------",type(i["total"]))
                vExtension = startWeek.extension
                vDuration = startWeek.duration + i["duration__sum"]
                vBillsec = startWeek.billsec + i["billsec__sum"]
                # print(stats_week.callqty,type(startWeek.callqty),i["total"],type(i["total"]))
                vCallQty = startWeek.callqty + i["total"]
                # print(vCallQty,"***********")
            else:
                print("new")
                update = 0
                vExtension = i["cnum"]
                vDuration = i["duration__sum"]
                vBillsec = i["billsec__sum"]
                vCallQty = i["total"]
            callMinutes = convert(vBillsec)
            print(vWCdate.date(),vExtension,vDuration,vBillsec,vCallQty,callMinutes,"00000000000000000")
            if update == 1:
                print("update",vCallQty) 
                stats_week.objects.filter(wcdate=vWCdate.date(),extension=i["cnum"]).update(duration=vDuration,billsec=vBillsec,callqty=vCallQty,callminutes=callMinutes)
            else:
                add = stats_week(wcdate=vWCdate.date(),extension=vExtension,duration=vDuration,billsec=vBillsec,callqty=vCallQty,callminutes=callMinutes)
                add.save()
        return JsonResponse({"status":"success","message":"successfully saved"})
    except Exception as error:
        ZohoSyncErrorLogs.objects.create(module_type='Wallboard - stats_week', added_on=datetime.now(),  error_message=str(error))

import calendar
from time import gmtime, strftime



def statsMonth():
    try:
        eyear = calendar.monthrange(int(strftime("%Y", gmtime())), int(strftime("%m", gmtime())))[1]
        month = date.today().month
        year = date.today().year
        given_date = datetime.today().date()
        sYear = given_date.strftime("%Y-%m-01")
 
        eYear = given_date.strftime("%Y-%m-"+str(eyear))
        sYear = datetime.fromisoformat(sYear)
        eYear = datetime.fromisoformat(eYear)
        print(sYear,eYear)
        startDay = wbcdr.objects.filter(calldate__gte=sYear,calldate__lte=eYear,process_field=0).values('cnum').annotate(Sum('duration'),Sum('billsec'),total=Count('cnum'))
        print(startDay,"==========")
        for i in startDay:
            monthCheck = stats_month.objects.filter(mcdate__gte=sYear,mcdate__lte=eYear,extension=i["cnum"])
            if monthCheck.exists():
                update = 1
                startMonth=stats_month.objects.get(mcdate__gte=sYear,mcdate__lte=eYear,extension=i["cnum"])
                vExtension = startMonth.extension 
                vDuration = startMonth.duration + i["duration__sum"]
                vBillsec = startMonth.billsec + i["billsec__sum"]
                vCallQty = startMonth.callqty + i["total"]
            else:
                update = 0
                vExtension = i["cnum"]
                vDuration = i["duration__sum"]
                vBillsec = i["billsec__sum"]
                vCallQty = i["total"]
            callMinutes = convert(vBillsec)
            print(vDuration,vBillsec,vCallQty,"*************")
            if update==1:
                print("update")
                stats_month.objects.filter(mcdate=sYear,extension=i["cnum"]).update(duration=vDuration,billsec=vBillsec,callqty=vCallQty,callminutes=callMinutes)
            else:
                print("add")
                add = stats_month(mcdate=sYear,extension=vExtension,duration=vDuration,billsec=vBillsec,callqty=vCallQty,callminutes=callMinutes)
                add.save()
        return JsonResponse({"status":"success","message":"successfully saved"})
    except Exception as error:
        ZohoSyncErrorLogs.objects.create(module_type='Wallboard - stats_month', added_on=datetime.now(),  error_message=str(error))

def statsYear():
    try:
        year = date.today().year
        sYear = datetime.fromisoformat(str(year)+"-01-01")
        eYear = datetime.fromisoformat(str(year)+"-12-31")
        print(type(sYear),type(eYear))
        startDay = wbcdr.objects.filter(calldate__gte=sYear,calldate__lte=eYear,process_field=0).values('cnum').annotate(Sum('duration'),Sum('billsec'),total=Count('cnum'))
        for i in startDay:
            print(i,"!!!!!!!!!!!!!!!!!!")
            yearCheck = stats_year.objects.filter(ycdate__date=sYear.date(),extension=i["cnum"])
            if yearCheck.exists():
                update = 1
                startYear=stats_year.objects.get(ycdate__date=sYear.date(),extension=i["cnum"])
                vExtension = startYear.extension 
                vDuration = startYear.duration + i["duration__sum"]
                vBillsec = startYear.billsec + i["billsec__sum"]
                vCallQty = startYear.callqty + i["total"]
            else:
                update = 0
                vExtension = i["cnum"]
                vDuration = i["duration__sum"]
                vBillsec = i["billsec__sum"]
                vCallQty = i["total"]
            callMinutes = convert(vBillsec)
            print(vDuration,vBillsec,vCallQty,"*************")
            if update==1:
                print("update")
                stats_year.objects.filter(ycdate=sYear,extension=i["cnum"]).update(duration=vDuration,billsec=vBillsec,callqty=vCallQty,callminutes=callMinutes)
            else:
                print("add")
                add = stats_year(ycdate=sYear,extension=vExtension,duration=vDuration,billsec=vBillsec,callqty=vCallQty,callminutes=callMinutes)
                add.save()
        return JsonResponse({"status":"success","message":"successfully saved"})
    except Exception as error:
        ZohoSyncErrorLogs.objects.create(module_type='Wallboard - stats_year', added_on=datetime.now(),  error_message=str(error))


def call_status():
    try:
        currentDate = datetime.now()
        currentDate = londonTimeConvert(currentDate)
        dateOnly = currentDate.date()
        wbcdrInfo = wbcdr.objects.filter(calldate__date=dateOnly,process_field=0).values('cnum').annotate(Sum('duration'),Sum('billsec'),total=Count('cnum'))
        print(wbcdrInfo,"00000000000")
        for i in wbcdrInfo:
            statDay = stats_day.objects.filter(cdate__date=dateOnly,extension=i["cnum"])
            if statDay.exists():
                update = 1
                statDay = stats_day.objects.get(extension=i["cnum"])
                vFirstCall = statDay.firstcall
                vCnum = statDay.extension 
                vDuration = statDay.duration + i["duration__sum"]
                vBillsec = statDay.billsec + i["billsec__sum"]
                vCallQty = statDay.callqty + i["total"]
            else:
                update = 0
                vFirstCall = 0
                vCnum = i["cnum"]
                vLastCall = 0
                vDuration = i["duration__sum"]
                vBillsec = i["billsec__sum"]
                vCallQty = i["total"]
            ad = wbcdr.objects.filter(calldate__date=dateOnly,cnum=i["cnum"],process_field=0).values('calldate','cnum').order_by('calldate','cnum')
            for i in range(len(ad)):
                print(ad[i],"1111111111111111")
                if i == 0:
                    if update == 1:
                        vFirstCall = vFirstCall
                    else:
                        vFirstCall = ad[i]["calldate"]
                    vLastCall = ad[i]["calldate"]
                else:
                    vLastCall = ad[i]["calldate"]
            # print(vFirstCall,"11111111111111")
            # add = stats_day(firstcall=vFirstCall)
            tz = pytz.timezone('UTC')
            london_tz = pytz.timezone('Europe/London')
            vFirstCall = vFirstCall.astimezone(london_tz)
            vLastCall = vLastCall.astimezone(london_tz)
            callMinutes = convert(vBillsec)

            if update==1:
                print("update")
                stats_day.objects.filter(cdate__date=dateOnly,extension=vCnum).update(cdate=vLastCall,firstcall=vFirstCall,lastcall=vLastCall,duration=vDuration,billsec=vBillsec,callqty=vCallQty,callminutes=callMinutes)
            else:
                print("add")
                add = stats_day(cdate=vLastCall,extension=vCnum,firstcall=vFirstCall,lastcall=vLastCall,duration=vDuration,billsec=vBillsec,callqty=vCallQty,callminutes=callMinutes)
                add.save()
            stats_week_1()
            statsMonth()
            statsYear()
            wbcdr.objects.filter(calldate__date=dateOnly,cnum=vCnum).update(process_field=1)
            # var = {"firstcall":vFirstCall,"lastcall":vLastCall,"duration":vDuration,"billsec":vBillsec,"callqty":vCallQty}
            # print(var)
            # seri = StatsDayInfoSerializer(data=var)
            # if seri.is_valid():
            #     seri.save()
            # else:
            #     return JsonResponse({"status":"failure","message":"request not valid"})
        return JsonResponse({"status":"success","message":"successfully"})   
    except Exception as error:
        ZohoSyncErrorLogs.objects.create(module_type='Wallboard - stats_day', added_on=datetime.now(),  error_message=str(error))