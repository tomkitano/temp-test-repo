#-*-coding:utf-8-*-
"""
参考
    http://b4rracud4.hatenadiary.jp/entry/20181207/1544129263
    https://matplotlib.org/gallery/user_interfaces/embedding_in_tk_sgskip.html
    https://pg-chain.com/python-tkinter-entry
"""
import numpy as np
import pandas as pd
import tkinter
from tkinter import messagebox
import tkinter.messagebox as tkmsg
from tkinter import *
from tkinter import Tk,ttk
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg  import FigureCanvasTkAgg
from functools import partial
import matplotlib as mpl

from datetime import datetime

from sqlalchemy.sql import func
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fins_protocol import Fins
import socket
import subprocess
bg_color_type='light cyan'
bg_color_type='azure'
color_type='light cyan'
color_type='azure'
graph_color_type='lightcyan'
graph_color_type='azure'
graph_color_type_enter='white'
font_size=14
width_size=14
btn_width_size=12
tree_font_size=13
font_type="MS ゴシック"

relief_type='solid'
relief_type='ridge'

select_list=[]

import openpyxl
file='トラブルシューティング.xlsx'
# ブックを取得
book = openpyxl.load_workbook(file)
# シートを取得 
sheet = book['Sheet1']

# 釜センサー異常
m_A1=sheet['A1'].value
m_B1=sheet['B1'].value
m_B2=sheet['B2'].value

# 過昇温
m_A5=sheet['A5'].value
m_B5=sheet['B5'].value
m_B6=sheet['B6'].value

# 低温
m_A9=sheet['A9'].value
m_B9=sheet['B9'].value
m_B10=sheet['B10'].value

# 釜ヒータ1漏電
m_A13=sheet['A13'].value
m_B13=sheet['B13'].value
m_B14=sheet['B14'].value

# 釜ヒータ2漏電
m_A18=sheet['A18'].value
m_B18=sheet['B18'].value
m_B19=sheet['B19'].value
from multiprocessing import Process
import asyncio
import threading
potSensorDisorderAlert_flg =False
potSensorOverTempAlert_flg = False
potSensorUnderTempAlert_flg =False
potHeaterOneTempAlert_flg = False
potHeaterTwoTempAlert_flg = False
log_file_name = "異常ログ.txt"

Base = declarative_base()
engine = create_engine('sqlite:///db.sqlite3', echo=False)
Session = sessionmaker(bind=engine)
session = Session()
 


class User(Base):
       __tablename__='plc_info'
       id= Column('id',Integer,primary_key=True)
       name=Column('name',String)
       ip_address=Column('ip_address',String)
       port=Column('port',Integer)


#データベースアップデート
def ip_info_update(id,name,ip_address,port):
    #row = session.query(User).filter_by(id=1).one()
    row = session.query(User).filter_by(id=id).one()
    row.name =name
    row.ip_address=ip_address
    row.port=port
    session.add(row)
    session.commit()
    # 例文
    #ip_info_update(id=1,name='釜A',ip_address='192.168.0.10',port=9600)



def temp_data_insert():
       users = session.query(User.id, User.name, User.ip_address, User.port).all()
       print(users)


##########################################################
## 20/05/11 釜温度等の取得データをデータベースに追記する
"""
class DataBase_A(Base):
       __tablename__='DataBase_A'
       id= Column('id',Integer,primary_key=True)
       name=Column('name',String)
       date=Column('data',String)
       time=Column('time',String)
       temp=Column('temp',Integer)
       on_count=Column('on_count',Integer)
"""
class DataBase_A(Base):
       __tablename__='DataBase'
       id= Column('id',Integer,primary_key=True)
       name=Column('name',String)
       date=Column('date',String)
       time=Column('time',String)
       temp=Column('temp',Integer)
       in_temp=Column('in_temp',Integer)
       in_hum=Column('in_hum',Integer)
       on_count=Column('on_count',Integer)


##########
# 20/05/13 作成関数
def data_insert(return_data):#return_dataにはfins_read_A()等タプル化し引数
    #db_A=DataBase_A()
    data_list=[return_data]#中身はタプル
    #temp_data = [{'data':d[0],'time':d[1],'temp':d[2],'on_count':d[3] } for d in data_list]
    temp_data = [{'id':d[0],'name':d[1],'data':d[2],'time':d[3],'temp':d[4],'on_count':d[5]} for d in data_list]
    session.execute(DataBase_A.__table__.insert(),temp_data)
    session.commit()
# 20/05/13
##########

"""
def data_base_insert_A(id,name,date,time,temp,on_count):
       _add=DataBase_A(id=id,name=name,date=date,time=time,temp=temp,on_count=on_count)
       session.add(_add)
       session.commit()
"""
# 20/06/11 室内温度湿度を追加したDB対応の追記
def data_base_insert_A(id,name,date,time,temp,in_temp,in_hum,on_count):
       _add=DataBase_A(
              id = id,
              name = name,
              date = date,
              time = time,
              temp = temp,
              in_temp = in_temp,
              in_hum = in_hum,
              on_count = on_count)
       session.add(_add)
       session.commit()

# 削除処理
def database_A_delete(id):
    row = session.query(DataBase_A).filter_by(id=id).one()
    session.delete(row)
    session.commit()

#database_A_delete(id=1)
    
db_flg_A = True
db_flg_A = False


def button_push_A():
       #ax1=fig.add_subplot(2,2,2)
       global ax1
       ax1=plt.subplot2grid((1,1),(0,0),colspan=2)
       #ax1 = fig.add_subplot(111)
       #ax1=plt.plot()
       #ax1.set_title('釜温度推移')

       global ax2
       #ax2=plt.subplot2grid((2,2),(1,0),colspan=2)
       #ax2.set_title('リレー時間')
       #ax2.set_xlabel('リレー数')
       #キャンバスの生成
       global Canvas
       Canvas = FigureCanvasTkAgg(fig, master=data_frm)
       Canvas.get_tk_widget().grid(row=1, column=1)#, rowspan=10)

       data_base_select_tree_view(pot_name="A")
       grap(Canvas,ax1)
       #grap2(Canvas,ax2)
       
       
def data_base_select_tree_view(pot_name):
       global table_frm
       global db_flg_A
       """ not flag managed
       if(db_flg_A == False):
              db_flg_A = True
       else:
              db_flg_A = False
       """
       table_frm.grid_forget()
       table_name="釜A"
       table_frm=tkinter.Frame(data_frm,background=color_type)
       table_frm.grid(row=1,column=0,padx=10)
       tree=ttk.Treeview(table_frm,height=20)
       tree["columns"]=(1,2,3,4,5)
       tree["show"]="headings"
       tree.column(1,width=80)
       tree.column(2,width=75)
       tree.column(3,width=50)
       tree.column(4,width=60)
       tree.column(5,width=60)
       #tree.column(6,width=50)
       tree.heading(1,text="日付")
       tree.heading(2,text="時刻")
       tree.heading(3,text="釜温度")
       tree.heading(4,text="室内温度")
       tree.heading(5,text="室内湿度")
       #tree.heading(6,text="リレー数")#リレー回数は載せない
       global date_select_A_list
       global temp_select_A_list
       global on_count_select_A_list
       global days_select_A_list
       date_select_A_list = []
       tmpe_select_A_list = []
       days_select_A_list = []
       if(db_flg_A == False):
              aaa = session.query(
                     DataBase_A.date,
                     DataBase_A.time,
                     DataBase_A.temp,
                     DataBase_A.in_temp,
                     DataBase_A.in_hum
                     #DataBase_A.on_count#リレーを消して室内温度・湿度を入れる
                     ).filter(DataBase_A.name==pot_name).order_by(DataBase_A.id.desc()).all()
              days_select_A = session.query(
                     DataBase_A.date
                     ).filter(DataBase_A.name == pot_name).order_by(DataBase_A.id.desc()).all()
              date_select_A = session.query(
                     DataBase_A.time
                     ).filter(DataBase_A.name==pot_name).order_by(DataBase_A.id.desc()).all()
              temp_select_A = session.query(
                     DataBase_A.temp
                     ).filter(DataBase_A.name==pot_name).order_by(DataBase_A.id.desc()).all()
              on_count_select_A = session.query(
                     DataBase_A.on_count
                     ).filter(DataBase_A.name==pot_name).order_by(DataBase_A.id.desc()).all()
       else:
              aaa = session.query(DataBase_A.date,DataBase_A.time,DataBase_A.temp,DataBase_A.on_count).filter(DataBase_A.name=="A").all()
              #aaa = session.query(DataBase_A.date,DataBase_A.time,DataBase_A.temp).filter(DataBase_A.name=="A").all()
              date_select_A = session.query(DataBase_A.time).filter(DataBase_A.name=="A").all()
              temp_select_A = session.query(DataBase_A.temp).filter(DataBase_A.name=="A").all()
              on_count_select_A = session.query(DataBase_A.on_count).filter(DataBase_A.name=="A").all()
       tree_count = 0
       starttttt = time.time()
       days_select_A_list = [list(i)[0] for i in days_select_A]
       days_select_A_list = [x for x in set(days_select_A_list) if days_select_A_list.count(x) > 1]
       #days_select_A_list = [x for x in days_select_A_list if days_select_A_list.count(x) > 1]
       global days_select_A_list_sort
       global days_differ_list
       days_select_A_list_sort=sorted(days_select_A_list)
       #print('days_select_A_list_sort : ',days_select_A_list_sort)
       print(time.time()-starttttt)
       starttttt = time.time()
       days_differ_list = []
              
       try:
              for i in days_select_A_list_sort:
                     days_differ = session.query(
                            func.max(DataBase_A.on_count)
                            ).filter_by(name = pot_name,date =i).order_by(DataBase_A.id.desc()).all()
                     days_differ_list.append(days_differ)
       except:
              return
       print(555,time.time()-starttttt)

       starttttt = time.time()
       # 日別リスト
       days_differ_list = [list(i)[0] for i in days_differ_list]
       days_differ_list = [list(i)[0] for i in days_differ_list]
       date_select_A_list = [list(i)[0] for i in date_select_A]
       temp_select_A_list = [list(i)[0] for i in temp_select_A]
       on_count_select_A_list = [list(i)[0] for i in on_count_select_A]
       for i in aaa:
              tree_count += 1
              if(tree_count % 2 ==1):
                     tree.insert('','end',values = i,tags=('oddrow',))
              else:
                     tree.insert('','end',values = i)
                     
       #テーブル
       #global data_frm
       global data_pdf_name
       if(pot_name=='A'):
              data_frm["text"]="釜A温度調節器データ"
              data_pdf_name = '釜A'
       elif(pot_name=='B'):
              data_frm["text"]="釜B温度調節器データ"
              data_pdf_name = '釜B'
       elif(pot_name=='C'):
              data_frm["text"]="釜C温度調節器データ"
              data_pdf_name = '釜C'
       elif(pot_name=='D'):
              data_frm["text"]="釜D温度調節器データ"
              data_pdf_name = '釜D'
       tree.grid(row=0,padx=5,pady=5,ipady=5)
       style.configure("Treeview.headings",font=(font_type,tree_font_size+2))
       style.configure("Treeview",font=(font_type,tree_font_size))
       #tree.tag_configure('oddrow',background='#dcd6d9')
       y_bar = ttk.Scrollbar(table_frm,orient=VERTICAL,command=tree.yview)
       x_bar = ttk.Scrollbar(table_frm,orient=HORIZONTAL,command=tree.xview)
       tree['yscrollcommand'] = y_bar.set
       tree['xscrollcommand'] = x_bar.set
       y_bar.grid(row=0,column=1,sticky=NS)
       x_bar.grid(row=1,column=0,sticky=EW)
       print(666,time.time()-starttttt)




