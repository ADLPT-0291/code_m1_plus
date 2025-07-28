#!/usr/bin/env python3
from pyA20.gpio import gpio
from pyA20.gpio import port
from threading import Timer
from time import sleep
from apscheduler.schedulers.background import BlockingScheduler, BackgroundScheduler
from datetime import datetime, timedelta
import pytz
import time
import serial
import subprocess
import json
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import urllib
import url
import khaibao
import requests
import socket
import re
import os
import vlc
import random
import string
from urllib.parse import quote
gpio.init()
local_timezone = pytz.timezone('Asia/Ho_Chi_Minh') 
led_status = 203 #chan 7
watchdog = 20 # chan 29
led_connect = 21 # chan 31
kich_modul4g = 9 # chan 37
input_loa_L = 17 # chân 26
input_loa_R = 19 # chân 27
on_loa = 1 # chan 22 
congsuat_in = 18 # chan 28

phim_wifi = 6 # chan 12
mat_nguon = 0
mute = 2 # 13
#kich_nguon_sac = 16 # chan 18
gpio.setcfg(led_status, gpio.OUTPUT)
gpio.setcfg(watchdog, gpio.OUTPUT)
gpio.setcfg(led_connect, gpio.OUTPUT)
gpio.setcfg(kich_modul4g, gpio.OUTPUT)
gpio.setcfg(phim_wifi, gpio.INPUT)   #Configure PE11 as input
gpio.pullup(phim_wifi, gpio.PULLDOWN)    #Enable pull-down
gpio.setcfg(mat_nguon, gpio.INPUT)   #Configure PE11 as input
gpio.pullup(mat_nguon, gpio.PULLDOWN)    #Enable pull-down
gpio.output(kich_modul4g, 1)
gpio.output(watchdog, 0)
gpio.setcfg(mute, gpio.OUTPUT)

gpio.setcfg(on_loa, gpio.OUTPUT)
gpio.setcfg(input_loa_L, gpio.INPUT)   #Configure PE11 as input
gpio.pullup(input_loa_L, gpio.PULLDOWN)    #Enable pull-down
gpio.setcfg(input_loa_R, gpio.INPUT)   #Configure PE11 as input
gpio.pullup(input_loa_R, gpio.PULLDOWN)    #Enable pull-down
gpio.setcfg(congsuat_in, gpio.INPUT)   #Configure PE11 as input
gpio.pullup(congsuat_in, gpio.PULLDOWN)    #Enable pull-down
######### khai bao domain ##########
domainMqtt = url.domainMqtt
portMqtt = url.portMqtt
domainXacnhanketnoi = url.domainXacnhanketnoi
domainLogbantin = url.domainLogbantin
domainPing = url.domainPing
domainXacnhanketnoilai = url.domainXacnhanketnoilai
domainGuiLichPhat = url.domainGuiLichPhat
domainPingMatDien = url.domainPingMatDien
######## khai bao dia chi mqtt #####
id = khaibao.id
updatecode = khaibao.updatecode
trangthaiketnoi = khaibao.trangthaiketnoi
trangthaiplay = khaibao.trangthaiplay
trangthaivolume = khaibao.trangthaivolume
xacnhanketnoi = khaibao.xacnhanketnoi
dieukhienvolume = khaibao.dieukhienvolume
dieukhienplay = khaibao.dieukhienplay
yeucauguidulieu = khaibao.yeucauguidulieu
reset = khaibao.reset


####################################
MainBoard = 'M1_2024_V8.2'
phienban = "V2.3.0"
loiketnoi = 0
mabantinnhan = ''
kiemtraPlay = 0
demKiemtra = 0
data = ''
maxacthuc = ''
guidulieu = 0
ledConnectStatus = False
watchdogStatus = False
demRestartModul3g = 0
chedoRetartModul3g = False
demLoicallApiPing = 0
trangthaiguiApi = None
mangdangdung = ''
### khai bao nhap nhay wifi 
ledConnectStatus = 0
demnhapnhay = 0
demdung = 0
demnhanphim = 0
##### khai bao data do toc do mang speedtest #####
speedtest_upload = ''
speedtest_download = ''
speedtest_ping = ''
speedtest_ping_jitter = ''
### khai bao data ping ########
urldangphat = ''
tenchuongtrinh = ''
kieunguon = ''
thoiluong = ''
tennoidung = ''
diachingoidung = ''
kieuphat = ''
nguoitao = ''
taikhoantao = ''
# khai bao data api tinh #
userName = ''
password = '' 
madiaban = ''
tendiaban = ''
imel = ''
tenthietbi = ""
lat = ''
lng = ''
DichID = ''
TenDich = ''
MaNhaCungCap = ''
TenNhaCungCap = 'Gtech'
TenLoaiThietBi = 'Cụm loa truyền thanh'
NoiDungPhat = ''
TrangThaiHoatDong = 0
Status = "false"
khoaguidulieu = False
domainLoginTinh = ''
domainPingTinh = ''
domainLogTinh = ''

domainAddPlaylist = ''
domainDeletePlaylist = ''
Video = {"Index":"0", "Time": "", "MediaName": "", "AudioName": "", "Path": "", "Level": 0  }
ThoiDiemBatDau = 0
ThoiDiemKetThuc = 0
phatbantintinh = False
IdLichDangPhat = ''
DanhSachBanTinDung = []
BanTinKeTiep = []
ChuyenBanTin = False
Playing_ChuyenBai = False
IndexBanTinKeTiep = 0
PhatKhanCap = False
DataPhatKhanCap = {}
amluong = 30
LichPhatDangNhan = {}
version = "3"
TrangThaiKetNoi = '4G,-10dbm'
linkS3 = ''
ssid = "gtech-ip"
password = "123456789"
########
ChoPhatBanTinTinh = False
instance_amluong = vlc.Instance()
player_amluong = instance_amluong.media_player_new()
IdLichDangPhatNoiBo = ''
DungBanTinTinh = False
PhatBanTinNoiBo = False
Rssi = 0
TenNhaMang = None
MatDien = None
TrangThaiGuiMatDien = None
LoaiMang = ''
dbm = ''

##
file_path = 'lichphatTinh.json'
idBanTinTinhDangPhat = ''
idLichPhatTinhDangPhat = ''
thoiGianBatDauPhatTinh = None

status_loaL = 1
status_loaR = 1
status_congsuat = 1
docLoa = 0
demloi = 0

class RepeatedTimer(object):
  def __init__(self, interval, function, *args, **kwargs):
    self._timer     = None
    self.interval   = interval
    self.function   = function
    self.args       = args
    self.kwargs     = kwargs
    self.is_running = False
    self.start()
  def _run(self):
    self.is_running = False
    self.start()
    self.function(*self.args, **self.kwargs)
  def start(self):
    if not self.is_running:
      self._timer = Timer(self.interval, self._run)
      self._timer.start()
      self.is_running = True
  def stop(self):
    self._timer.cancel()
    self.is_running = False
#########
class VLCPlayer:
    def __init__(self, retries=5, delay=3):
        options = [
              '--no-xlib',
              '--no-video-title-show',
              '--no-video',
              '--play-and-exit',
              #sửa mới chỗ này ép buộc chỉ dùng alsa
              '--aout=alsa',
              '--no-ts-trust-pcr',
              '--input-fast-seek',
              '--network-caching=2000',
              '--quiet',
              '--verbose=0'
          ]
        self.instance = vlc.Instance(options)
        self.player = self.instance.media_player_new()
        self.amluong = amluong
        self.retries = retries
        self.delay = delay
    def load_media(self, path):
        media = self.instance.media_new(path)
        self.player.set_media(media)

    def play(self):
        self.player.play()
        time.sleep(1)
        self.player.audio_set_volume(self.amluong)
       
    def play_Set_Time(self, data):
        self.player.play()  
        time.sleep(2) 
        self.player.set_time(data)     
        self.player.audio_set_volume(self.amluong)
       
    def pause(self):
        self.player.set_pause(1)

    def stop(self):
        self.player.stop()
        self.player.set_media(None)

    def get_volume(self):
        return self.player.audio_get_volume()

    def set_volume(self, volume):
        # volume là giá trị từ 0 đến 100 (phần trăm)
        self.amluong = int(volume)
        self.player.audio_set_volume(int(volume))

    def get_state(self):
        state = self.player.get_state()
        if state == vlc.State.Playing:
            return "play"
        elif state == vlc.State.Paused:
            return "stop"
        elif state == vlc.State.Stopped:
            return "stop"
        elif state == vlc.State.NothingSpecial:
            return "stop"
        elif state == vlc.State.Error:
            return "Error"
        # elif state == vlc.State.Buffering:
        #     return "Error"
        # elif state == vlc.State.Opening:
        #     return "Error"
        # elif state == vlc.State.Opening:
        #     return "Error"
        else:
            return "Unknown"
        #Unknown
        #State.Opening
      
    def get_state_2(self):
        state = self.player.get_state()
        if state == vlc.State.Playing:
            return "Play"
        elif state == vlc.State.Paused:
            return "Pause"
        elif state == vlc.State.Stopped:
            return "Stop"
        elif state == vlc.State.NothingSpecial:
            return "stop"
        elif state == vlc.State.Error:
            return "Error"
        elif state == vlc.State.Buffering:
            return "Buffering"
        elif state == vlc.State.Opening:
            return "Opening"
        else:
            return "Unknown"
        #State.Opening
# kiểm tra loại kết nối mạng
def has_ipv4_address(interface):
    try:
        # Thay thế eth0 bằng tên giao diện mạng truyền vào (interface)
        output = subprocess.check_output(f"ifconfig {interface}", shell=True, universal_newlines=True)
        # Kiểm tra xem có 'inet ' trong output không (địa chỉ IPv4 bắt đầu bằng 'inet')
        if "inet " in output:
            return True
        else:
            return False
    except Exception as e:
        print(f"Lỗi kiểm tra mạng {interface}: " + str(e))
        return False

# Tính mức tín hiệu wifi
def signal_to_bars(signal):
    """Chuyển đổi mức tín hiệu thành số vạch."""
    signal = int(signal)
    if signal >= 76:
        return 4
    elif signal >= 51:
        return 3
    elif signal >= 26:
        return 2
    else:
        return 1

def parse_wifi_list(wifi_output):
    # Tách từng dòng trong kết quả
    lines = wifi_output.strip().split("\n")
    
    # Bỏ qua dòng tiêu đề
    wifi_list = []

    for line in lines[1:]:
        # Sử dụng regex để phân tích từng trường dựa trên khoảng trống
        match = re.match(r'(\*?)\s+([\w:]+)\s+(.+?)\s+(Infra|Ad-Hoc)\s+(\d+)\s+([\d\s]+Mbit/s)\s+(\d+)\s+([▂▄▆█_]+)\s+(\S+)', line)
        signal = int(match.group(7).strip())
        bars = signal_to_bars(signal)
        if match:
            wifi = {
                "IN-USE": match.group(1).strip(),
                "BSSID": match.group(2).strip(),
                "SSID": match.group(3).strip(),
                "MODE": match.group(4).strip(),
                "CHAN": match.group(5).strip(),
                "RATE": match.group(6).strip(),
                "SIGNAL": int(match.group(7).strip()),  # Chuyển đổi SIGNAL thành số nguyên
                "BARS": bars,
                "SECURITY": match.group(9).strip(),
            }
            wifi_list.append(wifi)
    
    return wifi_list


