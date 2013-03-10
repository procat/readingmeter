import urllib.request as req
import string
import time
import json
import urllib.parse
import math

class Monitor:
  def __new__(self):
		self.URL = "http://localhost/fiee/save_data_umg.php"
		self.URL_LOCAL = "http://localhost/fiee/save_data_local.php"
		self.JSON = [
		"json.do?_ULN[0..3],_ULN_AVG[0..3],_ULN_MIN[0..3],_ULN_MIN_T[0..3],_ULN_MAX[0..3],_ULN_MAX_T[0..3],_ULL[0..2],_ULL_AVG[0..2],_ULL_MIN[0..2],_ULL_MIN_T[0..2],_ULL_MAX[0..2],_ULL_MAX_T[0..2],_FREQ,_FREQ_AVG,_FREQ_MIN,_FREQ_MIN_T,_FREQ_MAX,_FREQ_MAX_T,_N,_N_AVG,_N_MIN,_N_MIN_T,_N_MAX,_N_MAX_T,_M,_M_AVG,_M_MIN,_M_MIN_T,_M_MAX,_M_MAX_T,_G,_G_AVG,_G_MIN,_G_MIN_T,_G_MAX,_G_MAX_T",
		"json.do?_ILN[0..3],_ILN_AVG[0..3],_ILN_AVG_MAX[0..3],_ILN_AVG_MAX_T[0..3],_ILN_MAX[0..3],_ILN_MAX_T[0..3],_THD_ILN[0..3],_THD_ILN_AVG[0..3],_THD_ILN_AVG_MAX[0..3],_THD_ILN_AVG_MAX_T[0..3],_THD_ILN_MAX[0..3],_THD_ILN_MAX_T[0..3],_IN,_IN_AVG,_IN_MAX,_IN_MAX_T,_IM,_IM_AVG,_IM_MAX,_IM_MAX_T,_IG,_IG_AVG,_IG_MAX,_IG_MAX_T",
		"json.do?_PLN[0..3],_PLN_AVG[0..3],_PLN_AVG_MAX[0..3],_PLN_AVG_MAX_T[0..3],_PLN_MAX[0..3],_PLN_MAX_T[0..3],_COS_PHI[0..3],_QLN[0..3],_P_SUM3,_P_SUM3_AVG,_P_SUM3_AVG_MAX,_P_SUM3_AVG_MAX_T,_P_SUM3_MAX,_P_SUM3_MAX_T,_COS_SUM3,_Q_SUM3,_P_SUM,_P_SUM_AVG,_P_SUM_AVG_MAX,_P_SUM_AVG_MAX_T,_P_SUM_MAX,_P_SUM_MAX_T,_QLN_AVG[0..3],_QLN_MAX[0..3],_QLN_MAX_T[0..3],_Q_SUM3_AVG,_Q_SUM3_MAX,_Q_SUM3_MAX_T,_Q_SUM,_Q_SUM_AVG,_Q_SUM_MAX,_Q_SUM_MAX_T,_SLN[0..3],_SLN_AVG[0..3],_SLN_MAX[0..3],_SLN_MAX_T[0..3],_S_SUM3,_S_SUM3_AVG,_S_SUM3_MAX,_S_SUM3_MAX_T,_S_SUM,_S_SUM_AVG,_S_SUM_MAX,_S_SUM_MAX_T", 
		"json.do?_WH_V[0..5],_WH_V_HT[0..5],_WH_V_NT[0..5],_IQH[0..5],_IQH_HT[0..5],_IQH_NT[0..5],_S0_CNT[0..1],_S0_POWER[0..1]"]
		self.PROXY = {}
		self.METER = {}
		self.CONN = True
		self.INTERVAL = {}
		self.TIME = 0
		PROMEDIO = {}