## 20/05/13 再開予定
############################################################

# 読取間隔用データベース
class Interval(Base):
       __tablename__='interval'
       id=Column('id',Integer,primary_key=True)
       interval=Column('interval',Integer)
# 読取間隔アップデート
def interval_update(interval):
    interval_up = session.query(Interval).filter(Interval.id==1).first()
    interval_up.interval=interval
    session.commit()
def interval_updates():
       #data_reader()
       interval_update(interval=interval_ent.get())

def name_update(id,name_ent):
       user_name=session.query(User).filter(User.id==id).first()
       user_name.name=name_ent
       session.commit()

# 削除処理
def ip_address_delete(id):
    row = session.query(User).filter_by(id=id).one()
    session.delete(row)
    session.commit()

# データベース追記

def ip_address_insert(name,ip_address,port):
    _add = User(name=name, ip_address=ip_address, port=9600)
    session.add(_add)
    session.commit()

def set_ip_address():
       # A
       A_ip=state_A_IP_ent.get()
       A_port=state_A_port_ent.get()
       A_name=A_lbl
       ip_info_update(id=1,name=A_name,ip_address=A_ip,port=A_port)
       # B
       B_ip=state_B_IP_ent.get()
       B_port=state_B_port_ent.get()
       B_name=B_lbl
       ip_info_update(id=2,name=B_name,ip_address=B_ip,port=B_port)
       # C
       C_ip=state_C_IP_ent.get()
       C_port=state_C_port_ent.get()
       C_name=C_lbl
       ip_info_update(id=3,name=C_name,ip_address=C_ip,port=C_port)
       # D
       D_ip=state_D_IP_ent.get()
       D_port=state_D_port_ent.get()
       D_name=D_lbl
       ip_info_update(id=4,name=D_name,ip_address=D_ip,port=D_port)
       # E
       E_ip=state_E_IP_ent.get()
       E_port=state_E_port_ent.get()
       ip_info_update(id=5,name='温湿度E',ip_address=E_ip,port=E_port)

#IPアドレス読込
def ip_data_read(id):
       user=session.query(User).get(id)
       name=user.name
       ip=user.ip_address
       port=user.port
       return name,ip,port
def interval_data_read():
       inter=session.query(Interval).get(1)
       _inter=inter.interval
       return _inter
              
def name_update(id,name_ent):
       user_name=session.query(User).filter(User.id==id).first()
       user_name.name=name_ent
       session.commit()
def name_updates():
       name_update(id=1,name_ent=another_A_name_ent.get())
       name_update(id=2,name_ent=another_B_name_ent.get())
       name_update(id=3,name_ent=another_C_name_ent.get())
       name_update(id=4,name_ent=another_D_name_ent.get())
       global pot_A_frm
       global pot_B_frm
       global pot_C_frm
       global pot_D_frm
       global pot_A_lbl
       global pot_B_lbl
       global pot_C_lbl
       global pot_D_lbl
       A_lbl,b,c=ip_data_read(id=1)
       B_lbl,b,c=ip_data_read(id=2)
       C_lbl,b,c=ip_data_read(id=3)
       D_lbl,b,c=ip_data_read(id=4)
       pot_A_lbl.grid_forget()
       pot_B_lbl.grid_forget()
       pot_C_lbl.grid_forget()
       pot_D_lbl.grid_forget()
       pot_A_lbl=tkinter.Label(pot_A_frm,text=A_lbl,bg=color_type,font=("",font_size))
       pot_A_lbl.grid(row=1,column=0,columnspan=2)
       pot_B_lbl=tkinter.Label(pot_B_frm,text=B_lbl,bg=color_type,font=("",font_size))
       pot_B_lbl.grid(row=1,column=0,columnspan=2)
       pot_C_lbl=tkinter.Label(pot_C_frm,text=C_lbl,bg=color_type,font=("",font_size))
       pot_C_lbl.grid(row=1,column=0,columnspan=2)
       pot_D_lbl=tkinter.Label(pot_D_frm,text=D_lbl,bg=color_type,font=("",font_size))
       pot_D_lbl.grid(row=1,column=0,columnspan=2)




btn_color_alert = "red"
btn_color_normal = "gray93"
btn_color_alert_flg = False
def btn_color_change(id):
       global pot_A_btn
       global pot_B_btn
       global pot_C_btn
       global pot_D_btn
       global btn_color_alert_flg
       #not flag managed
       if(btn_color_alert_flg == False):
              if(id == 1):
                     pot_A_btn["bg"] = btn_color_normal
              elif(id == 2):
                     pot_B_btn["bg"] = btn_color_normal
              elif(id == 3):
                     pot_C_btn["bg"] = btn_color_normal
              elif(id == 4):
                     pot_D_btn["bg"] = btn_color_normal
       else:
              if(id == 1):
                     pot_A_btn["bg"] = btn_color_alert
              elif(id == 2):
                     pot_B_btn["bg"] = btn_color_alert
              elif(id == 3):
                     pot_C_btn["bg"] = btn_color_alert
              elif(id == 4):
                     pot_D_btn["bg"] = btn_color_alert
graf_range = 50
def grap(canvas,ax,colors="red"):
       global data_frm
       global main_page
       changePage(main_page)
       ax.cla()#前の描画データの消去
       if(data_frm["text"] == "釜A温度調節器データ"):
              #ax.set_title('釜A温度推移')
              ax.set_title(pot_A_lbl.cget("text")+'釜温度データ')#入力保存されたラベル名からタイトルを入れる
       elif(data_frm["text"] == "釜B温度調節器データ"):
              ax.set_title('釜B温度推移')
       elif(data_frm["text"] == "釜C温度調節器データ"):
              ax.set_title('釜C温度推移')
       elif(data_frm["text"] == "釜D温度調節器データ"):
              ax.set_title('釜D温度推移')
       x = date_select_A_list[:graf_range]
       x.reverse()
       y = temp_select_A_list[:graf_range]
       y.reverse()
       ax.plot(x,y, marker='.')
       ax.tick_params(labelsize=5.5,axis='x', rotation=-300)
       #plt.xticks(y, rotation=90)
       ax.grid(True)
       
       ### 20/05/15
       ##try:
       ##       grap2(Canvas,ax2)
       ### 20/05/14
       ##except:
       ##       pass
       #Data indicater from DataBase_A(desc and asc)
       
       try:
              current_val,target_val,alert_over,alert_under,onoff_count=fins_read_A()
              alert_over=target_val+alert_over
              alert_under=target_val-alert_under
              
              current_val=str(current_val/10)+'℃'#送られてくる数値に小数点がないため
              target_temp_A=str(target_val/10)+"℃"
              alert_over_temp_A=str(alert_over/10)+"℃"
              alert_under_temp_A=str(alert_under/10)+"℃"
              print(alert_under_temp_A)
              global pot_A_ent
              pot_A_ent.delete(0,END)
              pot_A_ent.insert(END,current_val)
              global pot_A_over_st_ent
              pot_A_set_st_ent.delete(0,END)
              pot_A_set_st_ent.insert(END,target_temp_A)
              global pot_A_over_st_ent
              pot_A_over_st_ent.delete(0,END)
              pot_A_over_st_ent.insert(END,alert_over_temp_A)
              global pot_A_under_st_ent
              pot_A_under_st_ent.delete(0,END)
              pot_A_under_st_ent.insert(END,alert_under_temp_A)
       except:
              print("error")
              return
       canvas.draw()
       
graf_on_count_range = 20
def grap2(canvas,ax,colors="red"):
       
       global data_frm
       global days_select_A_list_sort
       global days_differ_list
       #x = date_select_A_list[:graf_on_count_range]
       x = days_select_A_list_sort[:graf_on_count_range]
       #x.reverse()
       #y = on_count_select_A_list[:graf_on_count_range]
       y = days_differ_list[:graf_on_count_range]
       grap2_count = 0
       z =[]
       # if elseで内包表記のメリットは微妙　→　可読性重視
       for i in x:
              if(grap2_count == 0):
                     z.append(i + '(' + str(y[grap2_count]) + ')')
                     #z.append(i)
              else:
                     z.append(i + '(前日+' + str(y[grap2_count] - y[grap2_count - 1]) + ')')
              grap2_count +=1

       #y.reverse()
       ax.cla()#前の描画データの消去
       ax.set_xlabel('リレー回数')
       ax.bar(z,y,width = 0.5,log = False)
       #ax.tick_params(labelsize=6,axis='x', rotation=-300)
       ax.tick_params(labelsize=6,axis='x')
       ax.grid(True,alpha = 0.8 ,)
       canvas.draw()
       
def grap3(canvas,ax,colors="red"):
       global data_frm
       data_frm["text"]="釜C温度調節器データ"
       ax.cla()#前の描画データの消去
       ax.bar(x[-20:],y_r_2[-20:])
       ax.tick_params(labelsize=6,axis='x', rotation=-300)
       ax.grid(True)
       ax.set_xlabel('リレー数')
       canvas.draw()


def hex_change(num):
    if(type(num)==str):
        num_int=int(num)
    else:
        num_int=num
    num=hex(num_int)
    num=num[2:4]
    if(num_int<=15):
        num='0'+num
    return num
def hex_change_points(num):
    if(type(num)==str):
        num_int=int(num)
    else:
        num_int=num
    num=hex(num_int)
    #data=data[2:4]
    if(num_int<=15):
        num='000'+num[2:]
    if(num_int<=255 and num_int>15):
        num='00'+num[2:]
    if(num_int>255 and num_int<=4095):
        data='0'+data[2:]
    if(num_int>4095 and num_int<=65535):
        num=num[2:]
    return num
def hex_change_data(data):
    if(type(data)==str):
        data_int=int(data)
    else:
        data_int=data
    data=hex(data_int)
    #data=data[2:4]
    if(data_int<=15):
        data='000'+data[2:]+'00'#語尾の00はビット指定の時に用いるためチャネルでは00固定
    if(data_int<=255 and data_int>15):
        data='00'+data[2:]+'00'
    if(data_int>255 and data_int<=4095):
        data='0'+data[2:]+'00'
    if(data_int>4095 and data_int<=65535):
        data=data[2:]+'00'
    return data
    

def changePage(page):
    page.tkraise()


def Quit():
       root.quit()
       root.destroy()
def datetime_XX(datetime):
       if(datetime<10):
              re_datetime = '0'+str(datetime)
       else:
              re_datetime = str(datetime)
       return re_datetime


def fins_read_temp_and_hum():
       # 室内温度湿度のPLCに対してFINS通信を試みる
       # D1501:室内温度
       # D1502:室内湿度
       temp_amd_hum_name,temp_and_hum_ip,temp_and_hum_port=ip_data_read(5)
       temp_and_hum_ip_split=temp_and_hum_ip.split('.')
       da1=temp_and_hum_ip_split[3]
       temp_and_hum_port=int(temp_and_hum_port)
       #data='82'+hex_change_data(data=0)+hex_change_points(num=16)
       data='82'+hex_change_data(data=1501) +\
              '82' + hex_change_data(data=1502) 
       try:
              fins=Fins(
                     ip = temp_and_hum_ip,
                     port = temp_and_hum_port,
                     dna = 0,
                     da1 = da1,
                     sna = 0,
                     sa1 = 195,
                     data = data)
       except:
              return
       try:
              return_data=fins.socket_0104()
              return_data[0] = int(hex(return_data[0])[2:])
              return_data[1] = int(hex(return_data[1])[2:])
              #print("室内温度湿度データを表示する",return_data)


       except:
              return
       return return_data