# Quét danh sách wifi hiện có trong khu vực
def get_wifi_list():
    # Chạy lệnh nmcli dev wifi
    result = subprocess.run(["nmcli", "dev", "wifi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Lấy kết quả đầu ra của lệnh
    output = result.stdout.decode()

    # Tách kết quả thành các dòng
    wifi_list = []
    lines = output.splitlines()
    # Gọi hàm và in kết quả dưới dạng JSON
    wifi_list = parse_wifi_list(output)
    return wifi_list

# Lấy danh sách các Wi-Fi có sẵn
class VLC:
    def __init__(self):
      self.TrangThaiHoatDong = TrangThaiHoatDong
      self.amluong = amluong
    #lấy trạng thái Volume
    def get_volume(self):
       return self.amluong
    
    #lấy trạng thái Play
    def get_Status_Play(self):
        return player.get_state()
    
    #play VLC
    def Play_VLC(self, data):
       # player.stop()
        print(data)
        player.load_media(data)      
        player.play()  
        self.TrangThaiHoatDong = 0

    def RePlay(self):
       # player.stop()    
        player.play()  
        self.TrangThaiHoatDong = 0

    def Play_VLC_Set_Time(self, data, ThoiGian):
       # player.stop()
        player.load_media(data)
        # Kiểm tra xem đường dẫn có chứa dấu chấm và tách phần mở rộng
        if '.' in data and data.split(".")[-1]:           
            extension = data.split(".")[-1].lower()
            # Kiểm tra xem phần mở rộng có là 'mp3' không
            if extension == "mp3":              
                player.play_Set_Time(ThoiGian)
            else:              
                player.play()
        else:
            # Nếu không có dấu chấm trong đường dẫn hoặc phần mở rộng rỗng, chạy player.play()
            player.play()
        self.TrangThaiHoatDong = 0

    #stop VLC
    def Stop_VLC(self):
        player.stop()
        # os.system("mpc stop") 
        # os.system("mpc clear")  
        self.TrangThaiHoatDong = 2

    #Tạm dừng VLC
    def Pause_VLC(self):
        player.pause()
        # os.system("mpc pause") 
        self.TrangThaiHoatDong = 1

    # set âm lượng
    def Set_Volume(self, value):
        self.amluong = int(value) 
        player.set_volume(value)
        
# gửi lệnh module Quectel
def send_command(ser, command):
    ser.write((command + '\r\n').encode('utf-8'))
    time.sleep(1)  # Chờ một chút trước khi đọc phản hồi

# đọc lệnh từ module Quectel
def read_response(ser):
    return ser.read(ser.in_waiting).decode('utf-8').strip()


# đọc mức rssi của mạng
def get_network_strength(ser):
    global LoaiMang
    try:
        # Gửi lệnh AT để lấy mức RSSI của mạng LTE
        send_command(ser, 'AT+CSQ')
        # Đọc phản hồi từ module
        response = read_response(ser)
       
        # Kiểm tra xem phản hồi có chứa thông tin RSSI không
        if '+CSQ' in response:
            try:
                #print('response', response)
                # Tách phần RSSI từ phản hồi
                rssi_str = response.split(':')[1].split(',')[0].strip()
               
                # Chuyển đổi RSSI sang dạng số nguyên
                rssi = int(rssi_str)
                LoaiMang = check_network_type(ser)
                if LoaiMang == '2G' or LoaiMang == '3G':
                    return display_signal_2g_3g(rssi)
                elif LoaiMang == 'LTE (4G)':          
                    return display_signal_lte(rssi)
                # Chuyển đổi RSSI sang mức mạng
            except (IndexError, ValueError) as e:
                # Bắt các lỗi liên quan đến việc xử lý chuỗi và chuyển đổi kiểu dữ liệu
                print("Error processing RSSI value:" + str(e))
                return None
        else:
            # Trả về None nếu không thể lấy được RSSI
            return None
    except Exception as e:
        # Bắt và xử lý các lỗi chung
        print("An error occurred:" + str(e))
        return None


def check_network_type(ser):
    try:
        # Gửi lệnh AT để lấy thông tin về mạng di động hiện tại
        ser.write(b'AT+QNWINFO\r\n')
        time.sleep(1)  # Đợi cho phản hồi
        # Đọc dữ liệu phản hồi
        response = ser.read(ser.inWaiting()).decode('utf-8')
     
        # Kiểm tra xem mạng là 3G hay LTE
       # Kiểm tra và trả về loại mạng
        if "GSM" in response or "GPRS" in response:
            return "2G"
        elif "UMTS" in response or "HSDPA" in response or "HSPA" in response:
            return "3G"
        elif "LTE" in response or "EPS" in response:
            return "LTE (4G)"
        else:
            return "Unknown"
    except Exception as e:
        print("Error:", e)
        return "Unknown"
    
def rssi_to_dbm(rssi):
    # Công thức ánh xạ giá trị RSSI sang mức độ dBm cho LTE
    if rssi == 0:
        return -113
    elif rssi == 1:
        return -111
    elif 2 <= rssi <= 30:
        return -109 + (rssi - 2) * 2
    elif rssi == 31:
        return -51
    elif rssi == 99:
        return "Not known or not detectable"
    elif rssi == 100:
        return -116
    elif rssi == 101:
        return -115
    elif 102 <= rssi <= 190:
        return -114 + (rssi - 102)
    elif rssi == 191:
        return -25
    elif rssi == 199:
        return "Not known or not detectable"
    elif 100 <= rssi <= 199:
        return "Extended to be used in TDSCDMA indicating received signal code power (RSCP)"
    else:
        return "(Invalid RSSI code)"

def display_signal_2g_3g(rssi):
    # Chuyển đổi giá trị RSSI sang dBm
    dbm = rssi_to_dbm(rssi)
    if isinstance(dbm, int) or isinstance(dbm, float):
        if dbm >= -70:
            data = {
               'dbm': str(dbm) + "dBm",
               'signal': 4
            }
            return data
        elif -70 > dbm >= -85:
            data = {
               'dbm': str(dbm) + "dBm",
               'signal': 3
            }
            return data
        elif -85 > dbm >= -100:
            data = {
               'dbm': str(dbm) + "dBm",
               'signal': 2
            }
            return data
        elif dbm < -100:
            data = {
               'dbm': str(dbm) + "dBm",
               'signal': 1
            }
            return data
    else:
        data = {
               'dbm': "No signal",
               'signal': 0
            }
        return data


def display_signal_lte(rssi):
    # Chuyển đổi giá trị RSSI sang dBm
    dbm = rssi_to_dbm(rssi)
   
    # Hiển thị mức độ tín hiệu tương ứng với mức dBm
    if isinstance(dbm, int) or isinstance(dbm, float):
        if dbm > -65:
            data = {
               'dbm': str(dbm) + "dBm",
               'signal': 4
            }
            return data
        elif -65 >= dbm > -75:
            data = {
               'dbm': str(dbm) + "dBm",
               'signal': 3
            }
            return data
        elif -75 >= dbm > -85:
            data = {
               'dbm': str(dbm) + "dBm",
               'signal': 2
            }
            return data
        elif -85 >= dbm > -95:
            data = {
               'dbm': str(dbm) + "dBm",
               'signal': 1
            }
            return data
        else:
            data = {
               'dbm': "No signal",
               'signal': 0
            }
            return data
    else:
        data = {
               'dbm': "No signal",
               'signal': 0
            }
        return data

def get_network_operator(ser):
    try:
        # Gửi lệnh AT để lấy thông tin nhà mạng
        send_command(ser, 'AT+COPS?')
        # Đọc phản hồi từ module
        response = read_response(ser)
        # Tìm và trích xuất tên nhà mạng từ phản hồi
        if '+COPS' in response:
            try:
                operator_info = response.split(',')[2].strip('"')
                # Chia chuỗi kết quả thành các từ
                words = operator_info.split()
                # Nếu có hai từ trở lên, loại bỏ từ cuối cùng
                if len(words) >= 2:
                    return ' '.join(words[:-1])
                return operator_info
            except (IndexError, ValueError) as e:
                # Bắt các lỗi liên quan đến việc xử lý chuỗi
                print("Error processing operator info:" + str(e))
                return "Unknown"
        else:
            return "Unknown"
    except Exception as e:
        # Bắt và xử lý các lỗi chung
        print("An error occurred:" + str(e))
        return "Unknown"

    
def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def convert_seconds_to_hhmmss(total_seconds):
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return "{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds))


def job_PhatBanTinTinh(ban_tin, status):
    global DanhSachBanTinDung, IdLichDangPhat, BanTinKeTiep, ChoPhatBanTinTinh  
    if(PhatKhanCap == False):     
        time.sleep(1)  
        playBantinTinh(ban_tin, status)
        api_nhatkybantinTinh(ban_tin)
          

def job_DungBanTinTinh():
    global DungBanTinTinh, DanhSachBanTinDung, IdLichDangPhat, BanTinKeTiep, ChoPhatBanTinTinh, phatbantintinh
    if PhatKhanCap == False:    
        phatbantintinh = False
        DungBanTinTinh = False
        if PhatBanTinNoiBo == False:
            DungBanTin()
           
def job_GuiApiPhatLaiLichPhatKhanCap(LichPhat):
    try:
        dataGui = {
           'id': id,
           'version': version,
           'LichPhat': LichPhat
        }
      
        responsePingtest = requests.post(domainGuiLichPhat, json = dataGui, timeout=5)
        trave = responsePingtest.json()
        # if trave['data'] == 'true':
            
        #     nguonphat = lap_qua_nguon_phat(LichPhat['GioBatDau'] , LichPhat['DanhSachNguonPhat'])
        #     kiem_tra_lich_phat_dang_phat(LichPhat, nguonphat)
        # else:
        #     DungBanTin()  
    except Exception as e:
            print('Loi Gui lich Phat lai Lich phat:' + str(e))

# dừng bản tin nội bộ
def job_DungBanTinNoiBo(LichPhat):
    now = datetime.now(local_timezone)
    ThoiGianHienTai = int(now.timestamp())
    global DanhSachBanTinDung, IdLichDangPhat, BanTinKeTiep, ChoPhatBanTinTinh, phatbantintinh
    if LichPhat['KieuPhat'] == 'phatngay':
        if LichPhat['KieuLapLai'] == 0:
            if(phatbantintinh == False and PhatKhanCap == False):               
                DungBanTin()  
        # Kiểm tra lặp lại ngay
        elif LichPhat['KieuLapLai'] == 1:
            if LichPhat['SoLanLapLai'] > 0:
                LichPhat['SoLanLapLai'] = LichPhat['SoLanLapLai'] - 1
                LichPhat['GioBatDau'] = ThoiGianHienTai 
                LichPhat['ThoiGianKetThuc'] = int(ThoiGianHienTai + LichPhat['ThoiLuong'])               
                job_GuiApiPhatLaiLichPhatKhanCap(LichPhat)
            else:
                if(phatbantintinh == False and PhatKhanCap == False):                 
                    DungBanTin()  
        elif LichPhat['KieuLapLai'] == 2:
            DungBanTin() 
            if LichPhat['SoLanLapLai'] > 0:
                LichPhat['SoLanLapLai'] = LichPhat['SoLanLapLai'] - 1
                LichPhat['GioBatDau'] = ThoiGianHienTai + LichPhat['ThoiGianLapLai']               
                LichPhat['ThoiGianKetThuc'] = int(ThoiGianHienTai + LichPhat['ThoiGianLapLai']  + LichPhat['ThoiLuong']) 
                job_id = "PhatLaiLichPhatKhanCap_" + str(LichPhat['LichPhatID'])
                bat_dau = datetime.fromtimestamp(ThoiGianHienTai + LichPhat['ThoiGianLapLai'] , local_timezone)
                if not scheduler.get_job(job_id):
                    scheduler.add_job(job_GuiApiPhatLaiLichPhatKhanCap, 'date', run_date=bat_dau, args=[LichPhat], id=job_id)  
                nguonphat = lap_qua_nguon_phat(ThoiGianHienTai + LichPhat['ThoiGianLapLai'], LichPhat['DanhSachNguonPhat'])
                kiem_tra_lich_phat_dang_phat(LichPhat, nguonphat)
            else:
                if(phatbantintinh == False and PhatKhanCap == False):                  
                    DungBanTin()  
    else:
       if(phatbantintinh == False and PhatKhanCap == False):       
          DungBanTin()  

# phát bản tin nội bộ       
def job_PhatBanTinNoiBo(Ban_Tin, LichPhat):  
    global  IdLichDangPhatNoiBo
   
    try:
      now = datetime.now(local_timezone)
      if Ban_Tin['kieunguon'] == "Tiếp Sóng":
          data = {
            'title': Ban_Tin['tenchuongtrinh'],
            'sourceType': Ban_Tin['kieunguon'],
            'duration': convert_seconds_to_hhmmss(Ban_Tin['thoiluong']),
            'audioName': Ban_Tin['tenkenh'],
            'path': Ban_Tin['urltiepsong']['url'],
            'url': Ban_Tin['urltiepsong']['url'] ,
            'playType': 'phatngay' if LichPhat['KieuPhat'] == 'phatngay' else "theolich",
            'AuthorFullname': Ban_Tin['nguoitao']['hoten'],
            'AuthorUsername': Ban_Tin['nguoitao']['tentaikhoan'],
            'AuthorAvatar': 'https://server1.gtechdn.vn/v1/client/avatar/NoAvatar.png',
            'AuthorMail': Ban_Tin['nguoitao']['email'],
            'kieunguon': Ban_Tin['kieunguon']
          }
          dataPingTinh = {
              'BanTinID': Ban_Tin['mabantin'],
              'LoaiBanTin': LichPhat['LoaiBanTin'],
              'MucDoUuTien': str(LichPhat['MucDoUuTien']),
              'TieuDe': LichPhat['TieuDe'],
              'LoaiLinhVuc': str(LichPhat['LoaiLinhVuc']),
              'NoiDungTomTat': LichPhat['TieuDe'],
              'ThoiGianSanXuat': LichPhat['ThoiGianSanXuat'],
              'ThoiLuong': convert_seconds_to_hhmmss(LichPhat['ThoiLuong']),
              'TacGia': {
                  'TenDayDu': Ban_Tin['nguoitao']['hoten'],
                  'ButDanh': Ban_Tin['nguoitao']['tentaikhoan'],
                  'Email': Ban_Tin['nguoitao']['email']
              },
              'ThoiDiemBatDau': int(Ban_Tin['ThoiGianBatDau']),
              'TiepAm': 0,
              'NguonTiepAm': '',
              'NoiDung': Ban_Tin['urltiepsong']['url'],
              'ThongTinChiTietBanTin': [{ 'Ten': '', 'GiaTri': '' }],
              'NguonTin': LichPhat['NguonTin'],             
              'CongSuat': ''
          }
          if(phatbantintinh == False and PhatKhanCap == False):
              IdLichDangPhatNoiBo = LichPhat['LichPhatID']
              PhatBanTin(data)
              if trangthaiguiApi == True:
                  api_nhatkybantinTinh(dataPingTinh)
      elif Ban_Tin['kieunguon'] == "FILE":
         for file in Ban_Tin['files']:
            bat_dau = datetime.fromtimestamp(file['ThoiGianBatDau'], local_timezone)
            ket_thuc = datetime.fromtimestamp(file['ThoiGianKetThuc'], local_timezone)
            data = {
                'title': Ban_Tin['tenchuongtrinh'],
                'sourceType': Ban_Tin['kieunguon'],
                'duration': convert_seconds_to_hhmmss(file['duration']),
                'audioName': file['fileName'],
                'path': str('http://' + quote(linkS3 + file['url'])), 
                'url': str('http://' + quote(linkS3 + file['url'])),
                'playType': 'phatngay' if LichPhat['KieuPhat'] == 'phatngay' else "theolich",
                'AuthorFullname': Ban_Tin['nguoitao']['hoten'],
                'AuthorUsername': Ban_Tin['nguoitao']['tentaikhoan'],
                'AuthorAvatar': 'https://server1.gtechdn.vn/v1/client/avatar/NoAvatar.png',
                'AuthorMail': Ban_Tin['nguoitao']['email'],
                'ThoiGianBatDau': file['ThoiGianBatDau'],
                'ThoiGianKetThuc': file['ThoiGianKetThuc'],
                'kieunguon': Ban_Tin['kieunguon']
                }   
          
            dataPingTinh = {
                'BanTinID': Ban_Tin['mabantin'],
                'LoaiBanTin': LichPhat['LoaiBanTin'],
                'MucDoUuTien': str(LichPhat['MucDoUuTien']),
                'TieuDe': LichPhat['TieuDe'],
                'LoaiLinhVuc': str(LichPhat['LoaiLinhVuc']),
                'NoiDungTomTat': LichPhat['TieuDe'],
                'ThoiGianSanXuat': LichPhat['ThoiGianSanXuat'],
                'ThoiLuong': convert_seconds_to_hhmmss(LichPhat['ThoiLuong']),
                'TacGia': {
                    'TenDayDu': Ban_Tin['nguoitao']['hoten'],
                    'ButDanh': Ban_Tin['nguoitao']['tentaikhoan'],
                    'Email': Ban_Tin['nguoitao']['email']
                },
                'ThoiDiemBatDau': int(Ban_Tin['ThoiGianBatDau']),
                'TiepAm': 0,
                'NguonTiepAm': '',
                'NoiDung': str('http://' + quote(linkS3 + file['url'])),
                'ThongTinChiTietBanTin': [{ 'Ten': '', 'GiaTri': '' }],
                'NguonTin': LichPhat['NguonTin'],             
                'CongSuat': ''
            }           
            if now >= bat_dau and now <= ket_thuc:
                if(phatbantintinh == False and PhatKhanCap == False):
                  IdLichDangPhatNoiBo = LichPhat['LichPhatID']
                  PhatBanTin(data)
                  if trangthaiguiApi == True:
                      api_nhatkybantinTinh(dataPingTinh)
            elif now < bat_dau:
                job_id = "PhatBanTinNoiBoFILE_" + generate_random_string(10)
                if not scheduler.get_job(job_id):
                    scheduler.add_job(job_PhatBanTinNoiBo, 'date', run_date=bat_dau, args=[Ban_Tin, LichPhat], id=job_id)     
      else:
        data = {
          'title': Ban_Tin['tenchuongtrinh'],
          'sourceType': Ban_Tin['kieunguon'],
          'duration': convert_seconds_to_hhmmss(Ban_Tin['thoiluong']),
          'audioName': Ban_Tin.get('noidung', 'noidunggiongnoi'),
          'path': Ban_Tin['url'],
          'url': Ban_Tin['url'] ,
          'playType': 'phatngay' if LichPhat['KieuPhat'] == 'phatngay' else "theolich",
          'AuthorFullname': Ban_Tin['nguoitao']['hoten'],
          'AuthorUsername': Ban_Tin['nguoitao']['tentaikhoan'],
          'AuthorAvatar': 'https://server1.gtechdn.vn/v1/client/avatar/NoAvatar.png',
          'AuthorMail': Ban_Tin['nguoitao']['email'],
          'ThoiGianBatDau': Ban_Tin['ThoiGianBatDau'],
          'ThoiGianKetThuc': Ban_Tin['ThoiGianKetThuc'],
          'kieunguon': Ban_Tin['kieunguon']
        }

        dataPingTinh = {
            'BanTinID': Ban_Tin['mabantin'],
            'LoaiBanTin': LichPhat['LoaiBanTin'],
            'MucDoUuTien': str(LichPhat['MucDoUuTien']),
            'TieuDe': LichPhat['TieuDe'],
            'LoaiLinhVuc': str(LichPhat['LoaiLinhVuc']),
            'NoiDungTomTat': LichPhat['TieuDe'],
            'ThoiGianSanXuat': LichPhat['ThoiGianSanXuat'],
            'ThoiLuong': convert_seconds_to_hhmmss(LichPhat['ThoiLuong']),
            'TacGia': {
                'TenDayDu': Ban_Tin['nguoitao']['hoten'],
                'ButDanh': Ban_Tin['nguoitao']['tentaikhoan'],
                'Email': Ban_Tin['nguoitao']['email']
            },
            'ThoiDiemBatDau': int(Ban_Tin['ThoiGianBatDau']),
            'TiepAm': 0,
            'NguonTiepAm': '',
            'NoiDung': Ban_Tin['url'],
            'ThongTinChiTietBanTin': [{ 'Ten': '', 'GiaTri': '' }],
            'NguonTin': LichPhat['NguonTin'],             
            'CongSuat': ''
            }    
        if(phatbantintinh == False and PhatKhanCap == False):
            IdLichDangPhatNoiBo = LichPhat['LichPhatID']
            PhatBanTin(data)    
            if trangthaiguiApi == True:
                api_nhatkybantinTinh(dataPingTinh)            
    except Exception as e:
            print('loi chay job phat ban tin noi bo theo lich "job_PhatBanTinNoiBo":' + str(e))
       
# hàm xóa Job
def delete_job():
    jobs = scheduler.get_jobs()
    for job in jobs:
        chuoi = job.id
        vi_tri_cuoi_cung = chuoi.rfind('_')
        chuoi_ket_qua = chuoi[:vi_tri_cuoi_cung]
        if chuoi_ket_qua == "PhatLaiLichPhatKhanCap" or chuoi_ket_qua == "DungBanTinNoiBo" or chuoi_ket_qua == "PhatBanTinNoiBo" or chuoi_ket_qua == "PhatBanTinNoiBoFILE":
            scheduler.remove_job(job.id)


# Hàm để thêm trường DaPhat vào danh sách lịch phát
def add_index_and_status(data):
    for ban_tin in data:
        for ngay_phat in ban_tin['DanhSachNgayPhat']:
            for thoi_diem in ngay_phat['ThoiDiemPhat']:
                thoi_diem['DaPhat'] = False
    return data


def load_data_from_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def save_data_to_file(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


# Lấy bản tin tiếp theo trong danh sách
def next_ban_tin(data, lich_phat_id, idBanTin):
    nearest_time_diff = float('inf')
    current_time = time.time()  # Lấy thời gian hiện tại dưới dạng epoch time
    current_date = datetime.fromtimestamp(current_time).date()  # Lấy ngày hiện tại
    for index, ban_tin in enumerate(data):
        if ban_tin['LichPhatID'] == lich_phat_id:
            for ngay_phat in ban_tin['DanhSachNgayPhat']:
                for thoi_diem_phat in ngay_phat['ThoiDiemPhat']:                   
                    thoi_gian_phat_epoch = thoi_diem_phat['ThoiGianBatDau']
                    thoi_gian_phat_date = datetime.fromtimestamp(thoi_gian_phat_epoch).date()  # Lấy ngày từ ThoiGianBatDau
                    # Kiểm tra nếu ngày phát trùng với ngày hiện tại
                    if thoi_gian_phat_date != current_date:                       
                        continue
                    time_diff = thoi_gian_phat_epoch - current_time
                    # Chỉ quan tâm đến những thời điểm phát sau thời điểm bắt đầu truyền vào
                    if ban_tin['BanTinID'] == idBanTin:
                            thoi_diem_phat['DaPhat'] = True
                    if time_diff > 0 and time_diff < nearest_time_diff:
                        nearest_time_diff = time_diff
                        # Cập nhật lại thời điểm phát
                        original_thoiGianBatDau = thoi_diem_phat['ThoiGianBatDau']
                        duration = thoi_diem_phat['ThoiGianKetThuc'] - original_thoiGianBatDau
                        thoi_diem_phat['ThoiGianBatDau'] = int(current_time)
                        thoi_diem_phat['ThoiGianKetThuc'] = int(thoi_diem_phat['ThoiGianBatDau'] + duration)
                        # Cập nhật lại dữ liệu trong data ban đầu
                        data[index] = ban_tin
                        return data

    return data  # Trường hợp không tìm thấy bản tin phù hợp
                                
# Đặt tất cả các bản tin thành True
def set_all_status_to_true():
    # Đặt danh sách bản tin thành rỗng
    data = []
    # Lưu lại dữ liệu vào file JSON
    with open('lichphatTinh.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
    
# Kiểm tra lịch phát
def kiem_tra_thoi_gian_bat_dau():

    global ChoPhatBanTinTinh, phatbantintinh, PhatKhanCap
    now = datetime.now(local_timezone)
    gio = now.strftime("%H")
    phut = now.strftime("%M")
    # Lấy ra ngày, tháng, năm
    ngay = now.strftime("%d")
    thang = now.strftime("%m")
    nam = now.strftime("%Y")
    gio_tim = "{}:{}".format(gio, phut)
    ngay_tim = "{}-{}-{}".format(ngay, thang, nam)

 
    # Đọc dữ liệu từ file lichphatTinh.json
    with open('lichphatTinh.json', 'r') as file:
        data = json.load(file)
    # Kiểm tra từng mục trong danh sách
    found_item = None
    lay_bat_dau = None
    lay_ket_thuc = None
    if len(data) > 0:
        for item in data:         
            #if item['status'] == False:
                for ngay_phat in item['DanhSachNgayPhat']:
                    tim_ngay_phat = ngay_phat['TimNgayPhat']
                    if tim_ngay_phat == ngay_tim:              
                        for thoi_diem_phat in ngay_phat['ThoiDiemPhat']:
                            if thoi_diem_phat['DaPhat'] == False:
                                tim_gio_phat = thoi_diem_phat['TimThoiGianBatDau']
                                bat_dau = thoi_diem_phat["ThoiGianBatDau"]
                                ket_thuc = thoi_diem_phat["ThoiGianKetThuc"]
                                # Chuyển đổi bat_dau và ket_thuc thành đối tượng datetime
                                bat_dau = datetime.fromtimestamp(bat_dau, local_timezone)
                                ket_thuc = datetime.fromtimestamp(ket_thuc, local_timezone)                                
                                # Thực hiện kiểm tra tại đây
                                if now >= bat_dau and now <= ket_thuc:                                
                                    found_item = item
                                    lay_bat_dau = thoi_diem_phat["ThoiGianBatDau"]
                                    lay_ket_thuc = thoi_diem_phat["ThoiGianKetThuc"]                           
                                elif now < bat_dau:
                                    remaining_seconds = (bat_dau - now).total_seconds()                                  
                                    if int(remaining_seconds) <= 120:
                                        IDBanTinString = item["IDBanTinString"]
                                        item["ThoiDiemBatDau"] = thoi_diem_phat["ThoiGianBatDau"]
                                        item["ThoiDiemKetThuc"] = thoi_diem_phat["ThoiGianKetThuc"]                                    
                                        job_id = "PhatBanTin_" + IDBanTinString                                      
                                        if not scheduler.get_job(job_id):
                                            # Thêm một giây vào thời điểm bắt đầu
                                            #bat_dau = bat_dau + timedelta(seconds=1)
                                            scheduler.add_job(job_PhatBanTinTinh, 'date', run_date=bat_dau, args=[item, 1], id=job_id)                                       
        if found_item is not None:        
            if DungBanTinTinh == False and phatbantintinh == False and PhatKhanCap == False:                                   
              found_item["ThoiDiemBatDau"] = lay_bat_dau
              found_item["ThoiDiemKetThuc"] = lay_ket_thuc
              job_PhatBanTinTinh(found_item, 0)
        else:
            if phatbantintinh == False and PhatKhanCap == False:
              job_DungBanTinTinh()
       
# Hàm kiểm tra dừng bản tin
def kiem_tra_thoi_gian_ket_thuc():
    global ChoPhatBanTinTinh
    now = datetime.now(local_timezone)
    gio = now.strftime("%H")
    phut = now.strftime("%M")
    # Lấy ra ngày, tháng, năm
    ngay = now.strftime("%d")
    thang = now.strftime("%m")
    nam = now.strftime("%Y")
    ngay_tim = "{}-{}-{}".format(ngay, thang, nam)
    # Đọc dữ liệu từ file lichphatTinh.json
    with open('lichphatTinh.json', 'r') as file:
        data = json.load(file)
    # Kiểm tra từng mục trong danh sách
    if len(data) > 0:
        for item in data:
            for ngay_phat in item['DanhSachNgayPhat']:
                tim_ngay_phat = ngay_phat['TimNgayPhat']
                if tim_ngay_phat == ngay_tim:              
                    for thoi_diem_phat in ngay_phat['ThoiDiemPhat']:
                        if thoi_diem_phat['DaPhat'] == False:
                            bat_dau = thoi_diem_phat["ThoiGianBatDau"]
                            ket_thuc = thoi_diem_phat["ThoiGianKetThuc"]
                            # Chuyển đổi bat_dau và ket_thuc thành đối tượng datetime
                            bat_dau = datetime.fromtimestamp(bat_dau, local_timezone)
                            ket_thuc = datetime.fromtimestamp(ket_thuc, local_timezone)
                            # Thực hiện kiểm tra tại đây
                            if now < ket_thuc:
                                remaining_time = ket_thuc - now
                                remaining_seconds = remaining_time.total_seconds()
                                if int(remaining_seconds) <= 120:
                                    # print(f"Còn {int(remaining_seconds)} giây để kết thúc.")
                                    IDBanTinString = item["IDBanTinString"]
                                    job_id = "DungBanTin_" + IDBanTinString                                                       
                                    if not scheduler.get_job(job_id):
                                        scheduler.add_job(job_DungBanTinTinh, 'date', run_date=ket_thuc, id = job_id)
                                    #args=[item],

# hàm lặp qua các nguồn phát để thêm thời gian bắt đầu và kết thúc nguồn phát
def lap_qua_nguon_phat(GioBatDau,array):
    new_LichPhatDangNhan = []
    for nguonphat in array:
        if nguonphat['thutu'] == 1:
            nguonphat['ThoiGianBatDau'] = GioBatDau
            nguonphat['ThoiGianKetThuc'] = GioBatDau + nguonphat['thoigianBatdau']
            if nguonphat['kieunguon'] == "FILE":
               for file in nguonphat['files']:
                  file['ThoiGianBatDau'] = int(GioBatDau + file['thoigianbatdau']) 
                  file['ThoiGianKetThuc'] = int(GioBatDau + file['thoigianbatdau'] + file['duration'])            
        else:
            nguonphat['ThoiGianBatDau'] = int(GioBatDau + nguonphat['batdauPhat']) 
            nguonphat['ThoiGianKetThuc'] = int(GioBatDau + nguonphat['batdauPhat'] +  nguonphat['thoiluong']) 
            if nguonphat['kieunguon'] == "FILE":
               for file in nguonphat['files']:
                  file['ThoiGianBatDau'] = int(GioBatDau + nguonphat['batdauPhat'] + file['thoigianbatdau']) 
                  file['ThoiGianKetThuc'] = int(GioBatDau + nguonphat['batdauPhat'] + file['thoigianbatdau'] + file['duration'])        
        new_LichPhatDangNhan.append(nguonphat)
    return new_LichPhatDangNhan

# kiểm tra lịch phát đang phát
def kiem_tra_lich_phat_dang_phat(LichPhat, NguonPhats):
    global LichPhatDangNhan
    if LichPhatDangNhan == {}:
        pass # Không làm gì cả
    else:
        try:
            now = datetime.now(local_timezone)
            # Kiểm tra thời gian kết thúc
            ketthuc = LichPhat['GioBatDau'] + LichPhat['ThoiLuong']
            Thoi_Gian_Ket_Thuc = datetime.fromtimestamp(ketthuc, local_timezone)           
            # Lấy các thành phần của datetime       
            if now <= Thoi_Gian_Ket_Thuc:
                job_id = "DungBanTinNoiBo_" + str(LichPhat['LichPhatID']) 
                # kết thúc bản tin
                if not scheduler.get_job(job_id):
                    scheduler.add_job(job_DungBanTinNoiBo, 'date', run_date=Thoi_Gian_Ket_Thuc, args=[LichPhat], id=job_id)
                # lặp qua tất cả nguồn phát
                if len(NguonPhats) > 0:
                    for item in NguonPhats:
                        bat_dau = item['ThoiGianBatDau']
                        ket_thuc = item['ThoiGianKetThuc']   
                        bat_dau_so_sanh = datetime.fromtimestamp(bat_dau, local_timezone)
                        ket_thuc_so_sanh = datetime.fromtimestamp(ket_thuc, local_timezone)  
                        if now >= bat_dau_so_sanh and now <= ket_thuc_so_sanh:
                           job_PhatBanTinNoiBo(item, LichPhat)
                        elif now < bat_dau_so_sanh:                           
                            item["ThoiDiemBatDau"] = bat_dau
                            item["ThoiDiemKetThuc"] = ket_thuc 
                            job_id = "PhatBanTinNoiBo_" + item['mabantin']
                            if not scheduler.get_job(job_id):
                                scheduler.add_job(job_PhatBanTinNoiBo, 'date', run_date=bat_dau_so_sanh, args=[item, LichPhat], id=job_id)            
                                                  
        except Exception as e:
            print('loi kiem tra phat ban tin noi bo:' + str(e))
    # LichPhatDangNhan có giá trị khác {}                
######### get dia chi ip ###################
def get_ip_address():
    try:
        ip_address = ''
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception as e:
        print("An error occurred:" + str(e))
        return "0.0.0.0"
  
def control_led_status(value):
    global status_loaL, status_loaR, status_congsuat, docLoa
    # print('nhan lenh phat', value)
    # print('docLoa', docLoa)
    if value == 1:
        if docLoa == 0:
            gpio.output(on_loa,1)
            time.sleep(2)
            status_loaL = gpio.input(input_loa_L)
            status_loaR = gpio.input(input_loa_R)
            # print('status_loaL', status_loaL)
            # print('status_loaR', status_loaR)
            gpio.output(on_loa,0)
            docLoa = 1     
            gpio.output(led_status,1)
            time.sleep(1)
            gpio.output(mute,1)
            
    else:
        gpio.output(led_status,0)
        gpio.output(on_loa,0)
        time.sleep(1)
        gpio.output(mute,0)
        docLoa = 0


def control_led_connect(value):
    gpio.output(led_connect,value)

# dừng bản tin
def DungBanTin():
    global  idLichPhatTinhDangPhat, idBanTinTinhDangPhat, PhatBanTinNoiBo, IdLichDangPhatNoiBo, kiemtraPlay, TrangThaiHoatDong, ThoiDiemBatDau, urldangphat, tenchuongtrinh, kieunguon, thoiluong, tennoidung, diachingoidung, kieuphat, nguoitao, taikhoantao, Status, NoiDungPhat
    try:
        kiemtraPlay = 0
        idBanTinTinhDangPhat = ''
        idLichPhatTinhDangPhat = ''   
        PhatBanTinNoiBo = False
        VLC_instance.Stop_VLC()
        control_led_status(0)
       
        TrangThaiHoatDong = 2
        ThoiDiemBatDau = 0
        # trang thai play #
        #station_status = VLC_instance.get_Status_Play()
        
        urldangphat = ""
        tenchuongtrinh = ""
        kieunguon = ""
        thoiluong = ""
        tennoidung = ""
        diachingoidung = ""
        kieuphat = ""
        nguoitao = ""
        taikhoantao = ""
        Status = "false"
        NoiDungPhat = ""
        IdLichDangPhatNoiBo = ""
        data_object = {
            "type": "stop",
            "tenchuongtrinh": "",
            "tennoidung": "",
        }
        json_data = json.dumps(data_object)
        client.publish(trangthaiplay,json_data)
        time.sleep(1)
        #pingServer()
    except Exception as e:
        print('Loi Stop ban tin:' + str(e))

# phát bản tin
def PhatBanTin(data):
    
    global PhatBanTinNoiBo, NoiDungPhat, kiemtraPlay, demKiemtra, TrangThaiHoatDong, urldangphat, tenchuongtrinh, kieunguon, thoiluong, tennoidung, diachingoidung, kieuphat, nguoitao, taikhoantao
    try:        
        #print('PhatBanTin')
        PhatBanTinNoiBo = True
        if data['kieunguon'] == "Tiếp Sóng":
            control_led_status(1)
            VLC_instance.Play_VLC(data['url'])
            NoiDungPhat = data['url']
            kiemtraPlay = 1       
            TrangThaiHoatDong = 0
            # trang thai play #
            urldangphat = data['url']
            tenchuongtrinh = data['title']
            kieunguon = data['sourceType']
            thoiluong = data['duration']
            tennoidung = data['audioName']
            diachingoidung = data['path']
            kieuphat = data['playType']
            nguoitao = data['AuthorFullname']
            taikhoantao = data['AuthorUsername']
            #time.sleep(2)  
            station_status = VLC_instance.get_Status_Play()
            data_object = {
              "type": station_status,
              "tenchuongtrinh": tenchuongtrinh,
              "tennoidung": tennoidung,
            }
            
            json_data = json.dumps(data_object)
            client.publish(trangthaiplay,json_data)
           # VLC_instance.Set_Volume(amluong)
            #setVolume(amluong)
            LogBanTin()
            #pingServer()
        else:          
            thoi_gian_hien_tai = datetime.now()
            # Định dạng thời gian hiện tại thành timestamp (giây kể từ epoch)
            thoi_gian_hien_tai_timestamp = int(thoi_gian_hien_tai.timestamp() * 1000) 
          # Kiểm tra xem thời điểm hiện tại có nằm trong khoảng từ ThoiGianBatDau đến ThoiGianKetThuc không
            if data['ThoiGianBatDau'] * 1000 <= thoi_gian_hien_tai_timestamp <= data['ThoiGianKetThuc'] * 1000:
                thoi_gian_da_phat = thoi_gian_hien_tai_timestamp - (data['ThoiGianBatDau'] * 1000)      
                lay_thoi_gian = thoi_gian_da_phat 
                giaydaqua = lay_thoi_gian // 1000
                control_led_status(1)
                if giaydaqua >= 10:
                    VLC_instance.Play_VLC_Set_Time(data['url'], lay_thoi_gian)
                  
                else:
                    VLC_instance.Play_VLC(data['url'])
                
                NoiDungPhat = data['url']
                kiemtraPlay = 1       
                demKiemtra = 0
                TrangThaiHoatDong = 0
                # trang thai play #                       
                urldangphat = data['url']              
                tenchuongtrinh = data['title']              
                kieunguon = data['sourceType']               
                thoiluong = data['duration']             
                tennoidung = data['audioName']              
                diachingoidung = data['path']              
                kieuphat = data['playType']               
                nguoitao = data['AuthorFullname']              
                taikhoantao = data['AuthorUsername']             
                #station_status = VLC_instance.get_Status_Play()
                data_object = {
                  "type": "play",
                  "tenchuongtrinh": tenchuongtrinh,
                  "tennoidung": tennoidung,
                }
                json_data = json.dumps(data_object)
                client.publish(trangthaiplay,json_data)
               # setVolume(amluong)
                LogBanTin()
                #pingServer()
    except Exception as e:
        print('Loi Phat ban tin:' + str(e))

# phát bản tin tiếp tục
def PhatBanTin_TiepTuc(data):
    global NoiDungPhat, kiemtraPlay, demKiemtra, TrangThaiHoatDong, urldangphat, tenchuongtrinh, kieunguon, thoiluong, tennoidung, diachingoidung, kieuphat, nguoitao, taikhoantao
    try:
        thoi_gian_hien_tai = datetime.now()
        # Định dạng thời gian hiện tại thành timestamp (giây kể từ epoch)
        thoi_gian_hien_tai_timestamp = int(thoi_gian_hien_tai.timestamp() * 1000) 
       # Kiểm tra xem thời điểm hiện tại có nằm trong khoảng từ ThoiGianBatDau đến ThoiGianKetThuc không
        if data['ThoiDiemBatDau'] * 1000 <= thoi_gian_hien_tai_timestamp <= data['ThoiDiemKetThuc'] * 1000:
            thoi_gian_da_phat = thoi_gian_hien_tai_timestamp - (data['ThoiDiemBatDau'] * 1000)
            lay_thoi_gian = thoi_gian_da_phat 
            VLC_instance.Play_VLC_Set_Time(data['url'], lay_thoi_gian) 
        NoiDungPhat = data['url']
        kiemtraPlay = 1       
        demKiemtra = 0
        TrangThaiHoatDong = 0
        # trang thai play #
        control_led_status(1)
        urldangphat = data['url']
        tenchuongtrinh = data['title']
        kieunguon = data['sourceType']
        thoiluong = data['duration']
        tennoidung = data['audioName']
        diachingoidung = data['path']
        kieuphat = data['playType']
        nguoitao = data['AuthorFullname']
        taikhoantao = data['AuthorUsername']
        time.sleep(2) 
        station_status = VLC_instance.get_Status_Play()
        client.publish(trangthaiplay,station_status)
        LogBanTin()
        pingServer()
    except Exception as e:
        print('Loi Phat ban tin:' + str(e))

def KiemTraPhim():
    global demnhanphim
    if gpio.input(phim_wifi) == 1:
        demnhanphim += 1
        if demnhanphim == 5:
            nhapnhatLedConnectCallApiloi.stop()
            nhapnhay_wifi.start()
            os.system("sudo systemctl enable myappserver.service")
            os.system("sudo systemctl start myappserver.service")
            os.system("sudo nmcli con up MyHomeWiFi")
            os.system("sudo systemctl start hostapd")
           
        if demnhanphim == 10:
            nhapnhay_wifi.stop()
            control_led_connect(1)
            demnhanphim = 0
            os.system("sudo systemctl stop myappserver.service")
            os.system("sudo systemctl disable myappserver.service")
            os.system("sudo nmcli con down MyHomeWiFi")
           
# log bản tin
def LogBanTin():
    global amluong
    try:       
        # Gọi phương thức get_volume()
        #volume = VLC_instance.get_volume()
        thoigianphat = time.time()
        dataLog = {
          'urldangphat': urldangphat,
          'id': id,  
          'tenchuongtrinh': tenchuongtrinh,
          'kieunguon': kieunguon,
          'thoiluong': thoiluong,
          'tennoidung': tennoidung,
          'diachingoidung': diachingoidung,
          'kieuphat': kieuphat,
          'nguoitao': nguoitao,
          'taikhoantao': taikhoantao,
          'thoigianphat': int(thoigianphat),
          'volume': amluong,
        }
        responsePingtest = requests.post(domainLogbantin, json = dataLog, timeout=30)
    except Exception as e:
          print('Loi gui log ban tin:' + str(e))

# Call API xác nhận kết nối
def api_xacnhanketnoi(data):
    global amluong, linkS3, domainAddPlaylist, domainDeletePlaylist, NoiDungPhat, ThoiDiemBatDau, MaNhaCungCap, DichID,TenDich, trangthaiguiApi, userName, password, domainLoginTinh, domainPingTinh, domainLogTinh, imel, tenthietbi, madiaban, tendiaban, lat, lng, Status, Video, khoaguidulieu
    try:
        responsePingtest = requests.post(domainXacnhanketnoi, json = data, timeout=30)
        jsonResponse = responsePingtest.json() 
        if(jsonResponse['success'] == True):
            #setVolume(jsonResponse['data']['data']['volume'])
            amluong = int(jsonResponse['data']['data']['volume']) 
            VLC_instance.Set_Volume(jsonResponse['data']['data']['volume'])    
            schedule = add_index_and_status(jsonResponse['data']['data']['LichPhatTinh'])     
            with open('lichphatTinh.json', 'w') as json_file:
                json.dump(schedule, json_file, indent=4)
            # Xóa tất cả các job ngoại trừ các job có id "check_lich_phat_tinh" và "check_lich_dung_tinh"
            jobs = scheduler.get_jobs()
            for job in jobs:
                if job.id not in ["check_lich_phat_tinh", "check_lich_dung_tinh"]:
                    scheduler.remove_job(job.id)
            DungBanTin()
            # set tham so data APi ve tinh #
            domainLoginTinh = jsonResponse['data']['dataApi']['domainLogin']
            domainPingTinh = jsonResponse['data']['dataApi']['domainPing']
            domainLogTinh = jsonResponse['data']['dataApi']['domainLog']
            domainAddPlaylist = jsonResponse['data']['dataApi']['domainAddPlaylist']
            domainDeletePlaylist = jsonResponse['data']['dataApi']['domainDeletePlaylist']
            userName = jsonResponse['data']['dataApi']['userName']
            password = jsonResponse['data']['dataApi']['password']
            imel = jsonResponse['data']['dataApi']['imel']
            tenthietbi = jsonResponse['data']['dataApi']['deviceName']
            madiaban = jsonResponse['data']['dataApi']['DestinationID']
            tendiaban = jsonResponse['data']['dataApi']['DestinationName']
            lat = jsonResponse['data']['dataApi']['lat']
            lng = jsonResponse['data']['dataApi']['lng']
            DichID = jsonResponse['data']['dataApi']['DichID']
            TenDich = jsonResponse['data']['dataApi']['TenDich']
            MaNhaCungCap = jsonResponse['data']['dataApi']['MaNhaCungCap']
            linkS3 = jsonResponse['data']['data']['UrlS3']
        
            # kiem tra dieu kien gui API #
            if(jsonResponse['data']['dataApi']['statusApi'] == True):
                trangthaiguiApi = True   
            else:      
                trangthaiguiApi = False
                khoaguidulieu = True
                pingApiTinh.stop()
        
    except Exception as e:
        print('loi xac nhan ket noi:' + str(e))
  # get_speedtest()

# Call API gửi log bản tin về tỉnh
def api_nhatkybantinTinh(data):
  global tenthietbi, imel, madiaban, tendiaban, Status, Video, MaNhaCungCap, TenNhaCungCap, DichID, TenDich
  Status = "true"     
  #gui nhat ky ban tin ve tinh#
  ##seconds = time.time()
  volume = VLC_instance.get_volume()
  dataLichsuApi = {
    'NguonID': madiaban,
    'TenNguon': tendiaban,
    'DichID': DichID,
    'TenDich': TenDich,
    'CumLoaID': imel,
    'TenThietBi': tenthietbi,
    'MaNhaCungCap': MaNhaCungCap,
    'TenNhaCungCap': TenNhaCungCap,
    'BanTinID': data['BanTinID'],
    'LoaiBanTin': str(data['LoaiBanTin']),
    'MucDoUuTien': str(data['MucDoUuTien']),
    'TieuDe': data['TieuDe'],
    'LoaiLinhVuc': str(data['LoaiLinhVuc']),
    'NoiDungTomTat': data['NoiDungTomTat'],
    'ThoiGianSanXuat': int(data['ThoiGianSanXuat']),
    'ThoiLuong': data['ThoiLuong'],
    'TacGia': data['TacGia'],
    'ThoiDiemBatDau': int(data['ThoiDiemBatDau']),
    'TiepAm': 0,
    'NguonTiepAm': data['NguonTiepAm'],
    'NoiDung': data['NoiDung'],
    'ThongTinChiTietBanTin': data['ThongTinChiTietBanTin'],
    'NguonTin': data['NguonTin'],
    'AmLuong': str(amluong),
    'CongSuat': ''
  }
  try:
    responseLogbantinTinh = requests.post(domainLoginTinh, json = {'Username':userName, 'Password':password}, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0','Content-Type': "application/json", 'Accept': "application/json"})
    datajsonResponseLog = responseLogbantinTinh.json()
    #print(datajsonResponseLog['NoiDung']['Token'])
    if(datajsonResponseLog['TrangThaiGui'] == 0): 
      headers = {'Authorization': "Bearer {}".format(datajsonResponseLog['NoiDung']['Token']), 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0', 'Content-Type': "application/json", 'Accept': "application/json"}
      responseLog = requests.post(domainLogTinh, json = dataLichsuApi, headers=headers, timeout=5)
    #   if responseLog.status_code == 400:
    #       error_message = responseLog.text  # Đọc thông báo lỗi từ nội dung phản hồi
    #       print("Thông báo lỗi:", error_message)
    #   else:
    #     print("Yêu cầu thành công!")
    #     print(responseLog.json())
    # responseLog = requests.post(domainLogTinh, json = dataLichsuApi)
  except:
    print('loi gui log ban tin ve tinh')
 
# API nhật ký bản tạo mới cập nhật bản tin tỉnh
def api_nhatkyTaomoiBanTinTinh(data):
    dataLichsuApi = {
        'NguonID': madiaban,
        'TenNguon': tendiaban,
        'DichID': DichID,
        'TenDich': TenDich,
        'DanhSachDiaBan': data['DanhSachDiaBanNhan'],
        'CumLoaID': imel,
        'TenThietBi': tenthietbi,
        'MaNhaCungCap': MaNhaCungCap,
        'TenNhaCungCap': TenNhaCungCap,
        'LichPhatID': data['LichPhatID'],
        'TenLichPhat': data['TenLichPhat'],
        'DanhSachBanTin': data['DanhSachBanTin'],
    }
  
    try:
        responseLogbantinTinh = requests.post(domainLoginTinh, json = {'Username':userName, 'Password':password}, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0','Content-Type': "application/json", 'Accept': "application/json"})
        datajsonResponseLog = responseLogbantinTinh.json()
        #print(datajsonResponseLog['NoiDung']['Token'])
        if(datajsonResponseLog['TrangThaiGui'] == 0): 
            headers = {'Authorization': "Bearer {}".format(datajsonResponseLog['NoiDung']['Token']), 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0', 'Content-Type': "application/json", 'Accept': "application/json"}
            responseLog = requests.post(domainAddPlaylist, json = dataLichsuApi, headers=headers, timeout=5)
           # print(responseLog.json())
            #   if responseLog.status_code == 400:
            #       error_message = responseLog.text  # Đọc thông báo lỗi từ nội dung phản hồi
            #       print("Thông báo lỗi:", error_message)
            #   else:
            #     print("Yêu cầu thành công!")
            #     print(responseLog.json())
            # responseLog = requests.post(domainLogTinh, json = dataLichsuApi)
    except:
        print('loi gui log ban tin ve tinh')

# API nhật ký hủy lịch tỉnh
def api_nhatkyHuyBanTinTinh(data):
    dataLichsuApi = {
        'NguonID': madiaban,
        'TenNguon': tendiaban,
        'DichID': DichID,
        'TenDich': TenDich,
        'DanhSachThietBi': data['DanhSachThietBi'],
        'LichPhatID': data['LichPhatID'],
        'TenLichPhat': data['TenLichPhat'],
    }
   
    try:
        responseLogbantinTinh = requests.post(domainLoginTinh, json = {'Username':userName, 'Password':password}, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0','Content-Type': "application/json", 'Accept': "application/json"})
        datajsonResponseLog = responseLogbantinTinh.json()
        #print(datajsonResponseLog['NoiDung']['Token'])
        if(datajsonResponseLog['TrangThaiGui'] == 0): 
            headers = {'Authorization': "Bearer {}".format(datajsonResponseLog['NoiDung']['Token']), 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0', 'Content-Type': "application/json", 'Accept': "application/json"}
            responseLog = requests.post(domainDeletePlaylist, json = dataLichsuApi, headers=headers, timeout=5)
           # print(responseLog.json())
            #   if responseLog.status_code == 400:
            #       error_message = responseLog.text  # Đọc thông báo lỗi từ nội dung phản hồi
            #       print("Thông báo lỗi:", error_message)
            #   else:
            #     print("Yêu cầu thành công!")
            #     print(responseLog.json())
            # responseLog = requests.post(domainLogTinh, json = dataLichsuApi)
    except:
        print('loi gui log ban tin ve tinh')
   
# gửi trạng thái mất điện
def api_TrangThaiMatDien(value, ThoiGian):
    try:
      data = {
        'id': id,
        'MatDien': value,
        'ThoiGianMatDien': ThoiGian
      }
      responsePing = requests.post(domainPingMatDien, json = data, timeout=5)
      trave = responsePing.json()
      return trave['success']
     
    except Exception as e:    
       pass

# Ping trạng thái thiết bị về server tỉnh
def pingTinh():
  global domainAddPlaylist, domainDeletePlaylist, NoiDungPhat, ThoiDiemBatDau, kiemtraPlay, DichID, TenDich, TenLoaiThietBi,  MaNhaCungCap, TenNhaCungCap, TrangThaiHoatDong, trangthaiguiApi, userName, password, domainLoginTinh, domainPingTinh, domainLogTinh, imel, tenthietbi, madiaban, tendiaban, lat, lng, Video, khoaguidulieu
  # test
  if not khoaguidulieu:
    if trangthaiguiApi == None or userName == '':
      try:
        data = {
          'id': id
        }
        responseXacnhan = requests.post(domainXacnhanketnoilai, json= data)
        jsonResponse = responseXacnhan.json()
  
        if jsonResponse['success'] == True:
          domainLoginTinh = jsonResponse['data']['domainLogin']
          domainPingTinh = jsonResponse['data']['domainPing']
          domainLogTinh = jsonResponse['data']['domainLog']
          domainAddPlaylist = jsonResponse['data']['domainAddPlaylist']
          domainDeletePlaylist = jsonResponse['data']['domainDeletePlaylist']
          userName = jsonResponse['data']['userName']
          password = jsonResponse['data']['password']
          imel = jsonResponse['data']['imel']
          tenthietbi = jsonResponse['data']['deviceName']
          madiaban = jsonResponse['data']['DestinationID']
          tendiaban = jsonResponse['data']['DestinationName']
          lat = jsonResponse['data']['lat']
          lng = jsonResponse['data']['lng']
          DichID = jsonResponse['data']['DichID']
          TenDich = jsonResponse['data']['TenDich']
          MaNhaCungCap = jsonResponse['data']['MaNhaCungCap']
          if jsonResponse['data']['statusApi'] == True:
            trangthaiguiApi = True
          else:
            trangthaiguiApi = False
            khoaguidulieu = True
            pingApiTinh.stop()
      except:
        print('loi call api xac nhan ket noi lai')
  if trangthaiguiApi:
      try:
        response = requests.post(domainLoginTinh, json = {'Username':userName, 'Password':password}, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0', 'Content-Type': "application/json", 'Accept': "application/json"})
        jsonResponse = response.json()           
        trangthai = jsonResponse['TrangThaiGui']
        if trangthai == 0:
          Token = jsonResponse['NoiDung']["Token"]        
          seconds = time.time()
          volume = VLC_instance.get_volume()
          ping = {
            'NguonID': madiaban,
            'TenNguon': tendiaban,
            'DichID': DichID,
            'TenDich': TenDich,
            'CumLoaID': imel,
            'TenThietBi': tenthietbi,
            'TenLoaiThietBi': TenLoaiThietBi,
            'MaNhaCungCap': MaNhaCungCap,
            'TenNhaCungCap': TenNhaCungCap,
            'AmLuong': str(amluong),
            'TrangThaiHoatDong': str(TrangThaiHoatDong),
            'TrangThaiKetNoi': TrangThaiKetNoi,
            'ViDo': float(lat) if lat else 0,
            'KinhDo': float(lng) if lng else 0,
            'ThongTinThietBi': {
              'CongSuat': '',
              'NhietDo': '41',
              'DungLuongSuDung': ''
            },
            'ThoiDiemBatDau': int(seconds),
            'NoiDungPhat': NoiDungPhat,
            'PhienBanUngDung': phienban,
          }     
          # Chuyển đổi epoch time thành đối tượng datetime
          # dt = datetime.fromtimestamp(seconds)
          # # Hiển thị thời gian dưới dạng 'HH:MM:SS - dd/mm/yyyy'
          # formatted_time = dt.strftime('%H:%M:%S - %d/%m/%Y')
          # client.publish('datatest2', str(formatted_time)) 
       
          headers = {'Authorization': "Bearer {}".format(Token), 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0', 'Content-Type': "application/json", 'Accept': "application/json"}   
          responsePing = requests.post(domainPingTinh, json = ping, headers=headers, timeout=20)
        #   trave = responsePing.json()
        #   json_data = json.dumps(trave)
        #   print(ping)
        #   print(json_data)
        #   json_dataBody = json.dumps(ping)
        #   client.publish('testdata',json_data)
        #   client.publish('testdata',json_dataBody)
      except Exception as e:    
        print('loi call api ping tinh:' + str(e))
      
       
# Ping trạng thái thiết bị về server
def pingServer():
    global loiketnoi, linkS3, LichPhatDangNhan, phatbantintinh, Video, NoiDungPhat, urldangphat, tenchuongtrinh, kieunguon, thoiluong, tennoidung, diachingoidung, kieuphat, nguoitao, taikhoantao, demLoicallApiPing, loiketnoi, kiemtraPlay, led_status, demKiemtra, mabantinnhan, trangthaiplay
    if(loiketnoi == 10):       
        os.system("(sudo systemctl restart myapp.service)")
    try:
        # Lấy danh sách các Wi-Fi có sẵn
        #wifi_list = get_wifi_list()
        #print("Danh sách Wi-Fi:", wifi_list)
        # print('///----------------------------------------------////')
        # for job in scheduler.get_jobs():           
        #     print(f"Job ID: {job.id}, Next Run Time: {job.next_run_time}")
        # Gọi phương thức get_volume()
        # trang thai play #
       
        station_status = VLC_instance.get_Status_Play()   
        statusLoa = {
            'status_loaL': status_loaR,
            'status_loaR': status_loaL,
            'status_congsuat': status_congsuat
        }  
        seconds = time.time()
        dataPing = {
            'phatbantintinh': phatbantintinh,
            'url': urldangphat,
            'id': id,
            'trangthai': station_status,   
            'tenchuongtrinh': tenchuongtrinh,
            'kieunguon': kieunguon,
            'thoiluong': thoiluong,
            'tennoidung': tennoidung,
            'diachingoidung': diachingoidung,
            'kieuphat': kieuphat,
            'nguoitao': nguoitao,
            'taikhoantao': taikhoantao,
            'trangthaiplay': trangthaiplay,
            'ThoiDiemKetThuc': ThoiDiemKetThuc,
            'version': version,
            'IDLichDangPhat': IdLichDangPhatNoiBo,
            'Rssi': Rssi,
            'TenNhaMang': TenNhaMang,
            'MatDien': TrangThaiGuiMatDien,
            'dbm': dbm,
            'LoaiMang': LoaiMang,
            'statusLoa': statusLoa,
            'timePing':  int(seconds)  
        }
       
        responsePingtest = requests.post(domainPing, json = dataPing, timeout=20)
        trave = responsePingtest.json()
        if(trave['data'] != ''):
            linkS3 = trave['data']['urlS3'] 
            if(trave['data']['statusPlay'] == 'play'):  
                status = player.get_state_2()
                if status == 'Opening':                 
                    pass
                else:                  
                # play bản tin  
                    VLC_instance.Stop_VLC()
                    LichPhatDangNhan = trave['data']['LichPhat']
                    nguonphat = lap_qua_nguon_phat(trave['data']['LichPhat']['GioBatDau'], trave['data']['LichPhat']['DanhSachNguonPhat'])
                    kiem_tra_lich_phat_dang_phat(trave['data']['LichPhat'],nguonphat)
                    loiketnoi +=1
            if(trave['data']['statusPlay'] == 'stop'):
                DungBanTin()
                loiketnoi +=1
            if(trave['data']['statusPlay'] == 'dungbantintinh'):    
                phatbantintinh = False       
                DungBanTin()
                
            # if(trave['data']['statusPlay'] == 'phatbantintinh'):
            #     playBantinTinh(trave['data']['DataPlayBanTinTinh'], 0)
        demLoicallApiPing = 0
        nhapnhatLedConnectCallApiloi.stop()
        control_led_connect(1)
    except Exception as e:
        if demLoicallApiPing < 50:
            demLoicallApiPing+=1
        if demLoicallApiPing == 1:
            nhapnhatLedConnect.stop()
            nhapnhatLedConnectCallApiloi.start()
            #os.system("mpc stop")
        if demLoicallApiPing == 38:
            retartModul3g() 
        if demLoicallApiPing == 48:    
            os.system("(sudo systemctl restart myapp.service)")
        # if not run_main:
        #   nhapnhatLedConnectCallApiloi.stop()
        print('loi ping 20s ve server:' + str(e))
#Code sửa
# Kiểm tra trạng thái Play
def kiemtraTrangthaiPlay():
    global kiemtraPlay, demKiemtra, phatbantintinh, PhatKhanCap, status_congsuat,demloi

    if kiemtraPlay == 1:
        status_congsuat = gpio.input(congsuat_in)
        if (status_congsuat == 0):
            gpio.output(led_status,0)
            time.sleep(1)
            gpio.output(mute,0)
        if phatbantintinh == True or PhatBanTinNoiBo == True or PhatKhanCap == True:
            station_status = VLC_instance.get_Status_Play()
            # print("Trạng thái VLC hiện tại:", station_status)
            if station_status != 'play':
                demloi += 1
                if demloi == 3:
                    # print("Đang reset VLC...")
                    os.system("sudo systemctl restart myapp.service")
                    demloi = 0
            else:
                demloi = 0  # nếu đang play thì reset bộ đếm về 0
    # else:
    #     gpio.output(led_status,0)
        
    # if status_congsuat == 1:
    #     gpio.output(led_status,1)
    # else:
    #     gpio.output(led_status,0)
    #     gpio.output(on_loa,0)

    # station_status = VLC_instance.get_Status_Play()
    # if station_status == 'play':
    #     demKiemtra = 0  # Nếu trạng thái là 'play', đặt đếm kiểm tra về 0
    # elif station_status == 'stop' or station_status == 'Unknown':
    #     if kiemtraPlay == 1:
    #         if demKiemtra < 10:
    #             if PhatKhanCap == True:               
    #                 VLC_instance.Stop_VLC()
    #                 time.sleep(1)
    #                 playBantinTinh(DataPhatKhanCap, 1)                  
    #                 demKiemtra += 1
    #             else:
    #                 phatbantintinh = False
    #                 VLC_instance.Stop_VLC()
    #                 time.sleep(1) 
    #                 kiem_tra_thoi_gian_bat_dau() 
    #                 phatbantintinh = True
    #                 demKiemtra += 1
    #         else:
    #             pass
               
    #     else:
    #         pass
    # else:
    #     print(f"Trạng thái không xác định: {station_status}")

# Nhấp nháy Led Wifi
def led_nhapnhaywifi():
    global ledConnectStatus, demnhapnhay, demdung
    if(demnhapnhay < 4):
     gpio.output(led_connect,not ledConnectStatus)
     ledConnectStatus = not ledConnectStatus
     demnhapnhay+=1
     demdung=0
    if(demnhapnhay == 4):
     demdung+=1
    if(demdung == 16):
     demnhapnhay=0

# Led Connect Nhấp nháy
def ledConnectNhapnhay():
    global ledConnectStatus
    gpio.output(led_connect,not ledConnectStatus) 
    ledConnectStatus = not ledConnectStatus

# WatchDog
def watchdogStart():
  global watchdogStatus
  gpio.output(watchdog,not watchdogStatus)
  watchdogStatus = not watchdogStatus

# Nhấp nháy led connect báo lỗi
def ledConnectNhapnhayLoiCallApi():
    global ledConnectStatus
    gpio.output(led_connect,not ledConnectStatus) 
    ledConnectStatus = not ledConnectStatus

# lay Rssi, nha mang
def layRssiNhamang():
    global Rssi, dbm, TenNhaMang
    dataRssi = get_network_strength(ser)
    print('dataRssi', dataRssi)
    if dataRssi is not None:
        Rssi = dataRssi['signal']
        dbm = dataRssi['dbm']
    TenNhaMang = get_network_operator(ser)
 

############################################################
def playMPC(data, status, ThoiDiemBatDau, ThoiDiemKetThuc):
  if status == 1:
    os.system("mpc clear")
    os.system("mpc add '" + data + "'")
    os.system("mpc play")  
  else:  
    thoi_luong = ThoiDiemKetThuc - ThoiDiemBatDau
    thoi_gian_hien_tai = int(time.time())
    thoi_gian_con_lai = ThoiDiemKetThuc - thoi_gian_hien_tai
    if thoi_gian_con_lai > 0 and thoi_gian_con_lai < thoi_luong:
      thoi_gian_da_phat = thoi_luong - thoi_gian_con_lai
      thoi_gian_phat_gio = thoi_gian_da_phat // 3600
      thoi_gian_phat_phut = (thoi_gian_da_phat % 3600) // 60
      thoi_gian_phat_giay = (thoi_gian_da_phat % 3600) % 60
      thoi_gian_phat_gio = "{:02}".format(thoi_gian_phat_gio)  # Thêm số 0 nếu nhỏ hơn 10
      thoi_gian_phat_phut = "{:02}".format(thoi_gian_phat_phut)  # Thêm số 0 nếu nhỏ hơn 10
      thoi_gian_phat_giay = "{:02}".format(thoi_gian_phat_giay)  # Thêm số 0 nếu nhỏ hơn 10

      os.system("sudo mpc clear")
      os.system("sudo mpc add '" + data + "'")
      os.system("sudo mpc play")  
     # os.system("sudo mpc seek 00:05:00")
      #os.system(f"sudo mpc seek {thoi_gian_phat_gio}:{thoi_gian_phat_phut}:{thoi_gian_phat_giay}")

def stopMPC():
  os.system("mpc stop") 
  os.system("mpc clear")
# Phát bản tin tỉnh
def playBantinTinh(data, status):
  global thoiGianBatDauPhatTinh,  idLichPhatTinhDangPhat, idBanTinTinhDangPhat, PhatBanTinNoiBo, ThoiDiemKetThuc,  ThoiDiemBatDau,  NoiDungPhat, phatbantintinh, TrangThaiHoatDong, Video, kiemtraPlay, demKiemtra, trangthaiplay, led_status, urldangphat, tenchuongtrinh, kieunguon, thoiluong, tennoidung, diachingoidung, kieuphat, nguoitao, taikhoantao
  try:
    if PhatKhanCap == False:
        idLichPhatTinhDangPhat = data['LichPhatID']
        thoiGianBatDauPhatTinh = data['ThoiDiemBatDau']
        idBanTinTinhDangPhat = data['BanTinID']
    TrangThaiHoatDong = 0
    kiemtraPlay = 1      
    PhatBanTinNoiBo = False 
    if status == 1:
        VLC_instance.Play_VLC(data['NoiDung'])
    else:
        # thoi_luong = data['ThoiDiemKetThuc'] - data['ThoiDiemBatDau']
        # print("Thời lượng:", int(thoi_luong))
        # Lấy thời gian hiện tại
        thoi_gian_hien_tai = datetime.now()
        # Định dạng thời gian hiện tại thành timestamp (giây kể từ epoch)
        thoi_gian_hien_tai_timestamp = int(thoi_gian_hien_tai.timestamp() * 1000) 
       # Kiểm tra xem thời điểm hiện tại có nằm trong khoảng từ ThoiGianBatDau đến ThoiGianKetThuc không
        if data['ThoiDiemBatDau'] * 1000 <= thoi_gian_hien_tai_timestamp <= data['ThoiDiemKetThuc'] * 1000:
            thoi_gian_da_phat = thoi_gian_hien_tai_timestamp - (data['ThoiDiemBatDau'] * 1000)
            # print("Thời gian đã phát:", thoi_gian_da_phat) 
            lay_thoi_gian = thoi_gian_da_phat 
            giaydaqua =  lay_thoi_gian // 1000           
            if giaydaqua >= 10:             
                VLC_instance.Play_VLC_Set_Time(data['NoiDung'], lay_thoi_gian)
            else:              
                VLC_instance.Play_VLC(data['NoiDung'])

    phatbantintinh = True
    NoiDungPhat = data['NoiDung']
    ThoiDiemBatDau = data['ThoiDiemBatDau']
    ThoiDiemKetThuc = data["ThoiDiemKetThuc"]
    # kiemtraPlay = 1       
    # demKiemtra = 0
    control_led_status(1)
    # gui log ban tin ve server #
    urldangphat = data['NoiDung']
    tenchuongtrinh = data['TieuDe']
    kieunguon = "Bản tin HTTTN"
    thoiluong = data['ThoiLuong']
    tennoidung = data['NoiDungTomTat']
    diachingoidung = data['NoiDung']
    kieuphat = "Phát theo lịch"
    nguoitao = data['TacGia']['TenDayDu']
    taikhoantao = data['TacGia']['ButDanh']
    time.sleep(2) 
    station_status = VLC_instance.get_Status_Play()     
    data_object = {
      "type": station_status,
      "tenchuongtrinh": tennoidung,
      "tennoidung": diachingoidung,
    }
    json_data = json.dumps(data_object)
    client.publish(trangthaiplay,json_data)
    LogBanTin()
    #pingServer()
  except Exception as e:
    print("Loi phat ban tin tinh:" + str(e))

def playBantinTinh2(data):
  global ThoiDiemKetThuc,  ThoiDiemBatDau,  NoiDungPhat, phatbantintinh, TrangThaiHoatDong, Video, kiemtraPlay, demKiemtra, trangthaiplay, led_status, urldangphat, tenchuongtrinh, kieunguon, thoiluong, tennoidung, diachingoidung, kieuphat, nguoitao, taikhoantao
  try:
    # os.system("mpc stop") 
    # os.system("mpc clear")
    # os.system("mpc add '" + data['NoiDung'] + "'")
    # os.system("mpc play")        
    # print('ok clear')
    # MPC.add('https://storage-ttn.quangnam.gov.vn/2023//09//12//THOI_SU_THU_2M/b5cc0822a37f4abca1d17937cdb6bc27.mp3')  
    # print('ok add')
    # MPC.play(0)     
    # MPC.seek(0,thoi_gian_da_phat)           
    # print('ok play')
    playMPC(data['NoiDung'],0, data['ThoiDiemBatDau'],data['ThoiDiemKetThuc'] )
    TrangThaiHoatDong = 0
    phatbantintinh = True
    NoiDungPhat = data['NoiDung']
    ThoiDiemBatDau = data['ThoiDiemBatDau']
    ThoiDiemKetThuc = data["ThoiDiemKetThuc"]
    # kiemtraPlay = 1       
    # demKiemtra = 0
    station = subprocess.check_output("mpc current", shell=True ).decode("utf-8")
    lines=station.split(":")
    length = len(lines) 
    if length==1:
      line1 = lines[0]
      line1 = line1[:-1]
      line2 = "No additional info: "
    else:
      line1 = lines[0]
      line2 = lines[1]
    line2 = line2[:42]
    line2 = line2[:-1]
    #trap no station data
    if line1 =="":
      line2 = "Press PLAY or REFRESH"
      station_status = "stop"   
    else:
      station_status = "play"     
    client.publish(trangthaiplay,station_status)
    gpio.output(led_status,1)
    # gui log ban tin ve server #
    urldangphat = data['NoiDung']
    tenchuongtrinh = data['TieuDe']
    kieunguon = "Bản tin HTTTN"
    thoiluong = data['ThoiLuong']
    tennoidung = data['NoiDungTomTat']
    diachingoidung = data['NoiDung']
    kieuphat = "Phát theo lịch"
    nguoitao = data['TacGia']['TenDayDu']
    taikhoantao = data['TacGia']['ButDanh']
    # volume #
    volume = subprocess.check_output("mpc volume", shell=True ).decode("utf-8")
    volume = volume[8:]
    volume = volume[:-1]
    ## luu log ban tin
    thoigianphat = time.time()
    dataLog = {
      'urldangphat': urldangphat,
      'id': id,  
      'tenchuongtrinh': tenchuongtrinh,
      'kieunguon': kieunguon,
      'thoiluong': thoiluong,
      'tennoidung': tennoidung,
      'diachingoidung': diachingoidung,
      'kieuphat': kieuphat,
      'nguoitao': nguoitao,
      'taikhoantao': taikhoantao,
      'thoigianphat': int(thoigianphat) ,
      'volume': volume,
    }
   
    try:
      responsePingtest = requests.post(domainLogbantin, json = dataLog, timeout=4)
    except:
      print('loi call api log ban tin ve server ')
    ### ping ban tin dang phat ve server ###
   
    dataPing = {
      'phatbantintinh': phatbantintinh,
      'url': urldangphat,
      'id': id,
      'trangthai': station_status,   
      'tenchuongtrinh': tenchuongtrinh,
      'kieunguon': kieunguon,
      'thoiluong': thoiluong,
      'tennoidung': tennoidung,
      'diachingoidung': diachingoidung,
      'kieuphat': kieuphat,
      'nguoitao': nguoitao,
      'taikhoantao': taikhoantao,
      'trangthaiplay': trangthaiplay,
      'ThoiDiemKetThuc': ThoiDiemKetThuc
    }
   
    responsePingtest = requests.post(domainPing, json = dataPing, timeout=5)
  except Exception as e:
    print("loi ping ban tin dang phat play ve server:" + str(e))

#################### ham stop ban tin tinh ##############################
def stopBanTinTinh():
  global ThoiDiemBatDau, phatbantintinh, TrangThaiHoatDong, NoiDungPhat, Status, Video,  kiemtraPlay, trangthaiplay, led_status, urldangphat, tenchuongtrinh, kieunguon, thoiluong, tennoidung, diachingoidung, kieuphat, nguoitao, taikhoantao
  try:
    # os.system("mpc stop") 
    # os.system("mpc clear")
    
    # MPC.stop()  
    # MPC.delete(0) 
    # MPC.clear()
    stopMPC()
    gpio.output(led_status,0)
    phatbantintinh = False
    kiemtraPlay = 0
    TrangThaiHoatDong = 2
    ThoiDiemBatDau = 0
    station = subprocess.check_output("mpc current", shell=True ).decode("utf-8")
    lines=station.split(":")
    length = len(lines) 
    if length==1:
      line1 = lines[0]
      line1 = line1[:-1]
      line2 = "No additional info: "
    else:
      line1 = lines[0]
      line2 = lines[1]
    line2 = line2[:42]
    line2 = line2[:-1]
  #trap no station data
    if line1 =="":
      line2 = "Press PLAY or REFRESH"
      station_status = "stop"   
    else:
      station_status = "play" 
    client.publish(trangthaiplay,station_status)
    urldangphat = ''
    tenchuongtrinh = ''
    kieunguon = ''
    thoiluong = ''
    tennoidung = ''
    diachingoidung = ''
    kieuphat = ''
    nguoitao = ''
    taikhoantao = ''
    Status = "false"
    NoiDungPhat = ''
    ### ping ban tin dang phat ve server ###
    dataPing = {
      'phatbantintinh': phatbantintinh,
      'url': urldangphat,
      'id': id,
      'trangthai': station_status,   
      'tenchuongtrinh': tenchuongtrinh,
      'kieunguon': kieunguon,
      'thoiluong': thoiluong,
      'tennoidung': tennoidung,
      'diachingoidung': diachingoidung,
      'kieuphat': kieuphat,
      'nguoitao': nguoitao,
      'taikhoantao': taikhoantao,
      'trangthaiplay': trangthaiplay,
    }
    
    responsePingtest = requests.post(domainPing, json = dataPing, timeout=5)
  except:
    print('loi ping ban tin dang phat stop ve server ')
  
#### phát bản tin kế tiếp ###
def phatbantinKetiepTrongDanhSach(bantins):
  global Playing_ChuyenBai, IndexBanTinKeTiep, BanTinKeTiep, ChuyenBanTin, DanhSachBanTinDung
  if len(bantins) > 0:
    current_time = int(time.time())
    for item in bantins:
        for ngayphat_index, ngayphat in enumerate(item["DanhSachNgayPhat"]):
            for thoidiemphat in ngayphat["ThoiDiemPhat"]:
                thoi_gian_bat_dau = thoidiemphat["ThoiGianBatDau"]
                thoi_gian_ket_thuc = thoidiemphat["ThoiGianKetThuc"]                   
                if current_time == thoi_gian_bat_dau:
                    if (Playing_ChuyenBai == False):                   
                      if(ngayphat_index != 0):
                        Playing_ChuyenBai = True 
                        IndexBanTinKeTiep += 1
                        item['ThoiDiemBatDau'] = thoi_gian_bat_dau
                        item['ThoiDiemKetThuc'] = thoi_gian_ket_thuc
                        playBantinTinh(item)
                        api_nhatkybantinTinh(item)
                    # Thêm mã lệnh để chạy "mpc play" ở đây                   
                if current_time == thoi_gian_ket_thuc:
                    if (Playing_ChuyenBai == True):                     
                      stopBanTinTinh()
                      Playing_ChuyenBai = False 
                      del BanTinKeTiep[ngayphat_index]
                      IndexBanTinKeTiep -= 1
                      if(len(BanTinKeTiep) == IndexBanTinKeTiep):                     
                        ChuyenBanTin = False
                        BanTinKeTiep = []
                        IndexBanTinKeTiep = 0
     
#### phát khẩn cấp bản tin tỉnh ### 
def PhatKhanCapBanTinTinh(bantin):   
  global PhatKhanCap, DataPhatKhanCap, phatbantintinh
  current_time = int(time.time())   
  if current_time == bantin["ThoiDiemKetThuc"]:
    if (PhatKhanCap == True):   
      # stopBanTinTinh()
      PhatKhanCap = False
      phatbantintinh = False
      DataPhatKhanCap = {}
      DungBanTin()
      kiem_tra_thoi_gian_bat_dau()

################# ham dieu khien volume ####################
def setVolume(volume_level):
    global amluong
  # Sử dụng lệnh amixer để đặt âm lượng
    amluong = volume_level
    #command = f"amixer set Master {volume_level}%"
    #os.system(command)
   
    VLC_instance.Set_Volume(volume_level)
############################################################

############ khoi dong lai modul 3g ########################
def retartModul3g():
    global demRestartModul3g
    gpio.output(kich_modul4g,0) 
    time.sleep(20)
    gpio.output(kich_modul4g,1) 
    demRestartModul3g = 0
############################################################

############### on_disconnect ##############################
def on_disconnect(client, userdata, flags, rc=0):
    m="DisConnected flags"+"result code "+str(rc)+"client_id  "
    print(m)
    client.connected_flag=False
############################################################

#################### connect MQTT ##########################
def on_connect(client, userdata, flags, rc):
    global dbm, Rssi, TenNhaMang, TrangThaiKetNoi, demLoicallApiPing, yeucauguidulieu, updatecode, dieukhienvolume, dieukhienplay, maxacthuc, chedoRetartModul3g, demRestartModul3g, demLoicallApiPing
    if rc==0:
        print("connected OK Returned code=",rc)
        demLoicallApiPing = 0
        chedoRetartModul3g = False
        demRestartModul3g = 0      
        #Flag to indicate success
        client.subscribe(dieukhienvolume) 
        client.subscribe(updatecode)
        client.subscribe(dieukhienplay)
        client.subscribe(yeucauguidulieu)
        client.subscribe(reset)
        client.connected_flag=True
        nhapnhatLedConnect.stop()
        nhapnhatLedConnectCallApiloi.stop()
        control_led_connect(1)
        """ call API xac nhan ket noi """
       # ip = requests.get('https://api.ipify.org').text
        # eth_connected = has_ipv4_address("eth0")
        # wifi_connected = has_ipv4_address("wlan0")
        # print(f"eth0 connected: {eth_connected}")
        # print(f"wlan0 connected: {wifi_connected}")
        ketnoimang = has_ipv4_address('eth0')      
        if ketnoimang == True:
            TrangThaiKetNoi = 'Ethernet'
           # layThongtinMang.stop()
        else:
            TenNhaMang = get_network_operator(ser)
            dataRssi = get_network_strength(ser)
            if dataRssi is not None:
                Rssi = dataRssi['signal']
                dbm = dataRssi['dbm']
            TrangThaiKetNoi = '4G,-10dbm'

        
        # print(TenNhaMang)
        # print(Rssi)

        dataXacnhanketnoi = {
          'xacnhanketnoi': xacnhanketnoi,
          'ip': get_ip_address(),
          'phienban': phienban,   
          'version': version,
          'MainBoard': MainBoard,
          'LoaiMangKetNoi': '0' if ketnoimang else '1',
          'TenNhaMang': TenNhaMang,
          'Rssi': Rssi,
          'dbm': dbm,
          'LoaiMang': LoaiMang
        }
      
        api_xacnhanketnoi(dataXacnhanketnoi)           
    else:
        print("Bad connection Returned code=",rc)
        client.bad_connection_flag=True
###########################################################

############### ham hien thi log ##########################
def on_log(client, userdata, level, buf):
    print("log: ",buf)
###########################################################

########### nhan tin nhan tu broker #######################
def on_message(client, userdata, msg):
    global linkS3, DungBanTinTinh, amluong, LichPhatDangNhan, TrangThaiHoatDong, PhatKhanCap, DataPhatKhanCap, phatbantintinh, IndexBanTinKeTiep,  Playing_ChuyenBai, ChuyenBanTin, BanTinKeTiep, DanhSachBanTinDung, IdLichDangPhat, ThoiDiemBatDau, NoiDungPhat,  kiemtraPlay, updatecode, dieukhienvolume, dieukhienplay, demKiemtra, guidulieu, yeucauguidulieu, userName, password, domainPing, imel, tenthietbi, madiaban, tendiaban, lat, lng, Status, Video, khoaguidulieu
    themsg = msg.payload.decode("utf-8")
    topic = msg.topic
    #### nhan lenh tu server ####
    #### update code ####
    if topic == updatecode:
      try:
        data = themsg.split() 
        if data[0] == id:
          control_led_status(0)
          os.system("(cd /root/h3_m1_plus && git pull https://phamdung1211:'"+ data[1] + "'@bitbucket.org/phamdung1211/h3_m1_plus.git && sudo shutdown -h now)")
      except:
        print('loi')
    #### khoi dong lai thiet bi ####
    if topic == reset:
      if themsg == id:
        control_led_status(0)
        os.system("(sudo shutdown -h now)")
    #### dieu chinh am luong ####
    if topic == dieukhienvolume: 
       try:
        data = json.loads(themsg)
        if data['deviceId'] == id:
          #setVolume(data['volume'])
          amluong = int(data['volume']) 
          VLC_instance.Set_Volume(data['volume'])
       except Exception as e:
        print('Loi set am luong:' + str(e))
       
    #### play ban tin  ####
    if topic == dieukhienplay: 
      try:
        data = json.loads(themsg)  
        if data['status'] == "play":
          if data['deviceId'] ==  id:
            if(phatbantintinh == False and PhatKhanCap == False):
                pass            
              
        #### stop luong ####
        if data['status'] == "stop":
            if data['deviceId'] == id:
              if(phatbantintinh == False and PhatKhanCap == False):              
                  pass
        
        # nhận lịch phát nội bộ
        if data['status'] == "nhan-lich-phat":
            delete_job() 
            LichPhatDangNhan = data['LichPhat']
            nguonphat = lap_qua_nguon_phat(data['LichPhat']['GioBatDau'], data['LichPhat']['DanhSachNguonPhat'])
            kiem_tra_lich_phat_dang_phat(data['LichPhat'],nguonphat)
           
        # dừng lịch phát nội bộ
        if data['status'] == "huy-lenh-phat-ngay":
            delete_job() 
            DungBanTin()
            if data['LichPhat'] == '':              
                pass                         
            else:
                LichPhatDangNhan = data['LichPhat']
                nguonphat = lap_qua_nguon_phat(data['LichPhat']['GioBatDau'], data['LichPhat']['DanhSachNguonPhat'])
                kiem_tra_lich_phat_dang_phat(data['LichPhat'],nguonphat)
      except Exception as e:
          print("Loi nhận MQTT:" + str(e))
    ### gui log ban tin ve tinh ####
    if topic == yeucauguidulieu:
      try:
        data = json.loads(themsg) 
        # điều khiển âm lượng
        if(data['command'] == 'amluong'):
          amluong = int(data['volume']) 
          VLC_instance.Set_Volume(data['volume'])
        # Dừng phát nội dung
        if(data['command'] == 'DungPhatNoiDung'):            
          #if(PhatKhanCap == False):
            # Dừng tất cả bản tin
            if(data['ThamSo'] == '0'):
                DataPhatKhanCap = {}
                PhatKhanCap = False
                phatbantintinh = False
                ChuyenBanTin = False
                DungBanTinTinh = True
                BanTinKeTiep = []
                DungBanTin()
                set_all_status_to_true()
                jobs = scheduler.get_jobs()
                for job in jobs:
                    if job.id not in ["check_lich_phat_tinh", "check_lich_dung_tinh"]:
                        scheduler.remove_job(job.id)
                        print("Removed job ID:" + str(job.id))
              
                kiem_tra_thoi_gian_bat_dau() 
               
            # dừng bản tin hiện tại, phát bản tin tiếp theo nếu trong lịch phát còn bản tin
            if(data['ThamSo'] == '1'):            
                if phatbantintinh == True and PhatKhanCap == False:                 
                    jobs = scheduler.get_jobs()                   
                    lichPhat = load_data_from_file(file_path)
                    banTinTiepTheo =  next_ban_tin(lichPhat, idLichPhatTinhDangPhat, idBanTinTinhDangPhat)           
                    #print(banTinTiepTheo)
                    with open('lichphatTinh.json', 'w') as json_file:
                        json.dump(banTinTiepTheo, json_file, indent=4)
                    for job in jobs:
                        if job.id not in ["check_lich_phat_tinh", "check_lich_dung_tinh"]:
                            scheduler.remove_job(job.id)
                    phatbantintinh = False
                    DungBanTinTinh = False
                    DungBanTin()
                    kiem_tra_thoi_gian_bat_dau() 

            # dưng tạm thời bản tin
            if(data['ThamSo'] == '2'):
                #pass
                VLC_instance.Pause_VLC()
              # os.system("mpc pause")    
                TrangThaiHoatDong = 1      
            # phát lại bản tin hiện tại
            if(data['ThamSo'] == '3'):
               #pass
                VLC_instance.RePlay()
                #playBantinTinh(data, 1)
              # os.system("mpc play")
                TrangThaiHoatDong = 0
        # Khởi động lại thiết bị
        if(data['command'] == 'khoidonglai'):
            os.system("(sudo shutdown -h now)")
        
        # phát khẩn cấp
        if(data['command'] == 'phatkhancap'):
          TrangThaiHoatDong = 0       
          api_nhatkybantinTinh(data)
          DataPhatKhanCap = data
          PhatKhanCap = True
          playBantinTinh(data, 1)
       
         
        # phát bản tin tỉnh
        if(data['command'] == 'PhatBanTinTinh'):   
          if(PhatKhanCap == False):
            if(data["index"] == 0):
              if data["LichPhatID"] in DanhSachBanTinDung:
                DanhSachBanTinDung.remove(data["LichPhatID"])
              IdLichDangPhat = data["LichPhatID"]
              BanTinKeTiep = data["BanTinKeTiep"]
              playBantinTinh(data, 1)
              api_nhatkybantinTinh(data)
            else:
              if data["LichPhatID"] not in DanhSachBanTinDung:
                IdLichDangPhat = data["LichPhatID"]
                BanTinKeTiep = data["BanTinKeTiep"]
                playBantinTinh(data, 1)
                api_nhatkybantinTinh(data)
        # Dừng bản tin tỉnh
        if(data['command'] == 'DungBanTinTinh'):
          if( PhatKhanCap == False):
            if data["LichPhatID"] not in DanhSachBanTinDung:    
              DungBanTin()
              phatbantintinh = False
            if(data['XoaLich'] == True):        
              if data["LichPhatID"] in DanhSachBanTinDung:
                DanhSachBanTinDung.remove(data["LichPhatID"])
              IdLichDangPhat = ''   
        # Lưu lịch phát
        if(data['command'] == 'Luu_Lich_Phat_Tinh'):                
            schedule = add_index_and_status(data["DanhSachBanTin"])     
            # Sắp xếp dữ liệu           
            with open('lichphatTinh.json', 'w') as json_file:
                json.dump(schedule, json_file, indent=4)
            # Xóa tất cả các job ngoại trừ các job có id "check_lich_phat_tinh" và "check_lich_dung_tinh"
            jobs = scheduler.get_jobs()
            for job in jobs:
                if job.id not in ["check_lich_phat_tinh", "check_lich_dung_tinh"]:
                    scheduler.remove_job(job.id)
            kiem_tra_thoi_gian_bat_dau() 
            api_nhatkyTaomoiBanTinTinh(data)
        
        # Lưu lịch phát
        if(data['command'] == 'Huy_Lich_Phat_Tinh'):
            schedule = add_index_and_status(data["DanhSachBanTin"])           
            with open('lichphatTinh.json', 'w') as json_file:
                json.dump(schedule, json_file, indent=4)
            # Xóa tất cả các job ngoại trừ các job có id "check_lich_phat_tinh" và "check_lich_dung_tinh"
            jobs = scheduler.get_jobs()
            for job in jobs:
                if job.id not in ["check_lich_phat_tinh", "check_lich_dung_tinh"]:
                    scheduler.remove_job(job.id)
            DungBanTin()
            kiem_tra_thoi_gian_bat_dau() 
            api_nhatkyHuyBanTinTinh(data)
            
        ##### console #########
        if(data['command'] == 'console'):
          if(data['id'] == id):
            os.system(data['data'])
        ## Kieerm tra loi tai nay
        ##### Ping Device #########
        if(data['command'] == 'ping-device'):
                if(data['statusPlay'] == 'dungbantintinh'):    
                    phatbantintinh = False       
                    DungBanTin()
                if(data['statusPlay'] == 'play'):  
                    linkS3 = data['urlS3'] 
                    status = player.get_state_2()
                    if status == 'Opening':                 
                        pass
                    else:                  
                    # play bản tin  
                       # print('nhan ban tin từ ping server 20s')
                        VLC_instance.Stop_VLC()
                        LichPhatDangNhan = data['LichPhat']
                        nguonphat = lap_qua_nguon_phat(data['LichPhat']['GioBatDau'], data['LichPhat']['DanhSachNguonPhat'])
                        kiem_tra_lich_phat_dang_phat(data['LichPhat'],nguonphat)
                      
                if(data['statusPlay'] == 'stop'):
                    DungBanTin()
                 
            
      except Exception as e:
        print('loi nhan lenh MQTT:' + str(e))
###########################################################

def validate_json_Wifi(file_path):
    """
    Hàm kiểm tra tính hợp lệ của một file JSON.
    :param file_path: Đường dẫn tới file JSON cần kiểm tra.
    :return: Trả về dữ liệu JSON nếu hợp lệ, None nếu không hợp lệ.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
             # Ví dụ truy cập các trường
            # Lấy SSID và PASSWORD từ file JSON
            ssid = data.get('ssid', '').strip()
            password = data.get('password', '').strip()
            # Kiểm tra SSID và PASSWORD có rỗng không
            if not ssid:
                print("SSID không được để trống.")
                return
            if not password:
                print("Password không được để trống.")
                return
            print(f"Kết nối tới Wi-Fi: {ssid}")
             # Thực hiện kết nối Wi-Fi
            # Đưa SSID và password vào dấu ngoặc kép để xử lý khoảng cách
            ssid_quoted = f'"{ssid}"'
            password_quoted = f'"{password}"'
            # Thực hiện kết nối Wi-Fi
            try:
                result = subprocess.run(
                    ['nmcli', 'dev', 'wifi', 'connect', ssid_quoted, 'password', password_quoted, 'ifname', 'wlan0'],
                    check=True,
                    text=True,
                    capture_output=True,
                    shell=True  # Cần shell=True để xử lý các chuỗi có dấu ngoặc kép
                )
                print("Kết nối thành công:", result.stdout)
            except subprocess.CalledProcessError as e:
                print("Không thể kết nối Wi-Fi. Lỗi:", e.stderr)

    except json.JSONDecodeError as e:
        print("File JSON không hợp lệ:", e)
        return None

CLEAN_SESSION=False
VLC_instance = VLC()
player = VLCPlayer()
#broker="iot.eclipse.org" #use cloud broker
client = mqtt.Client()    #create new instance
#client.on_log=on_log #client logging
mqtt.Client.connected_flag=False #create flags
mqtt.Client.bad_connection_flag=False #
mqtt.Client.retry_count=0 #
client.on_connect=on_connect        #attach function to callback
client.will_set("device/offline", payload=id, qos=1, retain=False)
client.on_disconnect=on_disconnect
client.on_message = on_message
nhapnhatLedConnect = RepeatedTimer(1, ledConnectNhapnhay)
nhapnhatLedConnectCallApiloi = RepeatedTimer(0.2, ledConnectNhapnhayLoiCallApi)
nhapnhatLedConnectCallApiloi.stop()
kiemtraPlay = RepeatedTimer(10, kiemtraTrangthaiPlay)
callApipingServer = RepeatedTimer(20, pingServer)
pingApiTinh = RepeatedTimer(60, pingTinh)
watchdog_start = RepeatedTimer(1, watchdogStart)
nhapnhay_wifi = RepeatedTimer(0.15, led_nhapnhaywifi)
ketnoimang = has_ipv4_address('eth0')

if ketnoimang != True:
   layThongtinMang = RepeatedTimer(60, layRssiNhamang)
nhapnhay_wifi.stop()
#setVolume(amluong)
# speedtest_start = RepeatedTimer(60, get_speedtest)
#pwmLed = RepeatedTimer(1, pwm_led)
run_main=False
run_flag=True
# Khởi tạo lịch trình

scheduler = BackgroundScheduler()
# check_lich_phat_tinh = scheduler.add_job(kiem_tra_thoi_gian_bat_dau, 'cron', minute='*/1')
# check_lich_dung_tinh = scheduler.add_job(kiem_tra_thoi_gian_ket_thuc, 'cron', minute='*/1')
scheduler.add_job(kiem_tra_thoi_gian_bat_dau, 'cron', minute='*/1', id="check_lich_phat_tinh")
scheduler.add_job(kiem_tra_thoi_gian_ket_thuc, 'cron', minute='*/1', id="check_lich_dung_tinh")
scheduler.start()
ser = serial.Serial('/dev/ttyS1', 115200, timeout=1)
# kết nối wifi
# Đọc file JSON

file_path = 'wifiConfig.json'
# kết nối wifi
#validate_json_Wifi(file_path)


while run_flag:
    while not client.connected_flag and client.retry_count<3:
        count=0 
        run_main=False
        try:
            print("connecting ",domainMqtt)         
            client.connect(domainMqtt,portMqtt,60)      
            break #break from while loop
        except:           
            # kiểm soát mất diện
            if gpio.input(mat_nguon) == 0:     
                if TrangThaiGuiMatDien == True or TrangThaiGuiMatDien == None:   
                    ThoiGianMatDien = time.time()  
                    data_object = {
                        "type": "mat-dien",
                        "ThoiGianMatDien": int(ThoiGianMatDien),
                    }
                    json_data = json.dumps(data_object)       
                    client.publish(trangthaiplay,json_data)
                    ketquaMatdien = api_TrangThaiMatDien(False,  ThoiGianMatDien)                               
                    if ketquaMatdien == True:
                        TrangThaiGuiMatDien = False  
             
                # có điện
                else:     
                    if TrangThaiGuiMatDien == False or TrangThaiGuiMatDien == None:        
                        ThoiGianMatDien = time.time()  
                        data_object = {
                            "type": "co-dien",
                            "ThoiGianMatDien": int(ThoiGianMatDien),
                        }
                        json_data = json.dumps(data_object)       
                        client.publish(trangthaiplay,json_data)
                        ketquaMatdien = api_TrangThaiMatDien(True, ThoiGianMatDien)                     
                        if ketquaMatdien == True:
                            TrangThaiGuiMatDien = True  
            print("connection attempt failed will retry")         
            # nhapnhatLedConnect.start()
            # nhapnhatLedConnectCallApiloi.stop()
            client.retry_count+=1         
            if(client.retry_count == 2):
              retartModul3g()
              print('khoi dong lai modul lan dau...')
            #if client.retry_count>3:
                #print('thoat')
                #run_flag=False
    if not run_main:   
        client.loop_start()
        while True:
           
            # kiểm soát mất diện
            if gpio.input(mat_nguon) == 0:     
                if TrangThaiGuiMatDien == True or TrangThaiGuiMatDien == None:   
                    ThoiGianMatDien = time.time()  
                    data_object = {
                        "type": "mat-dien",
                        "ThoiGianMatDien": int(ThoiGianMatDien),
                    }
                    json_data = json.dumps(data_object)       
                    client.publish(trangthaiplay,json_data)
                    ketquaMatdien = api_TrangThaiMatDien(False,  ThoiGianMatDien)                    
                    if ketquaMatdien == True:
                        TrangThaiGuiMatDien = False  
             
                # có điện
                else:     
                    if TrangThaiGuiMatDien == False or TrangThaiGuiMatDien == None:        
                        ThoiGianMatDien = time.time()  
                        data_object = {
                            "type": "co-dien",
                            "ThoiGianMatDien": int(ThoiGianMatDien),
                        }
                        json_data = json.dumps(data_object)       
                        client.publish(trangthaiplay,json_data)
                        ketquaMatdien = api_TrangThaiMatDien(True,  ThoiGianMatDien)                      
                        if ketquaMatdien == True:
                            TrangThaiGuiMatDien = True  
            if client.connected_flag: #wait for connack
                client.retry_count=0 #reset counter
                run_main=True
                break
            # if count>6 or client.bad_connection_flag: #don't wait forever
            #   demRestartModul3g+=1
            #   if demRestartModul3g >= 900:                  
            #     print('reset lai modul 3g..')
            #     retartModul3g()                  
            # time.sleep(1)
            count+=1
    if run_main: 
        try:          
            # print('trạng thái:', player.get_state_2())        
            if(PhatKhanCap == True):
              PhatKhanCapBanTinTinh(DataPhatKhanCap)
            if(ChuyenBanTin == True):
              phatbantinKetiepTrongDanhSach(BanTinKeTiep)
            time.sleep(1)           
        except(KeyboardInterrupt):
            print("keyboard Interrupt so ending")
            DungBanTin()
            os._exit(0)
            #run_flag=False
    # Mất điện
    if gpio.input(mat_nguon) == 0:     
        if TrangThaiGuiMatDien == True or TrangThaiGuiMatDien == None:   
          ThoiGianMatDien = time.time()  
          data_object = {
              "type": "mat-dien",
              "ThoiGianMatDien": int(ThoiGianMatDien),
          }
          json_data = json.dumps(data_object)           
          client.publish(trangthaiplay,json_data)       
          ketquaMatdien = api_TrangThaiMatDien(False,  ThoiGianMatDien)   
          if ketquaMatdien == True:
             TrangThaiGuiMatDien = False  
             
    # có điện
    else:     
        if TrangThaiGuiMatDien == False or TrangThaiGuiMatDien == None:        
          ThoiGianMatDien = time.time()  
          data_object = {
              "type": "co-dien",
              "ThoiGianMatDien": int(ThoiGianMatDien),
          }
          json_data = json.dumps(data_object)               
          client.publish(trangthaiplay,json_data)       
          ketquaMatdien = api_TrangThaiMatDien(True,  ThoiGianMatDien)        
          if ketquaMatdien == True:
             TrangThaiGuiMatDien = True       
    if gpio.input(phim_wifi) == 1:
      KiemTraPhim()
    
print("quitting")
# client.disconnect()
# client.loop_stop()
