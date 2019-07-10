# coding:utf-8

import requests
import re
import time
import csv
import json

# 全局变量
expires_time = 0
access_token = 'your Token'   


# 获取 accessToken， 超时后才会自动获取
def getAccessToken():

	global access_token
	global expires_time 

	cur_time = time.time()

	if cur_time >= expires_time: 
		url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=yourCorpId&corpsecret=yourSecret'
		token_text=requests.get(url).text
		print(token_text)
		access_token = json.loads(token_text)['access_token']
		expires_in = json.loads(token_text)['expires_in']
		expires_time = cur_time + expires_in


# 企业微信推送消息
def pushMsg_WX(sendUsr,sendContent,sendType):
	
	# print(access_token)
	global runOnce

	if runOnce == 0 :
		getAccessToken()

	url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + access_token
	logMonitor('消息发送API:', url, enable = 1)

	Msg = {"agentid" : 1000042,"safe":0}
	Msg["touser"] = sendUsr

	if sendType == 1:
		Msg["msgtype"] = "text"
		Msg["text"] = {'content':sendContent}
	elif sendType == 2:
		Msg["msgtype"] = "textcard"
		Msg["textcard"] = sendContent

	logMonitor('消息发送入参:', Msg, enable = 1)

	request_result = requests.post(url,json.dumps(Msg))

	logMonitor('发送消息返回结果:', request_result.text, enable = 1)


# 天气异常提醒 [北京]
# 异常：
# * 今日当前城市有雨/雪/雾，影响履约，预计出现时间 8点 - 11点
# * 今日最高气温 33℃，天气炎热，达达热天工作，注意安抚达达
# * 今日有雾，影响达达骑行
# * 今日有大风，注意提醒达达道路骑行安全
# 请各位城市对应同学关注哦~~
# 当日气象局预警提醒：xxxxx
# 日期:2019-12-22
def dealSendTxt(city,weather):

	content_header = '天气异常提醒 [' + city + ']\n'
	
	# alarmFlag 是否需要发送异常提醒
	alarmFlag = False 
	
	
	#判断高温
	max_tem = int(re.findall("\d+",weather['tem1'])[0])
	if max_tem > 30:
		alarmFlag = True
		content_body_tem = '* 今日最高气温 '+ str(max_tem) + '℃，天气炎热，达达热天配送辛苦，注意安抚达达 \n'
	else:
		content_body_tem = ''

	#判断气象局发布的气象预警
	try:
		alarm_content = weather['alarm']["alarm_content"]
	except :
		logMonitor('错误发生','alarm_content 无返回')
	finally:
		alarm_content = ''
	if alarm_content :
		alarmFlag = True
		content_body_alarm = '气象局预警提醒：\n'+ alarm_content + '\n'
	else:
		content_body_alarm = ''
	

	# 判断分时段的雨量
	hour_weathers  = weather['hours'] # 小时天气
	content_body_rain = ''
	for ll in range(len(hour_weathers)):
		hour = int(hour_weathers[ll]['day'][-3:-1]) #抓换成时间数字
		wea = hour_weathers[ll]['wea']
		logMonitor('wea & hour',wea + ' \ ' + str(hour))

		if hour >= 8 and hour < 23 and wea.find('雨') >=0 :
			alarmFlag = True
			content_body_rain = content_body_rain + str(hour) + '点，'

	if content_body_rain:
		content_body_rain = '* 当前城市今日有雨，影响履约，预计有雨出现时间: ' + content_body_rain + '\n'
	else:
		content_body_rain = ''	



	# 日期
	date = time.strftime("%Y-%m-%d", time.localtime())

	content_tail = '\n点击进入查看<a href=\"https://xw.tianqi.qq.com\">天气详情</a>。\n注：每日早上8点发送当日负责的相关城市天气预警情况。'

	# 判断是否需要发送消息，如果需要返回消息
	if alarmFlag:
		content_body = content_header + content_body_rain + content_body_tem + '日期：' + date  + content_tail
		return content_body
	else:
		return 0