def fins_read_A():
       # 釜AのPLCに対してFINS通信を試みる
       # 0104 複数読出し
       # D0007:現在値
       # D0008:目標値
       # D0011:警報値１(上限警報)
       # D0012:警報値２(待機下限警報シーケンス)
       # D0110:ON/OFF制御リレー回数
       ## 20/06/10 変更
       # 各釜に対しての現在値等のアドレスを変更する
       # D1500:現在値
       # D1501:設定値
       # D1502:警報値１
       # D1503:警報値２
       # D110:ON/OFF制御リレー回数
       A_name,A_ip,A_port=ip_data_read(1)
       A_ip_split=A_ip.split('.')
       da1=A_ip_split[3]
       A_port=int(A_port)
       #data='82'+hex_change_data(data=0)+hex_change_points(num=16)
       data='82'+hex_change_data(data=1500) +\
              '82' + hex_change_data(data=1501) +\
                     '82' + hex_change_data(data=1502) +\
                            '82' + hex_change_data(data=1503) +\
                                   '82' + hex_change_data(data=110)#+'30'+hex_change_points(0)+hex_change(4)
       #fins=Fins(ip='192.168.0.190',port=9600,dna=0,da1=190,sna=0,sa1=195,data=data)
       try:
              fins=Fins(ip=A_ip,port=A_port,dna=0,da1=da1,sna=0,sa1=195,data = data)
       except:
              raise
              return
       try:
              return_data=fins.socket_0104()
              return_data[0] = int(hex(return_data[0])[2:])
              #print(200610,return_data)


       except:
              raise
              return
       return return_data

def fins_read_bit_A():
       # 0.00:警報上限ON
       # 0.01:警報下限ON
       # 0.02:漏電１ON
       # 0.03:漏電２ON
       # 0.04:出力制御
       A_name,A_ip,A_port=ip_data_read(1)
       A_ip_split=A_ip.split('.')
       da1=A_ip_split[3]
       A_port=int(A_port)
       data='30'+hex_change_points(0)+hex_change(0)+\
             '30'+hex_change_points(0)+hex_change(1)+\
             '30'+hex_change_points(0)+hex_change(2)+\
             '30'+hex_change_points(0)+hex_change(3)+\
             '30'+hex_change_points(0)+hex_change(4)
       fins=Fins(ip=A_ip,port=A_port,dna=0,da1=da1,sna=0,sa1=195,data=data)
       try:
              return_data=fins.socket_0104_bit()
       except:
              raise
              return
       return return_data


import time
data_reader_start=0
data_read_time_start = 0
data_read_time_start_count = 0
updata_interval = 60# 60秒経てば画面が更新
updata_start_time = time.time()
updata_timer_read_time = time.time()
def data_reader():
       global data_reader_start
       if(round(time.time()-data_reader_start,2)>86400):
              pass
       else:
              print(round(time.time()-data_reader_start,2))
       data_reader_start=time.time()
       global root
       global interval_num
       global data_reader_count
       interval_num=interval_data_read()
       if(type(interval_num)==str):
              interval_num=int(interval_num)
       #print(interval_num)
       data_read_A_bit()# 常時監視するためにおく
       global data_read_time_start_count
       if(data_read_time_start_count == 0):# 初回は必ず読み取るために行う
              data_read_temp_and_hum()
              data_read_A()
              data_read_time_start_count = 1
       global updata_timer_read_time
       updata_timer_read = time.time() - updata_timer_read_time
       if(updata_timer_read > interval_num):# 設定された時間を超えた場合にデータを読み取る
              data_read_temp_and_hum()
              data_read_A()
              updata_timer_read_time = time.time()
       #data_read_time_start = time.time()

       global updata_start_time
       updata_timer = time.time() - updata_start_time
       if(updata_timer > updata_interval):
              button_push_A()
              updata_start_time = time.time()
       else:
              pass
       #root.after(interval_num*1000,data_reader)
       root.after(1000,data_reader)
       

def log_btn_click():
       global btn_color_alert_flg
       subprocess.Popen(log_file_name,shell = True)
       btn_color_alert_flg = False
       btn_color_change(id = 1)
       

def potSensorDisorderAlert():
    global potSensorDisorderAlert_flg
    potSensorDisorderAlert_flg =True# フラグ管理により、異常発生時の重複表示をさける
    messagebox.showinfo(m_A1, m_B1+'\n'+m_B2)
    potSensorDisorderAlert_flg =False
    return
def potSensorOverTempAlert():
    global potSensorOverTempAlert_flg
    potSensorOverTempAlert_flg = True
    messagebox.showinfo(m_A5, m_B5+'\n'+m_B6)
    potSensorOverTempAlert_flg = False
    return
def potSensorUnderTempAlert():
    global potSensorUnderTempAlert_flg
    potSensorUnderTempAlert_flg = True
    messagebox.showinfo(m_A9, m_B9+'\n'+m_B10)
    potSensorUnderTempAlert_flg = False
    return
def potHeaterOneTempAlert():
    global potHeaterOneTempAlert_flg
    potHeaterOneTempAlert_flg = True
    messagebox.showinfo(m_A13, m_B13+'\n'+m_B14)
    potHeaterOneTempAlert_flg =False
    return
def potHeaterTwoTempAlert():
    global potHeaterTwoTempAlert_flg
    potHeaterTwoTempAlert_flg =True
    messagebox.showinfo(m_A18, m_B18+'\n'+m_B19)
    potHeaterTwoTempAlert_flg =False
    return
data_read_A_count=0



def data_read_A_bit():
       global data_read_A_count
       global btn_color_alert_flg
       dt=datetime.now()
       date=str(dt.year)[2:4]+'/'+datetime_XX(dt.month)+'/'+datetime_XX(dt.day)
       time=datetime_XX(dt.hour)+':'+datetime_XX(dt.minute)+':'+datetime_XX(dt.second)
       try:
              alert_bit_list = fins_read_bit_A()
              alret_over_bit,alert_under_bit,leak_1,leak_2,onoff_bit= alert_bit_list
              #print(alret_over_bit,alert_under_bit,leak_1,leak_2,onoff_bit)
       except:
              print("BIT")
              return
       
       if(1 in alert_bit_list[0:4]):
              btn_color_alert_flg = True
              btn_color_change(id = 1)
              if(alret_over_bit == 1):
                     with open(log_file_name,mode = 'a')as f:
                            f.write("[釜A]"+date+" "+time + '：警報上限値を超えました\n')
                     if(potSensorOverTempAlert_flg ==True):
                            pass
                     else:
                            thread = threading.Thread(target=potSensorOverTempAlert)
                            thread.start()
              if(alert_under_bit == 1):
                     
                     with open("異常ログ.txt",mode = 'a')as f:
                            f.write("[釜A]"+date+" "+time + '：警報下限値を下回りました\n')
                     if(potSensorUnderTempAlert_flg == True):
                            pass
                     else:
                            thread = threading.Thread(target=potSensorUnderTempAlert)
                            thread.start()
                     
              if(leak_1 == 1):
                     with open("異常ログ.txt",mode = 'a')as f:
                            f.write("[釜A]"+date+" "+time + '：ヒータ１で漏電が起こりました\n')
                     if(potHeaterOneTempAlert_flg == True):
                            pass
                     else:
                            thread = threading.Thread(target=potHeaterOneTempAlert)
                            thread.start()
              if(leak_2 == 1):
                     with open("異常ログ.txt",mode = 'a')as f:
                            f.write("[釜A]"+date+" "+time + '：ヒータ２で漏電が起こりました\n')
                     if(potHeaterTwoTempAlert_flg == True):
                            pass
                     else:
                            thread = threading.Thread(target=potHeaterTwoTempAlert)
                            thread.start()

       else:
              pass

def data_read_temp_and_hum():
       global in_temp_val,in_hum_val
       try:
              in_temp_data,in_hum_data=fins_read_temp_and_hum()
              in_temp_val = in_temp_data/10
              in_hum_val = in_hum_data/10
       except:
              print("in temp and hum data retad")
              #raise
              return
       in_temp_val_str=str(in_temp_val)+'℃'
       in_hum_val_str=str(in_hum_val)+"%"
       # 200611 以下に室内温度湿度の文字を記入させる
       global factory_temp,factory_hum
       factory_temp.delete(0,END)
       factory_temp.insert(END,in_temp_val_str)
       factory_hum.delete(0,END)
       factory_hum.insert(END,in_hum_val_str)

def data_read_A():
       global data_read_A_count
       global btn_color_alert_flg
       global in_temp_val,in_temp_val
       dt=datetime.now()
       date=str(dt.year)[2:4]+'/'+datetime_XX(dt.month)+'/'+datetime_XX(dt.day)
       time=datetime_XX(dt.hour)+':'+datetime_XX(dt.minute)+':'+datetime_XX(dt.second)
       try:
              current_val,target_val,alert_over,alert_under,onoff_count=fins_read_A()
              # この周辺に室内温度・湿度のデータを取得する関数を用意する 20/05/25
              current_val = current_val/10
              target_val = target_val/10
              alert_over = alert_over/10
              alert_under = alert_under/10
       except:
              print("data_retad")
              #raise
              return
       dbrows = session.query(DataBase_A).count() + 1
       name = 'A'
       tuple_fins=(dbrows,name,date,time,current_val,in_temp_val,in_hum_val,onoff_count)
       print('追記内容 : ',tuple_fins)
       #data_insert(tuple_fins)# 20/05/13
       try:
              #print(dbrows,'\n',name,'\n',date,'\n',time,'\n',current_val,'\n',onoff_count)
              #data_base_insert_A(id=dbrows,name=name,date=date,time=time,temp=current_val,on_count=onoff_count)
              # 200611 DBに室内温度湿度も追加した場合の関数
              data_base_insert_A(id = dbrows,name = name,date = date,time = time,temp = current_val,in_temp = in_temp_val,in_hum = in_hum_val,on_count = onoff_count)
       except:
              print("data_insert a")
              raise
              return
       alert_over=target_val+alert_over
       alert_under=target_val-alert_under
       current_val=str(current_val)+'℃'
       target_temp_A=str(target_val)+"℃"
       alert_over_temp_A=str(alert_over)+"℃"
       alert_under_temp_A=str(alert_under)+"℃"
       global pot_A_ent
       pot_A_ent.delete(0,END)
       pot_A_ent.insert(END,current_val)
       global pot_A_set_st_ent
       pot_A_set_st_ent.delete(0,END)
       pot_A_set_st_ent.insert(END,target_temp_A)
       global pot_A_over_st_ent
       pot_A_over_st_ent.delete(0,END)
       pot_A_over_st_ent.insert(END,alert_over_temp_A)
       global pot_A_under_st_ent
       pot_A_under_st_ent.delete(0,END)
       pot_A_under_st_ent.insert(END,alert_under_temp_A)

def make_pdf_file():
       global data_pdf_name
       dt=datetime.now()
       pdf_date=str(dt.year)[2:4]+'_'+datetime_XX(dt.month)+'_'+datetime_XX(dt.day)+'_'+datetime_XX(dt.hour)
       data_pdf_name = pdf_date + data_pdf_name
       pdf_name = data_pdf_name + '.pdf'
       

       plt.savefig(pdf_name, transparent=True, bbox_inches = 'tight', pad_inches = 0)

def pdf_save(x,y,save_name):
       plt.title(save_name)
       plt.grid(True)
       plt.plot(x,y)
       plt.savefig(save_name, transparent=True,bbox_inches = 'tight', pad_inches = 0)