##### 
# METODOS AUXILIARES
#####

	def _OpenURL(self, url, proxy=False):
		if proxy==True:
			proxy = req.ProxyHandler({'http': self.PROXY[0]})
		else:
			proxy = None
		auth = req.HTTPBasicAuthHandler()
		opener = req.build_opener(proxy, auth, req.HTTPHandler)
		req.install_opener(opener)
		try:
			data = req.urlopen(url)
		except req.URLError as e:
			print(" _OpenURL ERROR] " + url + " : " + format(e))
			result = False
		else:
			result = json.loads(data.read().decode('utf-8'))
		finally:
			close = data.close()
		return result

	def  _SendPost(self, url, params, proxy=False):
		data = urllib.parse.urlencode(params)
		param = data.encode('utf-8')
		if proxy==True:
			proxy = req.ProxyHandler({'http': self.PROXY[0])
		else:
			proxy = None
		auth = req.HTTPBasicAuthHandler()
		opener = req.build_opener(proxy, auth, req.HTTPHandler)
		req.install_opener(opener)
		try:
			data = req.urlopen(self.URL, param, timeout=1)
		except req.URLError as e:
			print(" _SendPost ERROR] " + self.URL + " : " + format(e))
			self.CONN = False
		else:
			self.CONN = True
		finally:
			return self.CONN

	def _Measurement(self, number):
		if number==0:
			return 'voltage'
		if number==1:
			return 'current'
		if number==2:
			return 'power'
		if number==3:
			return 'energy'

	def _setTime(self):
		self.TIME = int(time.time())
		return self.TIME

	def _getTime(self):
		return self.TIME

##### 
# METODOS PRINCIPALES
#####

	def Config(self):
		f = open("config.dat")
		i = -1
		for linea in f.readlines():
			dictio = {}
			if linea[0:1]=="#":
				i+=1
			else:
				if linea[0:4]=="http":
					self.PROXY.append(linea[0:-1])
				else:
					ip_and_meter = linea[0:-1].split(" ")
					# 0=> IP , 1=> METER
					dictio = [ ip_and_meter[0], ip_and_meter[1] ]
					self.METER.append(dictio)
		f.close

	def Connect(self):
		if len(self.PROXY)>=1:
			proxy = True
		else:
			proxy = False
		for meter in range(0, len(self.METER)):
			for url in range(0, len(self.JSON)):
				result = self._OpenURL("http://" + self.METER[meter][1] + "/" + self.JSON[url], proxy)
				if result==True:
					result['type'] = self._Measurement(url)
					result_for_post = self.OrderJSON(result, meter)
					self.SendIt(result_for_post)
				else:
					return False

	def OrderJSON(self, data_from_json, meter_id):
		dictio = {}
		for row in data_from_json:
			if(isinstance(data_from_json[row][0], list) and len(data_from_json[row][0])>1):
				for i in range(0, len(data_from_json[row][0])):
					dictio[str(row) + "__" + str(i)]=data_from_json[row][0][i]
			else:
				dictio[str(row)]=data_from_json[row][0]
		dictio['timestamp'] = self._setTime()
		dictio['id'] = meter_id
		if (self._getTime()%90)==0:
			for val in dictio:
				self.INTERVAL[val] = {}
				self.INTERVAL[val][0] = dictio[val]
		else:
			for val in dictio:
				if (isinstance(self.INTERVAL[val], dict))==False:
					self.INTERVAL[val] = {}
				self.INTERVAL[val][self._getTime()%90] = dictio[val]
		return dictio

	def SendIt(self, data):
		if len(self.PROXY)>=1:
			proxy = True
		else:
			proxy = False
		if self._SendPost(self.URL, data, proxy)==False:
			# LOCAL STORAGE
			self._SendPost(self.URL_LOCAL, data, proxy)
			print(" SendIt WARNING] Using local storage")
		else:
			# SENT OK
			print(" SendIt] data has sent.")

	def CalculateAverage(self):
		VARIABLES = ["_ULL", "_ILN", "_P_SUM"]
		self.INTERVAL['V'] = {}
		self.INTERVAL['I'] = {}
		for val in VARIABLES:
			self.PROMEDIO[val] = []
			for j in range(0, 899):
				if self.INTERVAL[val].get(j)!=None:
					if val=="_ULL":
						self.INTERVAL['V'][j] = math.sqrt(math.pow(self.INTERVAL[val + '_AVG__0'][j], 2) + math.pow(self.INTERVAL[val + '_AVG__1'][j], 2) + math.pow(self.INTERVAL[val + '_AVG__2'][j], 2))
					if val=="_ILN":
						self.INTERVAL['I'][j] = math.sqrt(math.pow(self.INTERVAL[val + '_AVG__0'][j], 2) + math.pow(self.INTERVAL[val + '_AVG__1'][j], 2) + math.pow(self.INTERVAL[val + '_AVG__2'][j], 2))
					# ACTIVE POWER => '_P_SUM'
					# REACTIVE POWER => '_Q_SUM'