# 天气异常提醒 [北京]
# 异常：
# * 今日当前城市有雨/雪/雾，影响履约，预计出现时间 8点 - 11点
# * 今日最高气温 33℃，天气炎热，达达热天工作，注意安抚达达
# * 今日有雾，影响达达骑行
# * 今日有大风，注意提醒达达道路骑行安全
# 请各位城市对应同学关注哦~~
# 当日气象局预警提醒：xxxxx
# 日期:2019-12-22
def dealSendCardtext(weather):

	# alarmFlag 是否需要发送异常提醒
	alarmFlag = False 
	
	
	#判断高温
	max_tem = int(re.findall("\d+",weather['tem1'])[0])
	if max_tem > 30:
		alarmFlag = True
		content_body_tem = '<div class = \"normal\" >* 今日最高气温 '+ str(max_tem) + '℃，天气炎热，达达热天配送辛苦，注意安抚达达 </div>'
	else:
		content_body_tem = ''

	#判断气象局发布的气象预警
	try:
		alarm_content = weather['alarm']["alarm_content"]
	except :
		logMonitor('错误发生','alarm_content 无返回')
	finally:
		alarm_content = ''
	if alarm_content :
		alarmFlag = True
		# content_body_alarm = '气象局预警提醒：\n'+ alarm_content + '\n'
		content_body_alarm = '<div class = \"normal\" > 气象局预警提醒：'+ alarm_content + '</div>'
	else:
		content_body_alarm = ''
	

	# 判断分时段的雨量
	hour_weathers  = weather['hours'] # 小时天气
	content_body_rain = ''
	for ll in range(len(hour_weathers)):
		hour = int(hour_weathers[ll]['day'][-3:-1]) #抓换成时间数字
		wea = hour_weathers[ll]['wea']
		print('@',str(hour),'点, 天气状态状况为: ',wea) 

		if hour >= 8 and hour < 23 and wea.find('雨') >=0 :
			alarmFlag = True
			content_body_rain = content_body_rain + str(hour) + '点，'

	if content_body_rain:
		# content_body_rain = '* 当前城市今日有雨，影响履约，预计有雨出现时间: ' + content_body_rain + '\n'
		content_body_rain = '<div class = \"normal\" >* 当前城市今日有雨，影响履约，预计有雨出现时间: '+ content_body_rain + '</div>'
	else:
		content_body_rain = ''	



	# 日期
	date = '<div class = \"gray\" >'+ time.strftime("%Y年%m月%d日", time.localtime()) + '</div><div> </div>'
	

	content_tail = '<div> </div> <div class = \"gray\" >注：每日早上8点发送当日负责的相关城市天气预警情况。</div>'

	# 判断是否需要发送消息，如果需要返回消息
	if alarmFlag:
		content_body = date + content_body_rain + content_body_tem + content_tail
		return content_body
	else:
		return 0