def data_file_selected(event):
       global data_file_var
       aaa = data_file_var.get()
       #print(aaa)
def data_input_name_selected(event):
       global data_input_name_var
       bbb = data_input_name_var.get()
       print(bbb)

def data_file_selected_1(event):
       global data_file_range_var_1
       aaa = data_file_range_var_1.get()
       #print(days_select_A_list_sort.index(aaa),'番目')
       
       print(aaa)
def data_file_selected_2(event):
       global data_file_range_var_2
       bbb = data_file_range_var_2.get()
       #print(days_select_A_list_sort.index(aaa),'番目')
def data_file_ranges_click():
       global data_file_var
       global data_file_range_var_1
       global data_file_range_var_2
       global data_file_select_range_2
       get_put_number = data_file_var.get()# 取得対象の釜取得
       aaa = data_file_range_var_1.get()# 取得対象期間の開始日取得
       bbb = data_file_range_var_2.get()# 取得対象期間の終了日取得
       # 取得の範囲
       if(one_or_range_var.get()==0):
              ccc = days_select_A_list_sort[days_select_A_list_sort.index(aaa)]
       else:
              ccc = days_select_A_list_sort[days_select_A_list_sort.index(aaa):days_select_A_list_sort.index(bbb) + 1]
       print(ccc)

def data_file_one_and_range_rd_click():
       global data_file_select_range_2
       if(one_or_range_var.get()==0):
              data_file_select_range_2.config(state = 'disabled')
       else:
              data_file_select_range_2.config(state = 'normal')
              
def file_format_click(event):
       global temp_only_rd
       global relay_only_rd
       global temp_and_relay_rd
       global data_file_range_rd
       if(file_format_var.get() == 'CSV'):
              pdf_data_time_cmd.config(state = 'disabled')
              temp_only_rd.config(state = 'disabled')
              relay_only_rd.config(state = 'disabled')
              temp_and_relay_rd.config(state = 'disabled')
              data_file_range_rd.config(state='normal')
       else:
              pdf_data_time_cmd.config(state = 'normal')
              temp_only_rd.config(state = 'normal')
              relay_only_rd.config(state = 'normal')
              temp_and_relay_rd.config(state = 'normal')
              data_file_range_rd.config(state='disabled')


#配列内にあるものが何番目にあるのかを探る関数
def counter_time(_list,word):
    count = 0
    for i in _list:
        if(i.startswith(word) == True):
            return count
        
        count += 1

       
def data_file_output_click():
       global data_file_var
       global data_file_range_var_1
       global data_file_range_var_2
       global data_file_select_range_2
       global file_name_ent
       get_put_number = data_file_var.get()# 取得対象の釜取得
       aaa = data_file_range_var_1.get()# 取得対象期間の開始日取得
       bbb = data_file_range_var_2.get()# 取得対象期間の終了日取得
       if(file_format_var.get() == "CSV"):
              # 取得の範囲
              import csv
              days_differ_list = []
              if(one_or_range_var.get()==0):
                     ccc = days_select_A_list_sort[days_select_A_list_sort.index(aaa)]
                     try:
                            days_differ_list = session.query(
                                   DataBase_A.date,
                                   DataBase_A.time,
                                   DataBase_A.temp,
                                   DataBase_A.in_temp,
                                   DataBase_A.in_hum,
                                   DataBase_A.on_count
                                   ).filter_by(name = get_put_number,date = ccc).order_by(DataBase_A.id.asc()).all()
                            days_differ_list = [list(i) for i in days_differ_list]

                     except:
                            return
              else:
                     ccc = days_select_A_list_sort[days_select_A_list_sort.index(aaa):days_select_A_list_sort.index(bbb) + 1]
                     
                     try:
                            for i in ccc:
                                   days_differ = session.query(
                                          DataBase_A.date,
                                          DataBase_A.time,
                                          DataBase_A.temp,
                                          DataBase_A.in_temp,
                                          DataBase_A.in_hum,
                                          DataBase_A.on_count
                                          ).filter_by(name = get_put_number,date = i).order_by(DataBase_A.id.asc()).all()
                                   days_differ_list.append(days_differ)
                            days_differ_list = [[j for j in i] for i in days_differ_list]
                            days_differ_list_2 =[]
                            for i in range(len(days_differ_list)):
                                   days_differ_list_2.extend(days_differ_list[i])
                            days_differ_list = days_differ_list_2
                     except:
                            print('aaa')
                            return
              header = ['年月日','時間','温度','工場内温度','工場内湿度','リレー回数']
              output_data_file=file_name_ent.get()+'.csv'
              
              with open(output_data_file,mode = 'w')as f:
                     writer = csv.writer(f,lineterminator ='\n')
                     writer.writerow(header)
                     writer.writerows(days_differ_list)
       else:# PDF
              datetime_list =[]
              date_select_A_list = []
              time_select_A_list = []
              temp_select_A_list = []
              on_count_select_A_list = []
              date_select_A_list_2 =[]
              time_select_A_list_2 =[]
              temp_select_A_list_2 =[]
              on_count_select_A_list_2 = []
              if(one_or_range_var.get()==0):# or 1):
                     ccc = days_select_A_list_sort[days_select_A_list_sort.index(aaa)]
                     date_select_A = session.query(
                            DataBase_A.date
                            ).filter_by(name = get_put_number,date = ccc).order_by(DataBase_A.id.asc()).all()
                     time_select_A = session.query(
                            DataBase_A.time
                            ).filter_by(name = get_put_number,date = ccc).order_by(DataBase_A.id.asc()).all()
                     temp_select_A = session.query(
                            DataBase_A.temp
                            ).filter_by(name = get_put_number,date = ccc).order_by(DataBase_A.id.asc()).all()
                     # is this no mean?
                     on_count_select_A = session.query(
                            DataBase_A.on_count
                            ).filter_by(name = get_put_number,date = ccc).order_by(DataBase_A.id.asc()).all()
                     date_select_A_list_2=[list(ii)[0] for ii in date_select_A]
                     date_select_A_list.extend(date_select_A_list_2)
                     time_select_A_list_2=[list(ii2)[0] for ii2 in time_select_A]
                     time_select_A_list.extend(time_select_A_list_2)
                     temp_select_A_list_2=[list(ii3)[0] for ii3 in temp_select_A]
                     temp_select_A_list.extend(temp_select_A_list_2)
                     on_count_select_A_list_2=[list(ii4)[0] for ii4 in on_count_select_A]
                     on_count_select_A_list.extend(on_count_select_A_list_2)
                     for i in range(len(date_select_A_list)):
                            # 年月日と時間の配列を１つにする
                            # こちらのデータと温度を
                            #datetime_list.append(date_select_A_list[i]+'_'+time_select_A_list[i])#年月日と時間文字列の結合
                            datetime_list.append(time_select_A_list[i])#時間文字列のみ
                     
                     print(date_select_A_list[0:4])
                     print()
                     print(date_select_A_list[0:5])
              
              else:# こちらは使えないようにしている
                     ccc = days_select_A_list_sort[days_select_A_list_sort.index(aaa):days_select_A_list_sort.index(bbb) + 1]  
                     try:
                            for i in ccc:
                                   date_select_A = session.query(
                                          DataBase_A.date
                                          ).filter_by(name = get_put_number,date = i).order_by(DataBase_A.id.asc()).all()
                                   # 各配列に同じようなプログラムがあるが配列内タプルを消している
                                   date_select_A_list_2=[list(ii)[0] for ii in date_select_A]
                                   date_select_A_list.extend(date_select_A_list_2)
                                   
                                   time_select_A = session.query(
                                          DataBase_A.time
                                          ).filter_by(name = get_put_number,date = i).order_by(DataBase_A.id.asc()).all()
                                   time_select_A_list_2=[list(ii2)[0] for ii2 in time_select_A]
                                   time_select_A_list.extend(time_select_A_list_2)
                                   
                                   temp_select_A = session.query(
                                          DataBase_A.temp
                                          ).filter_by(name = get_put_number,date = i).order_by(DataBase_A.id.asc()).all()
                                   temp_select_A_list_2=[list(ii3)[0] for ii3 in temp_select_A]
                                   temp_select_A_list.extend(temp_select_A_list_2)
                            for i in range(len(date_select_A_list)):
                                   datetime_list.append(time_select_A_list[i])#時間文字列のみ
                            print(datetime_list[0:10])

                     except:
                            print('aaa')
                            return
              save_name = file_name_ent.get() + '.pdf'
              select_word = times_tuple_var.get()
              print(select_word,type(select_word))
              global temp_or_and_relay_var
              if(temp_or_and_relay_var.get() == 0):
                     #指定した時間から始まる
                     try:
                            if(type(int(select_word)) == int):
                                   print("int")
                                   pdf_data_start_time = counter_time(_list=datetime_list,word = select_word)
                                   enter_datetime = datetime_list[pdf_data_start_time:pdf_data_start_time+60]
                                   enter_temp=temp_select_A_list[pdf_data_start_time:pdf_data_start_time+60]
                            else:
                                   enter_temp=temp_select_A_list[:60]
                                   enter_datetime=datetime_list[:60]
                     except:
                            return
                     
                     global ax5
                     ax5 = plt.subplot2grid((1,1),(0,0))
                     ax5.plot(x=enter_temp,y=enter_datetime)
                     ax5.tick_params(labelsize=5.5,axis='x', rotation=-300)
              if(temp_or_and_relay_var.get() == 1):
                     print(9)
                     print(date_select_A_list_2)
                     date_select_A_list = [x for x in set(date_select_A_list_2) if date_select_A_list_2.count(x) > 1]
                     date_select_A_list_sort=sorted(date_select_A_list)
                     print(date_select_A_list_sort)
                     days_differ_list = []
                     try:
                            for i in date_select_A_list_sort:
                                   days_differ = session.query(
                                          func.max(DataBase_A.on_count)
                                          ).filter_by(name = get_put_number,date =i).order_by(DataBase_A.id.asc()).all()
                                   days_differ_list.append(days_differ)
                                   print('a')
                     except:
                            raise
                            return
              
                     days_differ_list = [list(i)[0] for i in days_differ_list]
                     days_differ_list = [list(i)[0] for i in days_differ_list]
                     enter_temp = days_select_A_list_sort[:graf_on_count_range]
                     enter_datetime = days_differ_list[:graf_on_count_range]
                     print(enter_datetime)
                     grap2_count = 0
                     
                     for i in enter_temp:
                            if(grap2_count == 0):
                                   enter_datetime.append(i + '(' + str(enter_datetime[grap2_count]) + ')')
                            else:
                                   enter_datetime.append(i + '(前日+' + str(enter_datetime[grap2_count] - enter_datetime[grap2_count - 1]) + ')')
                            grap2_count += 1
                     #global ax5
                     ax5.set_xlabel('リレー回数')
                     ax5.bar(x=enter_temp,y=enter_datetime,width = 0.5,log = False)
                     ax5.tick_params(labelsize=6,axis='x')
                     
                     
              #save_name = date_select_A_list + select_word +'.pdf'
              #キャンバスの生成
              global Canvas
              Canvas = FigureCanvasTkAgg(fig, master=data_frm)
              Canvas.get_tk_widget().grid(row=1, column=1)#, rowspan=10)
              pdf_save(x=enter_datetime,y=enter_temp,save_name=save_name)
              # 20/05/20
              # PDF保存ファイルの修正を行っていく
       

