import socket 
#import commands
import smtplib

s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.connect(('google.com',0))
ipAdress = s.getsockname()[0]
s.close()

content = ipAdress
mail = smtplib.SMTP('smtp.gmail.com',587)
mail.ehlo()
mail.starttls()
mail.login('baopq.spkt@gmail.com','bao0985265185')
mail.sendmail('baopq.spkt@gmail.com','baopq.spkt@gmail.com',content)
mail.close()
print("Ip:")
print(ipAdress)