# 天气异常提醒 [北京]
# 异常：
# * 今日当前城市有雨/雪/雾，影响履约，预计出现时间 8点 - 11点
# * 今日最高气温 33℃，天气炎热，达达热天工作，注意安抚达达
# * 今日有雾，影响达达骑行
# * 今日有大风，注意提醒达达道路骑行安全
# 请各位城市对应同学关注哦~~
# 当日气象局预警提醒：xxxxx
# 日期:2019-12-22
def assembleCardtext_hefeng(location='beijing'):

	# alarmFlag 是否需要发送异常提醒
	alarmFlag = False 

	# 日期
	date = '<div class = \"gray\" >'+ time.strftime("%Y年%m月%d日", time.localtime()) + '</div><div> </div>'

	try:

		today_weather  = getDailyWeather_hefeng(location,day=0)
		hourly_weather = getHourlyWeather_hefeng(location)
		
		logMonitor('今日天气',today_weather)
		logMonitor('小时天气',hourly_weather)

		#判断高温
		tmp_max = int(today_weather['tmp_max'])
		if tmp_max > 34:
			alarmFlag = True
			content_body_tem = '<div class = \"normal\" >* 今日最高气温 '+ str(tmp_max) + '℃，天气炎热，达达热天配送辛苦，注意安抚达达 </div>'
		else:
			content_body_tem = ''	


		#判断风速
		wind_spd = int(today_weather['wind_spd'])
		wind_sc  = today_weather['wind_sc']
		if wind_spd > 40:
			alarmFlag = True
			content_body_wind = '<div class = \"normal\" >* 今日预计有 '+ wind_sc + '级大风，请注意提醒达达路途配送安全 </div>'
		else:
			content_body_wind = ''

		

		#判断气象局发布的气象预警，需要换付费接口，暂时不提醒
		# try:
		# 	alarm_content = weather['alarm']["alarm_content"]
		# except :
		# 	logMonitor('错误发生','alarm_content 无返回')
		# finally:
		# 	alarm_content = ''
		# if alarm_content :
		# 	alarmFlag = True
		# 	# content_body_alarm = '气象局预警提醒：\n'+ alarm_content + '\n'
		# 	content_body_alarm = '<div class = \"normal\" > 气象局预警提醒：'+ alarm_content + '</div>'
		# else:
		# 	content_body_alarm = ''
		
	##
		# 判断分时段的雨量
		# 300	阵雨			301	强阵雨 	302	雷阵雨
		# 303	强雷阵雨
		# 304	雷阵雨伴有冰雹
		# 306	中雨	
		# 307	大雨	
		# 308	极端降雨
		# 310	暴雨	
		# 311	大暴雨
		# 312	特大暴雨
		# 313	冻雨	
		# 314	小到中雨
		# 315	中到大雨
		# 316	大到暴雨
		# 317	暴雨到大暴雨
		# 318	大暴雨到特大暴雨
	##

		today = time.strftime("%Y-%m-%d", time.localtime())
		content_body_rain = ''
		rain_list = (300,301,302,303,304,306,307,308,310,311,312,313,314,315,316,317,318)
		
		# 循环每个小时，获取有雨的时段
		for ll in range(len(hourly_weather)):
			ret_time = hourly_weather[ll]['time']
			ret_date = ret_time[:10]
			ret_hour = int(ret_time[-5:-3]) #换换成时间数字，比较大小
			cond_code = hourly_weather[ll]['cond_code'] 
			cond_txt  = hourly_weather[ll]['cond_txt'] 
			print('@',ret_date,' ',str(ret_hour),'点, 天气状态状况为: ',cond_code,'/',cond_txt) 

			# 只看今日且在8-23点期间的天气
			if ret_date == today and ret_hour >= 8 and ret_hour < 23:
				if int(cond_code) in rain_list:
					alarmFlag = True
					content_body_rain = content_body_rain + str(ret_hour) + '点，'
				# elif cond_code in frog_list:
				# 	pass
				# 	此处可以用来判断是否有雪、是否有风、是否有雾  -- 分时段
				else:
					pass	

		if content_body_rain:
			# content_body_rain = '* 当前城市今日有雨，影响履约，预计有雨出现时间: ' + content_body_rain + '\n'
			content_body_rain = '<div class = \"normal\" >* 当前城市今日有雨，影响履约，预计有雨出现时间: '+ content_body_rain + '</div>'
		else:
			content_body_rain = ''	


		content_tail = '<div> </div> <div class = \"gray\" >注：每日早上8点发送当日负责的相关城市天气预警情况。</div>'

		# 判断是否需要发送消息，如果需要返回消息
		if alarmFlag:
			content_body = date + content_body_rain + content_body_tem + content_body_wind + content_tail
			return content_body
		else:
			return 'NoMsg'
	except:	
		print("Error occored; Function assembleCardtext_hefeng , unknown error, please check \n")
		return 'NoMsg'




# End --assembleCardtext_hefeng--



# 日志记录
def logMonitor(title,content,enable=1):
	logTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	if enable:
		print('#',logTime, '# ',title,':\n',content,'\n')
	else:
		pass
# End --logMonitor--



#定点执行任务
def taskLoop(loopPeriod='Daily',hour=0,minute=0,sec=0,enable = 1):
	
	# 不生效，直接返回
	if enable == 0:
		return 0

		
	cur_hour = time.localtime().tm_hour
	cur_min = time.localtime().tm_min
	cur_sec = time.localtime().tm_sec

	
	if loopPeriod == 'Daily' and hour==cur_hour and minute == cur_min and sec == cur_sec:
		time.sleep(1) #避免重复进入
		return 1
	elif loopPeriod == 'Hourly' and minute == cur_min and sec == cur_sec:
		time.sleep(1) #避免重复进入
		return 1
	else:
		return 0