def main():
    global root
    global data_frm
    global main_page
    global state_page
    try:
       current_val_A,target_val_A,alert_over_A,alert_under_A,onoff_count=fins_read_A()
       alert_over_A=target_val_A+alert_over_A
       alert_under_A=target_val_A-alert_under_A
       current_temp_A=str(current_val_A/10)+"℃"#送られてくる数値に小数点がないため/10
       target_temp_A=str(target_val_A/10)+"℃"
       alert_over_temp_A=str(alert_over_A/10)+"℃"
       alert_under_temp_A=str(alert_under_A/10)+"℃"   
    except:
       pass
       #raise
       #return


    try:
        #GUIの生成
        root = tkinter.Tk()
        root.title("サンプル温度調節器データ管理ソフト")
        root.geometry('1260x680')
        root.minsize(500,300)
        root.configure(bg=bg_color_type)
        root.state('zoomed')#windows
        #root.attributes("-zoomed", "1")#linux
        global style
        style=ttk.Style()
        main_page=tkinter.Frame(root,bg=color_type)
        main_page.grid(row=0,column=0,sticky=(N,W,S,E))
        main_page.columnconfigure(0,weight=1)
        main_page.rowconfigure(0,weight=1)
        state_page=tkinter.Frame(root,bg=color_type)
        state_page.grid(row=0,column=0,sticky=(N,W,S,E))
        state_page.columnconfigure(0,weight=1)
        state_page.rowconfigure(0,weight=1)
        
        main_page.tkraise()
        
        ## tab
        nb=ttk.Notebook(main_page,width=1500,height=700)
        s=ttk.Style()
        s.configure("TNotebook",background=color_type)
        #style.theme_use('clam')
        
        tab0=tkinter.LabelFrame(nb,font=(font_type,tree_font_size),bg=color_type)
        tab1=tkinter.LabelFrame(nb,font=(font_type,tree_font_size+10),bg=color_type)
        tab2=tkinter.LabelFrame(nb,font=(font_type,tree_font_size),bg=color_type)
        tab3=tkinter.LabelFrame(nb,font=(font_type,tree_font_size),bg=color_type)
        tab4=tkinter.LabelFrame(nb,font=(font_type,tree_font_size),bg=color_type)
        nb.add(tab0,text='データ表示',padding=3)
        nb.add(tab4,text='データ出力',padding=3)
        nb.add(tab1,text='釜設定確認',padding=3)
        #nb.add(tab2,text='IPアドレス',padding=3)
        nb.add(tab3,text='設定',padding=3)
        
        nb.grid(row=1,column=0,columnspan=3)

        data_frm=tkinter.LabelFrame(tab0,text="かま",bg=color_type,font=(font_type,tree_font_size+2,'bold'))
        data_frm.grid(row=1,column=0)#,padx=10)

        #グラフの設定
        global fig
        fig=plt.figure(figsize=(10,5))
        fig.patch.set_facecolor(graph_color_type)  # 図全体の背景色
        fig.patch.set_alpha(1.0)  # 図全体の背景透明度
        # 図の大枠
        #plt.rcParams["figure.figsize"] = [6.4,4.0]  # 図の縦横のサイズ([横(inch),縦(inch)])
        plt.rcParams["figure.dpi"] = 300            # dpi(dots per inch)
        plt.rcParams["figure.autolayout"] = False   # レイアウトの自動調整を利用するかどうか
        plt.rcParams["figure.subplot.left"] = 0.00  # 余白
        plt.rcParams["figure.subplot.bottom"] = 0.00# 余白
        plt.rcParams["figure.subplot.right"] =0.00  # 余白
        plt.rcParams["figure.subplot.top"] = 0.00   # 余白
        plt.rcParams["figure.subplot.wspace"] = 0.00# 図が複数枚ある時の左右との余白
        plt.rcParams["figure.subplot.hspace"] = 0.10# 図が複数枚ある時の上下との余白
        #plt.rcParams["font.family"] = "serif"       # 使用するフォント
        plt.rcParams["mathtext.cal"] = "serif"      # TeX表記に関するフォント設定
        plt.rcParams["mathtext.rm"] = "serif"       # TeX表記に関するフォント設定
        plt.rcParams["mathtext.it"] = "serif:italic"# TeX表記に関するフォント設定
        plt.rcParams["mathtext.bf"] = "serif:bold"  # TeX表記に関するフォント設定
        plt.rcParams["mathtext.fontset"] = "cm"     # TeX表記に関するフォント設定
        #plt.rcParams['font.family'] = 'Times New Roman'
        plt.rcParams['font.size'] = 10  # 適当に必要なサイズに
        plt.rcParams['xtick.direction'] = 'in'  # in or out
        plt.rcParams['ytick.direction'] = 'in'
        plt.rcParams["xtick.top"] = False            # 上部に目盛り線を描くかどうか
        plt.rcParams["xtick.bottom"] = False         # 下部に目盛り線を描くかどうか
        plt.rcParams["ytick.left"] = False           # 左部に目盛り線を描くかどうか
        plt.rcParams["ytick.right"] = False          # 右部に目盛り線を描くかどうか
        plt.rcParams["xtick.major.size"] = 0.01      # x軸主目盛り線の長さ
        plt.rcParams["ytick.major.size"] = 5.00      # y軸主目盛り線の長さ
        plt.rcParams["xtick.major.width"] = 1.0     # x軸主目盛り線の線幅
        plt.rcParams["ytick.major.width"] = 1.0     # y軸主目盛り線の線幅
        plt.rcParams["xtick.minor.visible"] = True # x軸副目盛り線を描くかどうか
        plt.rcParams["ytick.minor.visible"] = True # y軸副目盛り線を描くかどうか
        plt.rcParams["xtick.minor.size"] = 1.0      # x軸副目盛り線の長さ
        plt.rcParams["ytick.minor.size"] = 1.0      # y軸副目盛り線の長さ
        plt.rcParams["xtick.minor.width"] = 1.0    # x軸副目盛り線の線幅
        plt.rcParams["ytick.minor.width"] = 1.0     # y軸副目盛り線の線幅
        plt.rcParams["xtick.labelsize"] = 12        # 目盛りのフォントサイズ
        plt.rcParams["ytick.labelsize"] = 12        # 目盛りのフォントサイズ
        
        plt.rcParams['axes.xmargin'] = 0.00
        plt.rcParams['axes.ymargin'] = 0.50
        plt.rcParams["legend.fancybox"] = False  # 丸角OFF
        plt.rcParams["legend.framealpha"] = 0  # 透明度の指定、0で塗りつぶしなし
        plt.rcParams["legend.edgecolor"] = 'black'  # edgeの色を変更
        plt.gca().yaxis.set_major_formatter(plt.FormatStrFormatter('%.1f'))#y軸小数点以下3桁表示
        #plt.locator_params(axis='y',nbins=10)#y軸，10個以内．
        #plt.gca().yaxis.set_tick_params(which='both', direction='in',bottom=True, top=True, left=True, right=True)
        #plt.contour(X, Y, Z, cmap='viridis') # viridisの配色で等高線を描く
        plt.axis("off")
        


        #ax1=fig.add_subplot(2,2,2)
        global ax1
        #ax1=plt.subplot2grid((1,1),(0,0),colspan=2)
        #ax1 = fig.add_subplot(1,1,1)
        ax1 =plt.plot()
        #ax1.set_title('釜温度推移')

        global ax2
        #ax2=plt.subplot2grid((2,2),(1,0),colspan=2)
        #ax2.set_title('リレー時間')
        #ax2.set_xlabel('リレー数')

        #global ax3
        #ax3=plt.subplot2grid((1,1),(0,0))
        #ax3.set_title('リレー数')
        #ax3.set_xlabel('リレー数')

        #キャンバスの生成
        global Canvas
        Canvas = FigureCanvasTkAgg(fig, master=data_frm)
        Canvas.get_tk_widget().grid(row=1, column=1)#, rowspan=10)
        #lalal=tkinter.Label(data_frm,text='momomomo')
        #lalal.grid(row=1,column=2)

        
        #テーブル
        
        global table_frm
        table_name="釜A"
        table_frm=tkinter.Frame(data_frm,background=color_type)
        table_frm.grid(row=1,column=0,padx=10)

        ## 関数の方で表示を行っているためコメントアウト
