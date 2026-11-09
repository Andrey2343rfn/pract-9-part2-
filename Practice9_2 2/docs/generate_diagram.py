from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
BASE=Path(__file__).resolve().parents[1]
W,H=1500,520
im=Image.new('RGB',(W,H),'#f6f9fc')
d=ImageDraw.Draw(im)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
fb=ImageFont.truetype(bold,31)
fm=ImageFont.truetype(bold,24)
fs=ImageFont.truetype(font,21)
ft=ImageFont.truetype(font,17)
d.rounded_rectangle((25,32,718,464),radius=26,fill='#e8f5f2',outline='#8dcaba',width=3)
d.rounded_rectangle((782,32,1475,464),radius=26,fill='#e9f0f9',outline='#8badcf',width=3)
d.text((55,56),'EDGE / ЛОКАЛЬНИЙ РІВЕНЬ',font=fb,fill='#17483f')
d.text((812,56),'CLOUD / АНАЛІТИКА',font=fb,fill='#254d75')

def rect(x,y,w,h,title,sub,bg,border):
 d.rounded_rectangle((x,y,x+w,y+h),radius=14,fill=bg,outline=border,width=3)
 d.text((x+16,y+13),title,font=fm,fill='#14293e')
 d.text((x+16,y+47),sub,font=fs,fill='#486175')

def arrow(x1,y1,x2,y2,color='#33637b'):
 d.line((x1,y1,x2,y2),fill=color,width=6)
 if x2>x1:d.polygon([(x2,y2),(x2-18,y2-10),(x2-18,y2+10)],fill=color)
 if x2<x1:d.polygon([(x2,y2),(x2+18,y2-10),(x2+18,y2+10)],fill=color)
rect(55,145,277,98,'SENSOR SIMULATOR','6 показників · 2 секунди','#ffffff','#b5c4d3')
rect(397,145,286,98,'EDGE PROCESSOR','Пороги · локальні дії','#ffffff','#7db5a2')
rect(397,302,286,95,'SQLite + MQTT','Буфер · повторний sync','#ffffff','#7db5a2')
rect(817,145,285,98,'CLOUD CONNECTOR','Flask REST · агрегація','#ffffff','#adc5e2')
rect(1157,145,285,98,'DASHBOARD','Графіки · команди','#ffffff','#adc5e2')
rect(817,302,285,95,'INFLUXDB','Часові ряди та історія','#ffffff','#adc5e2')
arrow(332,193,397,193)
arrow(683,193,817,193)
arrow(1102,193,1157,193)
arrow(540,243,540,302)
arrow(960,243,960,302)
d.text((326,112),'MQTT',font=ft,fill='#32667c')
d.text((708,160),'MQTT',font=ft,fill='#32667c')
d.text((1110,160),'HTTP',font=ft,fill='#32667c')
d.text((700,341),'cloud/ack',font=ft,fill='#33637b')
d.line((817,375,745,375),fill='#33637b',width=5)
d.polygon([(730,375),(750,364),(750,386)],fill='#33637b')
d.text((62,432),'Локальні рішення працюють без Cloud',font=ft,fill='#277d67')
d.text((810,432),'Оновлення даних раз на 3 секунди',font=ft,fill='#42658d')
im.save(BASE/'docs'/'architecture.png')