# 和风天气：https://dev.heweather.com/docs/api/weather
def getHourlyWeather_hefeng(location='beijing'):
	wea_api_url = 'https://free-api.heweather.net/s6/weather/hourly?key=youKey&location='
	wea_api_req = wea_api_url + location
	logMonitor('Hourly天气请求URL',wea_api_req)
	try:
		wea_text=requests.get(wea_api_req).text
		# print(wea_text)
		return json.loads(wea_text)['HeWeather6'][0]['hourly']
	except:
		print("Error occored; Request 和风 Hourly weather data error \n")
		return ''

# 和风天气：https://dev.heweather.com/docs/api/weather
# day:代表预测的天数
# 	-1 	代表返回所有
# 	0	代表预测今日
# 	1	代表预测明日
def getDailyWeather_hefeng(location='beijing',day=-1):
	wea_api_url = 'https://free-api.heweather.net/s6/weather/forecast?key=youKey&location='
	wea_api_req = wea_api_url + location
	logMonitor('Daily天气请求URL',wea_api_req)

	try:
		wea_text=requests.get(wea_api_req).text
		days_lens = len(wea_text)
		if day == -1:
			return json.loads(wea_text)['HeWeather6'][0]['daily_forecast']
		elif day < days_lens:
			return json.loads(wea_text)['HeWeather6'][0]['daily_forecast'][day]
		else:
			print("Error occored; Function getDailyWeather_hefeng , variable day exceed max length \n")
			return ''
	except:
		print("Error occored; Request 和风 Daily weather data error \n")
		return ''
	



def weatherAlarm(staff_list,city_dict_cache):
	staff_list_len = len(staff_list) #员工数量

	real_city_dict_cache = city_dict_cache
	for ii in range(staff_list_len):
		staff_info = staff_list[ii]
		
		city = staff_info['city']
		sendUsrId = staff_info['userId']
		sendUsrName = staff_info['name']

		city_len = len(city)
		for jj in range(city_len):
			# getHourlyWeather_tianqiapi(city[jj])
			weatherCardtext = real_city_dict_cache.get(city[jj])
			
			if weatherCardtext:
				logMonitor('当前从缓存获取天气数据，要发送的消息',str(weatherCardtext))
				

			else:
				weatherCardtext = assembleCardtext_hefeng(city[jj])
				logMonitor('当前请求和风，重新获取天气，要发送的消息',str(weatherCardtext))
				real_city_dict_cache[city[jj]]=weatherCardtext
			
			if weatherCardtext == 'NoMsg':
				print('未给#'+sendUsrName+' 发送【'+city[jj]+'】异常天气情况，原因为：无异常\n\n','-------------结束符-------------------------\n')

			else:
				
				pushMsg_WX(sendUsrId,{"title":'异常天气预警 - '+ city[jj],'description':weatherCardtext,'url':'https://xw.tianqi.qq.com','btntxt':'查看详细天气'},sendType=2)
				print('给#'+sendUsrName+' 发送【'+city[jj]+'】异常天气情况，结束\n\n','-------------结束符-------------------------\n')



#-------------------------------------
#----------以下为主任务进入--------------
#-------------------------------------

staff_list_test = [{'userId':'zhangsan','name':'张三','city':['北京','深圳']},
{'userId':'lisi','name':'李四','city':['北京','深圳','常州']}]



runOnce = 0
while 1:	
	if runOnce:
		weatherAlarm(staff_list_test,city_dict_cache={})
		break
		
	elif taskLoop(hour=9,minute=2,sec=0):

		print('\n\n预设任务的执行时间到达，准备执行,执行时间',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
		weatherAlarm(staff_list_all,city_dict_cache={})
		print('一次任务执行结束\n\n')

	elif taskLoop(loopPeriod='Hourly',minute=45,sec=0,enable = 0):
		print('\n\n预设任务的执行时间到达，准备执行,执行时间',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
		weatherAlarm(staff_list_test,city_dict_cache={})
		print('一次任务执行结束\n\n')

	elif taskLoop(loopPeriod='Hourly',minute=59,sec=59):
		print('整点报时：',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

	elif taskLoop(hour=8,minute=0,sec=0):
		print('here')
		pushMsg_WX(sendUsr='wangjunlong',sendContent='监控一切正常，目前正常运行中，今日应该没有问题，请放心！',sendType=1)

	else:
		pass			



	

				