##        tree=ttk.Treeview(table_frm,height=20)
##        tree["columns"]=(1,2,3,4,5)
##        tree["show"]="headings"
##        tree.column(1,width=80)
##        tree.column(2,width=70)
##        tree.column(3,width=50)
##        tree.column(4,width=60)
##        tree.column(5,width=60)
##        #tree.column(6,width=50)
##        tree.heading(1,text="日付")
##        tree.heading(2,text="時刻")
##        tree.heading(3,text="釜温度")
##        tree.heading(4,text="室内温度")
##        tree.heading(5,text="室内湿度")
##        #tree.heading(6,text="リレー数")
##
##        tree.grid(row=0,padx=5,pady=5,ipady=5)
##        style.configure("Treeview.headings",font=(font_type,tree_font_size+2))
##        style.configure("Treeview",font=(font_type,tree_font_size-2))
##        #tree.tag_configure('oddrow',background='#dcd6d9')
##        y_bar = ttk.Scrollbar(table_frm,orient=VERTICAL,command=tree.yview)
##        x_bar = ttk.Scrollbar(table_frm,orient=HORIZONTAL,command=tree.xview)
##        tree['yscrollcommand'] = y_bar.set
##        tree['xscrollcommand'] = x_bar.set
##        y_bar.grid(row=0,column=1,sticky=NS)
##        x_bar.grid(row=1,column=0,sticky=EW)

        
        
        

        # 各釜温度一覧
        base_frm=tkinter.Frame(main_page,bg=color_type,relief=relief_type,borderwidth=2)
        base_frm.grid(row=0,column=0,padx=10,pady=20,sticky=tkinter.N)


        # データベースより読出し
        A_name,A_ip,A_port=ip_data_read(1)
        B_name,B_ip,B_port=ip_data_read(2)
        C_name,C_ip,C_port=ip_data_read(3)
        D_name,D_ip,D_port=ip_data_read(4)
        E_name,E_ip,E_port=ip_data_read(5)
        
        # 釜A 現在
        global A_lbl
        A_lbl=A_name
        global pot_A_frm
        global pot_A_lbl
        global pot_A_btn
        pot_A_frm=tkinter.Frame(base_frm,bg=color_type,relief=relief_type,borderwidth=1)
        pot_A_frm.grid(row=0,column=0)
        #pot_A_btn = tkinter.Button(pot_A_frm,text="釜A",font=(font_type,font_size),width=btn_width_size,command=partial(grap, Canvas, ax1))#ボタンの生成button_push_A()
        pot_A_btn = tkinter.Button(pot_A_frm,text="釜A",font=(font_type,font_size),width=btn_width_size,command=button_push_A)#ボタンの生成
        pot_A_btn.grid(row=0, column=0,columnspan=2)#描画位置(テキトー)
        pot_A_lbl=tkinter.Label(pot_A_frm,text=A_lbl,font=("",font_size),bg=color_type)
        pot_A_lbl.grid(row=1,column=0,columnspan=2)#,sticky=tkinter.E)
        pot_A_ent_lbl=tkinter.Label(pot_A_frm,text="温度",font=("",font_size),bg=color_type)
        pot_A_ent_lbl.grid(row=2,column=0)
        global pot_A_ent
        pot_A_ent=tkinter.Entry(pot_A_frm,width=7,font=("",font_size))
        pot_A_ent.grid(row=2,column=1)
        try:
               pot_A_ent.insert(END,current_temp_A)
        except:
              pass
       
        
        
        # 釜B 現在
        global B_lbl
        global pot_B_lbl
        B_lbl=B_name
        global pot_B_frm
        pot_B_frm=tkinter.Frame(base_frm,bg=color_type,relief=relief_type,borderwidth=1)
        pot_B_frm.grid(row=0,column=1)
        pot_B_btn = tkinter.Button(pot_B_frm,text="釜B",font=("",font_size),width=btn_width_size, command=partial(grap, Canvas, ax1))#ボタンの生成
        pot_B_btn.grid(row=0, column=0,columnspan=2)#描画位置(テキトー)
        pot_B_lbl=tkinter.Label(pot_B_frm,text=B_lbl,bg=color_type,font=("",font_size))
        pot_B_lbl.grid(row=1,column=0,columnspan=2)
        pot_B_ent_lbl=tkinter.Label(pot_B_frm,text="温度",font=("",font_size),bg=color_type)
        pot_B_ent_lbl.grid(row=2,column=0)
        pot_B_ent=tkinter.Entry(pot_B_frm,width=7,font=("",font_size))
        pot_B_ent.grid(row=2,column=1)
        pot_B_ent.insert(END,"480.0"+"℃")
        
        # 釜C 現在
        global C_lbl
        global pot_C_lbl
        C_lbl=C_name
        global pot_C_frm
        pot_C_frm=tkinter.Frame(base_frm,bg=color_type,relief=relief_type,borderwidth=1)
        pot_C_frm.grid(row=0,column=2)
        pot_C_btn = tkinter.Button(pot_C_frm,text="釜C",width=btn_width_size,font=("",font_size),command=partial(grap, Canvas, ax1))#ボタンの生成# 本来はgrap3であったが変更した
        pot_C_btn.grid(row=0, column=0,columnspan=2)#描画位置(テキトー)
        pot_C_lbl=tkinter.Label(pot_C_frm,text=C_lbl,bg=color_type,font=("",font_size))
        pot_C_lbl.grid(row=1,column=0,columnspan=2)
        pot_C_ent_lbl=tkinter.Label(pot_C_frm,text="温度",font=("",font_size),bg=color_type)
        pot_C_ent_lbl.grid(row=2,column=0)
        pot_C_ent=tkinter.Entry(pot_C_frm,width=7,font=("",font_size))
        pot_C_ent.grid(row=2,column=1)
        pot_C_ent.insert(END,"480.0"+"℃")

        # 釜D 現在
        global D_lbl
        global pot_D_lbl
        D_lbl=D_name
        global pot_D_frm
        pot_D_frm=tkinter.Frame(base_frm,bg=color_type,relief=relief_type,borderwidth=1)
        pot_D_frm.grid(row=0,column=3)
        pot_D_btn = tkinter.Button(pot_D_frm,text="釜D",font=("",font_size),width=btn_width_size,command=partial(grap, Canvas, ax1))#ボタンの生成
        pot_D_btn.grid(row=0, column=0,columnspan=2)
        pot_D_lbl=tkinter.Label(pot_D_frm,text=D_lbl,bg=color_type,font=("",font_size))
        pot_D_lbl.grid(row=1,column=0,columnspan=2)
        pot_D_ent_lbl=tkinter.Label(pot_D_frm,text="温度",font=("",font_size),bg=color_type)
        pot_D_ent_lbl.grid(row=2,column=0)
        pot_D_ent=tkinter.Entry(pot_D_frm,width=7,font=("",15))
        pot_D_ent.grid(row=2,column=1)
        pot_D_ent.insert(END,"480.0"+"℃")

        
        #室内温度湿度
        # temp
        global factory_temp,factory_hum
        temp_frm=tkinter.Frame(base_frm,bg=color_type,relief=relief_type,borderwidth=1)
        temp_frm.grid(row=0,column=4)
        factory_temp_btn=tkinter.Button(temp_frm,text="工場内温湿度",font=("",font_size))
        factory_temp_btn.grid(row=0,column=0,columnspan=2)
        factory_temp_lbl=tkinter.Label(temp_frm,text="温度",bg=color_type,font=("",font_size))
        factory_temp_lbl.grid(row=1,column=0)
        factory_temp=tkinter.Entry(temp_frm,font=("",font_size),width=6)
        factory_temp.grid(row=1,column=1)
        factory_temp.insert(END,"25.0"+"℃")
        # hum
        factory_hum_lbl=tkinter.Label(temp_frm,text="湿度",bg=color_type,font=("",font_size))
        factory_hum_lbl.grid(row=2,column=0)
        factory_hum=tkinter.Entry(temp_frm,width=6,font=("",font_size))
        factory_hum.grid(row=2,column=1)#,sticky=tkinter.E)
        factory_hum.insert(END,"50"+"％")

        # file
        # log
        # PDF
        global log_file_frm
        global file_btn
        global pdf_btn
        global log_btn
        log_file_frm = tkinter.Frame(base_frm,bg = color_type,relief = relief_type,borderwidth = 1)
        log_file_frm.grid(row = 0,column = 5,sticky = tkinter.N)
        file_btn = tkinter.Button(log_file_frm,text = "データ出力",font=("",font_size - 2))
        #file_btn.grid(row = 0,column = 0,sticky = tkinter.E + tkinter.W)
        pdf_btn = tkinter.Button(log_file_frm,text = "PDF",font=("",font_size - 3),command = make_pdf_file)
        #pdf_btn.grid(row = 1,column = 0,sticky = tkinter.E + tkinter.W)
        log_btn = tkinter.Button(log_file_frm,text = "釜異常ログ",width = 10,font=("",font_size),command = log_btn_click)
        log_btn.grid(row = 2,column = 0,sticky = tkinter.E + tkinter.W)
        
        
        #DrawCanvas(Canvas,ax1)
        #DrawCanvas1(Canvas,ax2)
        #grap(Canvas,ax3)#グラフが初期から描写される

        ###############
        # 設定　ページ#
        ###############


        #　設定

        # 設定　フレームA
        # 釜温度設定 tab1

       
        pot_A_set_frm=tkinter.LabelFrame(tab1,text="釜A　設定",font=(font_type,font_size),bg=color_type)
        pot_A_set_frm.grid(row=0,column=0)
        pot_A_set_st_btn=tkinter.Label(pot_A_set_frm,text="設定",font=(font_type,font_size),bg=color_type,relief='flat')
        pot_A_set_st_btn.grid(row=0,column=0)
        global pot_A_set_st_ent
        pot_A_set_st_ent=tkinter.Entry(pot_A_set_frm,width=7,font=(font_type,font_size))
        pot_A_set_st_ent.grid(row=0,column=1,sticky=tkinter.E)
        global pot_A_over_st_ent
        try:
               pot_A_set_st_ent.delete(0,END)
               pot_A_set_st_ent.insert(END,target_temp_A)
               print(target_temp_A)
        except:
               print("asasa")
               pass
        # 上限
        try:
               pot_A_over_st_btn=tkinter.Button(pot_A_set_frm,text="上限",font=(font_type,font_size),bg=color_type,relief='flat')
               pot_A_over_st_btn.grid(row=1,column=0)
               pot_A_over_st_ent=tkinter.Entry(pot_A_set_frm,width=7,font=(font_type,font_size))
               pot_A_over_st_ent.grid(row=1,column=1)
               pot_A_over_st_ent.insert(END,alert_over_temp_A)
        except:
               pass
        # 下限
        try:
               pot_A_under_st_btn=tkinter.Button(pot_A_set_frm,text="下限",font=(font_type,font_size),bg=color_type,relief='flat')
               pot_A_under_st_btn.grid(row=2,column=0)
               global pot_A_under_st_ent
               pot_A_under_st_ent=tkinter.Entry(pot_A_set_frm,width=7,font=(font_type,font_size))
               pot_A_under_st_ent.grid(row=2,column=1)
               #global pot_A_under_st_ent
               pot_A_under_st_ent.insert(END,alert_under_temp_A)
        except:
               pass
        # IPアドレス tab3
        global state_A_IP_ent
        global state_A_port_ent
        state_IP_frm=tkinter.LabelFrame(tab3,text='IPアドレス',font=(font_type,tree_font_size),bg=color_type)
        state_IP_frm.grid(row=2,column=0,sticky=tkinter.W)
        state_A_IP_frm=tkinter.LabelFrame(state_IP_frm,text="釜A",font=(font_type,tree_font_size),bg=color_type)
        state_A_IP_frm.grid(row=0,column=0)
        state_A_IP=tkinter.Label(state_A_IP_frm,text="IPアドレス",font=(font_type,tree_font_size),bg=color_type)
        state_A_IP.grid(row=0,column=0)
        state_A_IP_ent=tkinter.Entry(state_A_IP_frm,width=width_size,font=(font_type,tree_font_size))
        state_A_IP_ent.grid(row=0,column=1)
        state_A_port=tkinter.Label(state_A_IP_frm,text="ポート",font=(font_type,tree_font_size),bg=color_type)
        state_A_port.grid(row=1,column=0)
        state_A_port_ent=tkinter.Entry(state_A_IP_frm,width=width_size,font=(font_type,tree_font_size))
        state_A_port_ent.grid(row=1,column=1)
        #A_name,A_ip,A_port=ip_data_read(1)

        state_A_IP_ent.delete(0,END)
        state_A_IP_ent.insert(END,A_ip)
        state_A_port_ent.delete(0,END)
        state_A_port_ent.insert(END,A_port)
        # another tab3
        global another_A_name_ent

        # 設定変更を行うフレーム
        another_frm = tkinter.LabelFrame(tab3,text="釜名",font=(font_type,tree_font_size),bg=color_type)
        another_frm.grid(row=0,column =0,sticky=tkinter.W)
        
        another_A_frm=tkinter.LabelFrame(another_frm,text="釜A",font=(font_type,tree_font_size),bg=color_type)
        another_A_frm.grid(row=0,column=0)
        another_A_name=tkinter.Label(another_A_frm,text="客先",font=(font_type,tree_font_size),bg=color_type)
        another_A_name.grid(row=0,column=0)
        another_A_name_ent=tkinter.Entry(another_A_frm,width=width_size,font=(font_type,tree_font_size))
        another_A_name_ent.grid(row=0,column=1)
        another_A_name_ent.delete(0,END)
        another_A_name_ent.insert(END,A_name)
        #another_A_name=tkinter.Label(state_A_IP_frm,text="ポート",font=(font_type,tree_font_size),bg=color_type)
        #state_A_port.grid(row=1,column=0)
        #state_A_port_ent=tkinter.Entry(state_A_IP_frm,width=width_size,font=(font_type,tree_font_size))
        #state_A_port_ent.grid(row=1,column=1)
        
        # 設定　フレームB
        # 釜温度設定 tab1
        pot_B_set_frm=tkinter.LabelFrame(tab1,text="釜B　設定",font=(font_type,font_size),bg=color_type)
        pot_B_set_frm.grid(row=0,column=1)
        pot_B_set_st_btn=tkinter.Label(pot_B_set_frm,text="設定",font=(font_type,font_size),bg=color_type,relief='flat')
        pot_B_set_st_btn.grid(row=0,column=0)
        pot_B_set_st_ent=tkinter.Entry(pot_B_set_frm,width=7,font=(font_type,font_size))
        pot_B_set_st_ent.grid(row=0,column=1,sticky=tkinter.E)
        pot_B_set_st_ent.insert(END,"480.0"+"℃")
        # 上限
        pot_B_over_st_btn=tkinter.Button(pot_B_set_frm,text="上限",font=(font_type,font_size),bg=color_type,relief='flat')
        pot_B_over_st_btn.grid(row=1,column=0)
        pot_B_over_st_ent=tkinter.Entry(pot_B_set_frm,width=7,font=(font_type,font_size))
        pot_B_over_st_ent.grid(row=1,column=1)
        pot_B_over_st_ent.insert(END,"500.0"+"℃")
        # 下限
        pot_B_under_st_btn=tkinter.Button(pot_B_set_frm,text="下限",font=(font_type,font_size),bg=color_type,relief='flat')
        pot_B_under_st_btn.grid(row=2,column=0)
        pot_B_under_st_ent=tkinter.Entry(pot_B_set_frm,width=7,font=(font_type,font_size))
        pot_B_under_st_ent.grid(row=2,column=1)
        pot_B_under_st_ent.insert(END,"430.0"+"℃")
        # IPアドレス tab3
        global state_B_IP_ent
        global state_B_port_ent
        state_B_IP_frm=tkinter.LabelFrame(state_IP_frm,font=(font_type,tree_font_size),bg=color_type)
        state_B_IP_frm.grid(row=0,column=1)
        state_B_IP_frm["text"]="釜B"
        state_B_IP=tkinter.Label(state_B_IP_frm,text="IPアドレス",font=(font_type,tree_font_size),bg=color_type)
        state_B_IP.grid(row=0,column=0)
        state_B_IP_ent=tkinter.Entry(state_B_IP_frm,width=width_size,font=(font_type,tree_font_size))
        state_B_IP_ent.grid(row=0,column=1)
        state_B_port=tkinter.Label(state_B_IP_frm,text="ポート",font=(font_type,tree_font_size),bg=color_type)
        state_B_port.grid(row=1,column=0)
        state_B_port_ent=tkinter.Entry(state_B_IP_frm,width=width_size,font=(font_type,tree_font_size))
        state_B_port_ent.grid(row=1,column=1)
        #B_name,B_ip,B_port=ip_data_read(2)

        state_B_IP_ent.delete(0,END)
        state_B_IP_ent.insert(END,B_ip)
        state_B_port_ent.delete(0,END)
        state_B_port_ent.insert(END,B_port)

        # another tab3
        global another_B_name_ent
        another_B_frm=tkinter.LabelFrame(another_frm,text="釜B",font=(font_type,tree_font_size),bg=color_type)
        another_B_frm.grid(row=0,column=1)
        another_B_name=tkinter.Label(another_B_frm,text="客先",font=(font_type,tree_font_size),bg=color_type)
        another_B_name.grid(row=0,column=0)
        another_B_name_ent=tkinter.Entry(another_B_frm,width=width_size,font=(font_type,tree_font_size))
        another_B_name_ent.grid(row=0,column=1)
        another_B_name_ent.delete(0,END)
        another_B_name_ent.insert(END,B_name)

        
        # 設定　フレームC
        # 釜温度設定 tab1
        pot_C_set_frm=tkinter.LabelFrame(tab1,text="釜C　設定",font=(font_type,font_size),bg=color_type)
        pot_C_set_frm.grid(row=0,column=2)
        pot_C_set_st_btn=tkinter.Label(pot_C_set_frm,text="設定",font=(font_type,font_size),bg=color_type,relief='flat')
        pot_C_set_st_btn.grid(row=0,column=0)
        pot_C_set_st_ent=tkinter.Entry(pot_C_set_frm,width=7,font=(font_type,font_size))
        pot_C_set_st_ent.grid(row=0,column=1,sticky=tkinter.E)
        pot_C_set_st_ent.insert(END,"480.0"+"℃")
        # 上限
        pot_C_over_st_btn=tkinter.Button(pot_C_set_frm,text="上限",font=(font_type,font_size),bg=color_type,relief='flat')
        pot_C_over_st_btn.grid(row=1,column=0)
        pot_C_over_st_ent=tkinter.Entry(pot_C_set_frm,width=7,font=(font_type,font_size))
        pot_C_over_st_ent.grid(row=1,column=1)
        pot_C_over_st_ent.insert(END,"500.0"+"℃")
        # 下限
        pot_C_under_st_btn=tkinter.Button(pot_C_set_frm,text="下限",font=(font_type,font_size),bg=color_type,relief='flat')
        pot_C_under_st_btn.grid(row=2,column=0)
        pot_C_under_st_ent=tkinter.Entry(pot_C_set_frm,width=7,font=(font_type,font_size))
        pot_C_under_st_ent.grid(row=2,column=1)
        pot_C_under_st_ent.insert(END,"430.0"+"℃")
        # IPアドレス tab3
        global state_C_IP_ent
        global state_C_port_ent
        state_C_IP_frm=tkinter.LabelFrame(state_IP_frm,font=(font_type,tree_font_size),bg=color_type)
        state_C_IP_frm.grid(row=0,column=2)
        state_C_IP_frm["text"]="釜C"
        state_C_IP=tkinter.Label(state_C_IP_frm,text="IPアドレス",font=(font_type,tree_font_size),bg=color_type)
        state_C_IP.grid(row=0,column=0)
        state_C_IP_ent=tkinter.Entry(state_C_IP_frm,width=width_size,font=(font_type,tree_font_size))
        state_C_IP_ent.grid(row=0,column=1)
        state_C_port=tkinter.Label(state_C_IP_frm,text="ポート",font=(font_type,tree_font_size),bg=color_type)
        state_C_port.grid(row=1,column=0)
        state_C_port_ent=tkinter.Entry(state_C_IP_frm,width=width_size,font=(font_type,tree_font_size))
        state_C_port_ent.grid(row=1,column=1)
        #C_name,C_ip,C_port=ip_data_read(3)

        state_C_IP_ent.delete(0,END)
        state_C_IP_ent.insert(END,C_ip)
        state_C_port_ent.delete(0,END)
        state_C_port_ent.insert(END,C_port)
        # another tab3
        global another_C_name_ent
        another_C_frm=tkinter.LabelFrame(another_frm,text="釜C",font=(font_type,tree_font_size),bg=color_type)
        another_C_frm.grid(row=0,column=2)
        another_C_name=tkinter.Label(another_C_frm,text="客先",font=(font_type,tree_font_size),bg=color_type)
        another_C_name.grid(row=0,column=0)
        another_C_name_ent=tkinter.Entry(another_C_frm,width=width_size,font=(font_type,tree_font_size))
        another_C_name_ent.grid(row=0,column=1)
        another_C_name_ent.delete(0,END)
        another_C_name_ent.insert(END,C_name)


        # 設定　フレームD

        # 釜温度設定 tab1
        pot_D_set_frm=tkinter.LabelFrame(tab1,text="釜D　設定",font=(font_type,font_size),bg=color_type)
        pot_D_set_frm.grid(row=0,column=3)
        pot_D_set_st_btn=tkinter.Label(pot_D_set_frm,text="設定",font=(font_type,font_size),bg=color_type,relief='flat')
        pot_D_set_st_btn.grid(row=0,column=0)
        pot_D_set_st_ent=tkinter.Entry(pot_D_set_frm,width=7,font=(font_type,font_size))
        pot_D_set_st_ent.grid(row=0,column=1,sticky=tkinter.E)
        pot_D_set_st_ent.insert(END,"480.0"+"℃")
        # 上限
        pot_D_over_st_btn=tkinter.Button(pot_D_set_frm,text="上限",font=(font_type,font_size),bg=color_type,relief='flat')
        pot_D_over_st_btn.grid(row=1,column=0)
        pot_D_over_st_ent=tkinter.Entry(pot_D_set_frm,width=7,font=(font_type,font_size))
        pot_D_over_st_ent.grid(row=1,column=1)
        pot_D_over_st_ent.insert(END,"500.0"+"℃")
        # 下限
        pot_D_under_st_btn=tkinter.Button(pot_D_set_frm,text="下限",font=(font_type,font_size),bg=color_type,relief='flat')
        pot_D_under_st_btn.grid(row=2,column=0)
        pot_D_under_st_ent=tkinter.Entry(pot_D_set_frm,width=7,font=(font_type,font_size))
        pot_D_under_st_ent.grid(row=2,column=1)
        pot_D_under_st_ent.insert(END,"430.0"+"℃")
        # IPアドレス tab3
        global state_D_IP_ent
        global state_D_port_ent
        state_D_IP_frm=tkinter.LabelFrame(state_IP_frm,font=(font_type,tree_font_size),bg=color_type)
        state_D_IP_frm.grid(row=0,column=3)
        state_D_IP_frm["text"]="釜D"
        state_D_IP=tkinter.Label(state_D_IP_frm,text="IPアドレス",font=(font_type,tree_font_size),bg=color_type)
        state_D_IP.grid(row=0,column=0)
        state_D_IP_ent=tkinter.Entry(state_D_IP_frm,width=width_size,font=(font_type,tree_font_size))
        state_D_IP_ent.grid(row=0,column=1)
        state_D_port=tkinter.Label(state_D_IP_frm,text="ポート",font=(font_type,tree_font_size),bg=color_type)
        state_D_port.grid(row=1,column=0)
        state_D_port_ent=tkinter.Entry(state_D_IP_frm,width=width_size,font=(font_type,tree_font_size))
        state_D_port_ent.grid(row=1,column=1)
        #D_name,D_ip,D_port=ip_data_read(4)

        state_D_IP_ent.delete(0,END)
        state_D_IP_ent.insert(END,D_ip)
        state_D_port_ent.delete(0,END)
        state_D_port_ent.insert(END,D_port)

        # another tab3
        global another_D_name_ent
        another_D_frm=tkinter.LabelFrame(another_frm,text="釜D",font=(font_type,tree_font_size),bg=color_type)
        another_D_frm.grid(row=0,column=3)
        another_D_name=tkinter.Label(another_D_frm,text="客先",font=(font_type,tree_font_size),bg=color_type)
        another_D_name.grid(row=0,column=0)
        another_D_name_ent=tkinter.Entry(another_D_frm,width=width_size,font=(font_type,tree_font_size))
        another_D_name_ent.grid(row=0,column=1)
        another_D_name_ent.delete(0,END)
        another_D_name_ent.insert(END,D_name)

        # 工場内温度湿度

        # IPアドレス tab3
        global state_E_IP_ent
        global state_E_port_ent
        state_E_IP_frm=tkinter.LabelFrame(state_IP_frm,font=(font_type,tree_font_size),bg=color_type)
        state_E_IP_frm.grid(row=0,column=4)
        state_E_IP_frm["text"]="工場内温湿度"
        state_E_IP=tkinter.Label(state_E_IP_frm,text="IPアドレス",font=(font_type,tree_font_size),bg=color_type)
        state_E_IP.grid(row=0,column=0)
        state_E_IP_ent=tkinter.Entry(state_E_IP_frm,width=width_size,font=(font_type,tree_font_size))
        state_E_IP_ent.grid(row=0,column=1)
        state_E_port=tkinter.Label(state_E_IP_frm,text="ポート",font=(font_type,tree_font_size),bg=color_type)
        state_E_port.grid(row=1,column=0)
        state_E_port_ent=tkinter.Entry(state_E_IP_frm,width=width_size,font=(font_type,tree_font_size))
        state_E_port_ent.grid(row=1,column=1)
        #E_name,E_ip,E_port=ip_data_read(5)

        state_E_IP_ent.delete(0,END)
        state_E_IP_ent.insert(END,E_ip)
        state_E_port_ent.delete(0,END)
        state_E_port_ent.insert(END,E_port)

        # 保存
        state_data_btn=tkinter.Button(state_IP_frm,text="設定保存",font=(font_type,tree_font_size),command=set_ip_address)
        state_data_btn.grid(row=1,column=0,columnspan=5,pady=20)#,sticky=tkinter.E)

        # 保存
        another_data_btn=tkinter.Button(another_frm,text="設定変更",font=(font_type,tree_font_size),command=name_updates)
        another_data_btn.grid(row=1,column=0,columnspan=5,pady=20)#,sticky=tkinter.E)

        # 読取間隔
        global interval_ent
        interval_buf=interval_data_read()
        interval_frm=tkinter.LabelFrame(tab3,text='読取間隔設定',font=(font_type,tree_font_size),bg=color_type)
        interval_frm.grid(row=1,column=0,sticky=tkinter.W)
        interval_ent=tkinter.Entry(interval_frm,width=width_size-6,font=(font_type,tree_font_size))
        interval_ent.grid(row=0,column=0)
        interval_ent.delete(0,END)
        interval_ent.insert(END,interval_buf)
        interval_sec_lbl=tkinter.Label(interval_frm,text='秒',width=3,font=(font_type,tree_font_size),bg=color_type)
        interval_sec_lbl.grid(row=0,column=1)
        
        interval_data_btn=tkinter.Button(interval_frm,text="間隔変更",font=(font_type,tree_font_size),command=interval_updates)
        interval_data_btn.grid(row=1,column=0,columnspan=2,sticky=(tkinter.W,tkinter.E))

        
        data_reader()
        button_push_A()
        #plt.savefig('figname.png', transparent=True,bbox_inches = 'tight', pad_inches = 0)


        
        # tab4 データ出力
        global data_file_var
        global data_input_name_var
        global data_file_range_var_1
        global data_file_range_var_2
        global data_file_range_rd
        data_file_var = StringVar()
        data_input_name_var = StringVar()
        data_file_range_var_1 = StringVar()
        data_file_range_var_2 = StringVar()
        
        # row 0
        data_file_frm = tkinter.LabelFrame(
               tab4,
               text="データ出力",
               font=(font_type,tree_font_size),bg=color_type)
        data_file_frm.grid(row = 0,column = 0)
        data_output_select_frm =tkinter.LabelFrame(
               data_file_frm,
               text='データ出力釜選択',
               font=(font_type,tree_font_size),bg=color_type)
        data_output_select_frm.grid(row=0,column=0,sticky=tkinter.W)
        
        data_file_select_cmb = ttk.Combobox(
               data_output_select_frm,
               width = 10,
               textvariable = data_file_var,
               font=(font_type,tree_font_size))
        data_file_select_cmb.bind('<<ComboboxSelected>>',data_file_selected)
        data_file_select_cmb['values'] = ('A','B','C','D')
        data_file_select_cmb.set('A')
        data_file_select_cmb.grid(row = 0, column = 0)

        # row 1
        # DBにある入力データのフレーム
        data_input_name_frm =tkinter.LabelFrame(
               data_file_frm,
               text="入力名選択",
               font=(font_type,tree_font_size),bg=color_type)
        data_input_name_frm.grid(row = 1,column =0,sticky=tkinter.W)
        # DBにある入力データ名を表示する
        data_input_name_select_cmb = ttk.Combobox(
               data_input_name_frm,
               width = 10,
               textvariable = data_input_name_var,
               font=(font_type,tree_font_size))
        data_input_name_select_cmb.bind('<<ComboboxSelected>>',data_input_name_selected)
        #20/05/27時点で釜名となっているがデータベースからinput_nameを取得するように変更する
        # 釜名選択 →　釜名に紐づいたinput_nameをDBから出力する関数 → 'values'に送る
        data_input_name_select_cmb['values'] = ('A','B','C','D')
        data_input_name_select_cmb.set('B')
        data_input_name_select_cmb.grid(row = 0, column = 0)


        # row 3
        # Oneday or Range
        global one_or_range_var
        one_or_range_var = tkinter.IntVar()
        one_or_range_var.set(0)
        data_file_one_or_range_frm = tkinter.LabelFrame(
               data_file_frm,
               text='出力範囲',
               font=(font_type,tree_font_size),bg=color_type)
        data_file_one_or_range_frm.grid(row=3,column =0,sticky=tkinter.W)
        data_file_one_rd = tkinter.Radiobutton(
               data_file_one_or_range_frm,
               text='１日(CSV/PDF)',value = 0,variable = one_or_range_var,
               font=(font_type,tree_font_size),bg=color_type,
               command = data_file_one_and_range_rd_click)
        data_file_one_rd.grid(row = 0,column =0,columnspan=2,sticky =tkinter.W)
        
        data_file_range_rd = tkinter.Radiobutton(
               data_file_one_or_range_frm,
               text='範囲(CSVのみ)',value = 1,variable = one_or_range_var,
               font=(font_type,tree_font_size),bg=color_type,
               command = data_file_one_and_range_rd_click)
        data_file_range_rd.grid(row = 1,column =0,columnspan=2,sticky =tkinter.W)


        # 期間指定　開始
        
        data_file_select_range_1 = ttk.Combobox(
               data_file_one_or_range_frm,
               width = 10,
               textvariable = data_file_range_var_1,
               font=(font_type,tree_font_size))
        data_file_select_range_1.bind('<<ComboboxSelected>>',data_file_selected_1)
        data_file_select_range_1['values'] = tuple(days_select_A_list_sort)
        data_file_select_range_1.set(days_select_A_list_sort[-1])
        data_file_select_range_1.grid(row = 2, column = 0,sticky=tkinter.W)

        # 期間指定　終了
        
        data_range_inter = Label(data_file_one_or_range_frm,text="-",font=(font_type,tree_font_size),bg=color_type)
        data_range_inter.grid(row = 2,column = 1,sticky = tkinter.W)
        global data_file_select_range_2
        data_file_select_range_2 = ttk.Combobox(
               data_file_one_or_range_frm,
               width = 10,
               textvariable = data_file_range_var_2,
               font=(font_type,tree_font_size))
        data_file_select_range_2.bind('<<ComboboxSelected>>',data_file_selected_2)
        data_file_select_range_2['values'] = tuple(days_select_A_list_sort)
        data_file_select_range_2.set(days_select_A_list_sort[-1])
        data_file_select_range_2.grid(row = 2, column = 2,sticky=tkinter.W)
        if(one_or_range_var.get()==0):
               data_file_select_range_2.config(state = 'disabled')
        else:
               data_file_select_range_2.config(state = 'normal')
        dt=datetime.now()
        date=str(dt.year)[2:4]+datetime_XX(dt.month)+datetime_XX(dt.day)+datetime_XX(dt.hour)
        time=datetime_XX(dt.hour)+':'+datetime_XX(dt.minute)+':'+datetime_XX(dt.second)

        # row 4
        file_name_frm = tkinter.LabelFrame(
               data_file_frm,text = "出力ファイル名",
               font=(font_type,tree_font_size),bg=color_type)
        file_name_frm.grid(row = 4,column = 0,sticky =tkinter.W)
        global file_name_ent
        file_name_ent = tkinter.Entry(file_name_frm,font=(font_type,tree_font_size),width =12)
        file_name_ent.grid(row = 0,column =0)
        file_name_ent.insert(END,date)


        # row 2
        global file_format_var
        file_format_frm = tkinter.LabelFrame(
               data_file_frm,
               text = "出力形式",
               font=(font_type,tree_font_size),bg=color_type)
        file_format_frm.grid(row=2,column=0,sticky=tkinter.W)
        file_format_var = tkinter.StringVar()
        file_format_lbl = tkinter.Label(
               file_format_frm,text = "出力形式",
               font=(font_type,tree_font_size),bg=color_type)
        #file_format_lbl.grid(row = 0,column = 0,sticky =tkinter.W)
        file_format_cmb = ttk.Combobox(
               file_format_frm,
               width = 10,
               textvariable = file_format_var,
               font=(font_type,tree_font_size))
        file_format_cmb.bind('<<ComboboxSelected>>',file_format_click)
        file_format_cmb['values'] = ('CSV','PDF')
        file_format_cmb.set('CSV')
        file_format_cmb.grid(row = 1, column = 0,sticky=tkinter.W)
        if(file_format_var.get()=='PDF'):
               data_file_range_rd.config(state='disabled')
        else:
               data_file_range_rd.config(state='normal')
        # Select data var
        #None_data_lbl_1 = tkinter.Label(data_file_frm,text="　",bg=color_type)
        #None_data_lbl_1.grid(row = 6,column =0,sticky =tkinter.W)
        #None_data_lbl_2 = tkinter.Label(data_file_frm,text="　",bg=color_type)
        #None_data_lbl_2.grid(row = 7,column =0,sticky =tkinter.W)
        
        global times_tuple_var
        global pdf_data_time_cmd
        times_tuple_var =tkinter.StringVar()
        times_tuple = ("08","09","10","11","12","13","14","15","16","17","18","19","20","21")
        pdf_data_time_cmd = ttk.Combobox(
               file_format_frm,
               width = 10,
               textvariable = times_tuple_var,
               font=(font_type,tree_font_size))
        pdf_data_time_cmd.set("時間選択")
        pdf_data_time_cmd.grid(row = 2, column = 0,sticky=tkinter.W)
        #pdf_data_time_cmd.bind('<<ComboboxSelected>>',data_file_selected_1)
        pdf_data_time_cmd['values'] = times_tuple
        
        global temp_or_and_relay_var
        global temp_only_rd
        global relay_only_rd
        global temp_and_relay_rd
        temp_or_and_relay_var = tkinter.IntVar()
        temp_or_and_relay_var.set(0)
        temp_only_rd = tkinter.Radiobutton(
               file_format_frm,
               text='釜温度 + 室内温度・湿度',value = 0,variable = temp_or_and_relay_var,
               font=(font_type,tree_font_size),bg=color_type,
               command = data_file_one_and_range_rd_click)
        temp_only_rd.grid(row = 3,column =0,sticky =tkinter.W)
        relay_only_rd = tkinter.Radiobutton(
               file_format_frm,
               text='釜温度 + 室内温度',value = 1,variable = temp_or_and_relay_var,
               font=(font_type,tree_font_size),bg=color_type,
               command = data_file_one_and_range_rd_click)
        relay_only_rd.grid(row = 4,column =0,sticky =tkinter.W)
        temp_and_relay_rd = tkinter.Radiobutton(
               file_format_frm,
               text='釜温度',value = 2,variable = temp_or_and_relay_var,
               font=(font_type,tree_font_size),bg=color_type,
               command = data_file_one_and_range_rd_click)
        temp_and_relay_rd.grid(row = 5,column =0,sticky =tkinter.W)
        
        if(file_format_var.get() == 'CSV'):
               pdf_data_time_cmd.config(state = 'disabled')
               temp_only_rd.config(state = 'disabled')
               relay_only_rd.config(state = 'disabled')
               temp_and_relay_rd.config(state = 'disabled')
        else:
               pdf_data_time_cmd.config(state = 'normal')
               temp_only_rd.config(state = 'normal')
               relay_only_rd.config(state = 'normal')
               temp_and_relay_rd.config(state = 'normal')
               data_file_range_rd.config(state='disabled')


        # row 12
        data_file_output_btn = tkinter.Button(
               data_file_frm,
               text = "出力",
               width = 20,
               font=(font_type,tree_font_size),#bg=color_type,
               command = data_file_output_click)
        data_file_output_btn.grid(row = 12,column = 0,columnspan = 3)
               
        #20/05/19

        
        

        
        root.mainloop()#描画し続ける
        
    except:
        import traceback
        traceback.print_exc()
    finally:
        input(">>")#エラー吐き出したときの表示待ち

    

if __name__ == "__main__":
    main()
