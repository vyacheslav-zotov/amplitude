#!/usr/bin/python

#installing pycurl
#https://stackoverflow.com/questions/37669428/error-in-installation-pycurl-7-19-0

import pycurl
from io import BytesIO

import json

import pandas as pd

from datetime import datetime, timedelta

import math

AMPL_API_DEBUG_MODE = False

#constants 
AMPL_FREQ_REALTIME = -300000
AMPL_FREQ_HOURLY = -3600000
AMPL_FREQ_DAILY = 1
AMPL_FREQ_WEEKLY = 7
AMPL_FREQ_MONTHLY = 30

AMPL_METRIC_UNIQUES = 'uniques'
AMPL_METRIC_TOTALS = 'totals'
AMPL_METRIC_PROP_SUM = 'sums'
AMPL_METRIC_FORMULA = 'formula'

#default formulas
AMPL_FORMULA_UNIQUES = 'UNIQUES(A)'
AMPL_FORMULA_TOTALS = 'TOTALS(A)'
AMPL_FORMULA_PROPSUM = 'PROPSUM(A)'

#LTV metrics
#One of the following metrics: 
#0 = ARPU, 
#1 = ARPPU, 
#2 = Total Revenue, 
#3 = Paying Users (default 0).
AMPL_LTV_METRIC_ARPU = 0
AMPL_LTV_METRIC_ARPPU = 1
AMPL_LTV_METRIC_TOTREV = 2
AMPL_LTV_METRIC_PAYING = 3

#
AMPL_SYSTEM_PROPERTIES = ['version', 
						  'country', 
						  'city', 
						  'region', 
						  'dma', 
						  'language', 
						  'platform', 
						  'os', 
						  'device', 
						  'device_type', 
						  'start_version', 
						  'paying',
						  'userdata_cohort',
						  'user_id']

class amplitudeEvent:
	
	def __init__(self, 
				 eventName):
		self.eventName = eventName.replace(' ', '%20')
		self.filters = []
		self.groupby = []

	def __addFilter__(self, propertyType, propertyName, operator, propertyValues):

		if not propertyName.lower() in AMPL_SYSTEM_PROPERTIES: 
			if propertyType == 'user':
				propertyName = 'gp:{0}'.format(propertyName)
			else:
				propertyName = '{0}'.format(propertyName)
		else:
			propertyName = propertyName.lower() #system props are all lower case

		propertyValues = ['"{0}"'.format(str(val)) for val in propertyValues]
		propertyValues = ','.join(propertyValues)

		condString = '{{"subprop_type":"{0}","subprop_key":"{1}","subprop_op":"{2}","subprop_value":[{3}]}}'.format(propertyType,
																													propertyName,
																													operator,
																													propertyValues)
		self.filters += [condString]

	def getEventUrl(self):
		
		#filters = ','.join(list(set(self.filters)))
		filters = ','.join(self.filters)
		#print(filters)
		if len(filters) > 0:
			filters = ',"filters":[{0}]'.format(filters)
		
		groupby = ','.join(list(self.groupby))
		if len(groupby) > 0:
			groupby = ',"group_by":[{0}]'.format(groupby)	

		result = '{{"event_type":"{0}"{1}{2}}}'.format(self.eventName, filters, groupby) 	
		#print(result)	
		return result

	def resetGroupBy(self):
		self.groupby = []

	def andIs(self, propertyType, propertyName, propertyValues):
		operator = 'is'
		self.__addFilter__(propertyType, propertyName, operator, propertyValues)

	def andIsNot(self, propertyType, propertyName, propertyValues):
		operator = 'is%20not'  	    	
		self.__addFilter__(propertyType, propertyName, operator, propertyValues)

	def andContains(self, propertyType, propertyName, propertyValues):
		operator = 'contains'   	
		self.__addFilter__(propertyType, propertyName, operator, propertyValues)

	def andDoesntContain(self, propertyType, propertyName, propertyValues):
		operator = 'does%20not%20contain'
		self.__addFilter__(propertyType, propertyName, operator, propertyValues)

	def andLess(self, propertyType, propertyName, propertyValues):
		operator = 'less'
		self.__addFilter__(propertyType, propertyName, operator, propertyValues)

	def andLessOrEqual(self, propertyType, propertyName, propertyValues):
		operator = 'less%20or%20equal'
		self.__addFilter__(propertyType, propertyName, operator, propertyValues)

	def andGreater(self, propertyType, propertyName, propertyValues):
		operator = 'greater'
		self.__addFilter__(propertyType, propertyName, operator, propertyValues)

	def andGreaterOrEqual(self, propertyType, propertyName, propertyValues):
		operator = 'greater%20or%20equal'
		self.__addFilter__(propertyType, propertyName, operator, propertyValues)

	def andSetIs(self, propertyType, propertyName, propertyValues):
		operator = 'set%20is'
		self.__addFilter__(propertyType, propertyName, operator, propertyValues)

	def andSetIsNot(self, propertyType, propertyName, propertyValues):
		operator = 'set%20is%20not'
		self.__addFilter__(propertyType, propertyName, operator, propertyValues)

	def groupBy(self, propertyType, propertyName):

		#Amplitude doesn't allow more than 2 dimensions 
		if len(self.groupby) > 2: raise Exception

		if not propertyName.lower() in AMPL_SYSTEM_PROPERTIES:
			if propertyType == 'user':
				propertyName = 'gp:{0}'.format(propertyName)
			else:
				propertyName = '{0}'.format(propertyName)
		else:
			propertyName = propertyName.lower() #system props are all lower case

		self.groupby += ['{{"type":"{0}","value":"{1}"}}'.format(propertyType, propertyName)]

class amplitudeSegment:

	def __init__(self):
		self.conditions = []

	def __addProperty__(self, operator, propertyName, propertyValues):
		
		if not propertyName.lower() in AMPL_SYSTEM_PROPERTIES: 
			propertyName = 'gp:{0}'.format(propertyName)
		else:
			propertyName = propertyName.lower() #system props are all lower case

		propertyValues = ['"{0}"'.format(str(val)) for val in propertyValues]
		propertyValues = ','.join(propertyValues)
		condString = '{{"prop":"{0}","op":"{1}","values":[{2}]}}'.format(propertyName,
																		 operator,
																		 propertyValues)
		self.conditions += [condString]

	def getConditionsUrl(self):
		#removing duplicates
		#joining into a list-string
		result = list(set(self.conditions))
		result = ','.join(result)
		return '&s=[{0}]'.format(result)

	def andIs(self, propertyName, propertyValues):
		operator = 'is'
		self.__addProperty__(operator, propertyName, propertyValues)

	def andIsNot(self, propertyName, propertyValues):
		operator = 'is%20not'  	    	
		self.__addProperty__(operator, propertyName, propertyValues)

	def andContains(self, propertyName, propertyValues):
		operator = 'contains'   	
		self.__addProperty__(operator, propertyName, propertyValues)

	def andDoesntContain(self, propertyName, propertyValues):
		operator = 'does%20not%20contain'
		self.__addProperty__(operator, propertyName, propertyValues)

	def andLess(self, propertyName, propertyValues):
		operator = 'less'
		self.__addProperty__(operator, propertyName, propertyValues)

	def andLessOrEqual(self, propertyName, propertyValues):
		operator = 'less%20or%20equal'
		self.__addProperty__(operator, propertyName, propertyValues)

	def andGreater(self, propertyName, propertyValues):
		operator = 'greater'
		self.__addProperty__(operator, propertyName, propertyValues)

	def andGreaterOrEqual(self, propertyName, propertyValues):
		operator = 'greater%20or%20equal'
		self.__addProperty__(operator, propertyName, propertyValues)

	def andSetIs(self, propertyName, propertyValues):
		operator = 'set%20is'
		self.__addProperty__(operator, propertyName, propertyValues)

	def andSetIsNot(self, propertyName, propertyValues):
		operator = 'set%20is%20not'
		self.__addProperty__(operator, propertyName, propertyValues)

#
class amplitudeUserPropertyGroupBy:

	def __init__(self, properties):

		#Amplitude doesn't allow more than 2 dimensions 
		if len(properties) > 2: raise Exception
		
		def transformAmplPropetyName(propertyName):
			if not propertyName.lower() in AMPL_SYSTEM_PROPERTIES:
				return 'gp:{0}'.format(propertyName)
			else:
				return propertyName.lower() #system props are all lower case

		self.properties = [transformAmplPropetyName(propName) for propName in properties]	

	def getConditionsUrl(self):
		#removing duplicates
		#joining into a list-string
		result = [''] + list(set(self.properties))
		return '&g='.join(result)    	


#amplitude API 
#https://amplitude.zendesk.com/hc/en-us/articles/205469748-Dashboard-Rest-API-Export-Amplitude-Dashboard-Data#results-from-an-existing-chart
class amplitudeAPI:
	
	def __init__(self, configFile):

		with open(configFile, 'r') as f:
			config = json.load(f)
			
		self.apiKey = config['apiKey']
		self.secretKey = config['secretKey']
		
	def queryApi(self, url):
		buffer = BytesIO()
		c = pycurl.Curl()
		c.setopt(c.URL, url)
		c.setopt(c.USERPWD, '{0}:{1}'.format(self.apiKey, self.secretKey)) 
		c.setopt(c.WRITEDATA, buffer)
		c.perform()
		c.close()    
		body = buffer.getvalue()
		body = body.decode('iso-8859-1')
		#print(body)
		try:
			body = json.loads(body)
			if AMPL_API_DEBUG_MODE:
				print(url)
				#print('Nova cost: {0}'.format(body['novaCost']))
				print(body)
			return body
		except:
			print('Body is not a json')
			print(url)
			print(body)
			raise

	def getEvents(self):
		
		#getting data from amplitude
		url = 'https://amplitude.com/api/2/events/list'
		response = self.queryApi(url)	

		return pd.DataFrame(response['data'])
		
	def getDataFromExistingChart(self, dashboardId):
		
		#getting data from amplitude
		url = 'https://amplitude.com/api/3/chart/{0}/query'.format(dashboardId)
		response = self.queryApi(url)

		return response
	
		#parsing
		#series = response['data']['series']
		#labels = response['data']['seriesLabels']
		#index = response['data']['xValues']
		
		#returning pandas dataframe
		#dfResult = pd.DataFrame()
		#for i, label in enumerate(labels):
		#	dfResult[label] = [val['value'] for val in series[i]]
		#dfResult['index'] = index
		#dfResult = dfResult.set_index('index')
		#return dfResult

	#returns annotations
	#default filter is set to major releases by default
	def getAnnotations(self, labelFilter = '^[0-9]+\.[0-9]+$'):

		url = 'https://amplitude.com/api/2/annotations'
		result = self.queryApi(url)

		try:
			data = result['data']
			result = []
			for record in data:
				result += [[record['id'], record['date'], record['label'], record['details']]]
			result = pd.DataFrame(result, columns = ['id', 
													 'startDt', 
													 'label', 
													 'details'])
		except:
			raise

		result.startDt = pd.to_datetime(result.startDt)
		result = result[result.label.str.contains(labelFilter)].sort_values(by = 'startDt')
		result['finishDt'] = result.startDt.shift(-1).fillna(datetime.now().date())
		result.finishDt = result.finishDt - timedelta(days = 1)
		result['duration'] = result.apply(lambda row: (row.finishDt - row.startDt).days, axis = 1)
		result = result.set_index('id')

		result.startDt = result.startDt.dt.date
		result.finishDt = result.finishDt.dt.date

		return result[['startDt', 
					   'finishDt', 
					   'duration', 
					   'label', 
					   'details']]

	def getUserActivity(self, 
						amplitudeUserId, 
						offset = 0, 
						limit = 1000):

		url = 'https://amplitude.com/api/2/useractivity?user={0}&offset={1}&limit={2}'.format(amplitudeUserId, offset, limit)
		result = self.queryApi(url)

		user = result['userData']

		events = []
		for event in result['events']:
		    user_properties = event['user_properties']
		    event_properties = event['event_properties']
		    #removing nested copies of user_properties and event_properties
		    header = event.copy()
		    header.pop('user_id', None)
		    header.pop('event_type', None)
		    header.pop('server_received_time', None)
		    header.pop('user_properties', None)
		    header.pop('event_properties', None)
		    
		    events += [[result['userData']['canonical_amplitude_id'], 
		                event['user_id'], 
		                event['event_type'], 
		                event['server_received_time'], 
		                result['userData']['paying'],
		                header,
		                user_properties,
		                event_properties]]

		events = pd.DataFrame(events, columns = ['amplitude_id', 
		                                         'user_id',
		                                         'event_type',
		                                         'dt',
		                                         'paying',
		                                         'header',
		                                         'user_properties',
		                                         'event_properties'])	
		events.paying = events.apply(lambda x: x.paying in ['true', 'True', True], axis = 1)
		events.dt = pd.to_datetime(events.dt)	

		return user, events

	#queries LTV
	def getLTV(self,  
			   startDt, 
			   finishDt, 
			   frequency = AMPL_FREQ_DAILY, 
			   metric = AMPL_LTV_METRIC_ARPPU,
			   segment = None,
			   groupBy = None):

		#frequency = AMPL_FREQ_DAILY
		#metric = AMPL_LTV_METRIC_ARPPU             #we can reconstruct all other metrics from ARPPU
		startDt = startDt.replace('-', '')
		finishDt = finishDt.replace('-', '')

		if segment is not None:
			segment = segment.getConditionsUrl()
		else:
			segment = ''

		if groupBy is not None: 	
			groupBy = groupBy.getConditionsUrl()
		else:
			groupBy = ''

		url = 'https://amplitude.com/api/2/revenue/ltv?m={0}&start={1}&end={2}&i={3}{4}{5}'.format(metric, startDt, finishDt, frequency, segment, groupBy)
		result = self.queryApi(url)
				
		byDayCumulativeSpendPerUser = []
		byDayConversions = []
		byDayTotals = []
		byDayCompleteFlag = []

		combinedSpendPerUser = []
		combinedTotals = []
		combinedCompleteFlag = []

		#for each of the series
		for seriesIndex, seriesName in enumerate(result['data']['seriesLabels']):
			currentSeriesData = result['data']['series'][seriesIndex]   
		
			#day by day values
			for day, dayValues in currentSeriesData['values'].items():
				
				byDayTotals += [[seriesName, 
								day,
								dayValues['count'], 
								dayValues['paid'],                         
								dayValues['total_amount'],  
								dayValues['rtotalnew'], 
								dayValues['rtotal']]]
				
				#remove totals in order not to break the generation of daily values
				dayValues.pop('total_amount')
				dayValues.pop('count')
				dayValues.pop('rtotalnew')
				dayValues.pop('rtotal')
				dayValues.pop('paid')
				
				byDayConversions += [[seriesName, 
									  day, 
									  int(key.replace('r', '').replace('new', '')), 
									  value] for key, value in dayValues.items() if key.endswith("new")]
				byDayCumulativeSpendPerUser += [[seriesName, 
												 day, 
												 int(key.replace('r', '').replace('d', '')), 
												 value] for key, value in dayValues.items() if key.endswith("d")] 
			
			#day by day completeness
			for day, dayValues in currentSeriesData['complete'].items():
				byDayCompleteFlag += [[seriesName, 
									   day, 
									   int(key.replace('r', '').replace('d', '')), 
									   value] for key, value in dayValues.items() if key.endswith("d")] 
				
			combinedCompleteFlag += [[seriesName, 
									  int(key.replace('r', '').replace('d', '')), 
									  value] for key, value in currentSeriesData['combined_complete'].items() if key.endswith("d")]
			
			#combined spenders, without by day separation
			combinedTotals += [[seriesName, currentSeriesData['combined']['paid']]]
			currentSeriesData['combined'].pop('paid')
			
			#combined spend per user (without by day separation)
			combinedSpendPerUser += [[seriesName, 
									  int(key.replace('r', '').replace('d', '')), 
									  value] for key, value in currentSeriesData['combined'].items() if key.endswith("d")]

		#flags indicating that the data is available for a day and age
		byDayCompleteFlag = pd.DataFrame(byDayCompleteFlag, columns=['segment',
																	 'dt',
																	 'age',
																	 'completed']).set_index(['segment',
																							  'dt',
																							  'age'])

		#combined daily statistics
		byDayTotals = pd.DataFrame(byDayTotals, columns = [	'segment', 
															'dt', 
															'cohort_size', 
															'payers', 
															'x1', 
															'x2', 
															'x3'])

		#day-by-day non-cumulative conversions up to d180, discrete values for d1-d7, d14, d30, d60, d90, d120, d180 are available
		byDayConversions = pd.DataFrame(byDayConversions, 
										columns = ['segment', 
												   'dt', 
												   'age',
												   'new_payers']).sort_values(by = ['segment', 
																					'dt', 
																					'age'])
		byDayConversions['conv'] = byDayConversions.groupby(by = ['segment', 
																  'dt']).new_payers.cumsum()
		byDayConversions = byDayConversions.set_index(['segment', 
													   'dt']).join(byDayTotals.set_index(['segment', 
													   									  'dt'])[['cohort_size', 
													                                              'payers']])
		byDayConversions = byDayConversions.reset_index().set_index(['segment', 
																	 'dt', 
																	 'age']).join(byDayCompleteFlag)
		byDayConversions = byDayConversions[['cohort_size', 
											 'payers', 
											 'new_payers', 
											 'conv', 
											 'completed']].reset_index()

		#day-by-day cumulative spend per user up to d180, continuos values for d1-d180 are available
		byDayCumulativeSpendPerUser = pd.DataFrame(byDayCumulativeSpendPerUser, 
												   columns = ['segment', 
															  'dt', 
															  'age', 
															  'rev_ppu']).sort_values(by = ['segment', 
																							'dt', 
																							'age'])	

		byDayCumulativeSpendPerUser = byDayCumulativeSpendPerUser.set_index(['segment', 
																			 'dt']).join(byDayTotals.set_index(['segment', 
																			 	                                'dt'])[['cohort_size', 
																			 											'payers']])
		byDayCumulativeSpendPerUser['tot_rev'] = byDayCumulativeSpendPerUser.rev_ppu * byDayCumulativeSpendPerUser.payers
		byDayCumulativeSpendPerUser = byDayCumulativeSpendPerUser.reset_index().set_index(['segment', 
																						   'dt', 
																						   'age']).join(byDayCompleteFlag)
		byDayCumulativeSpendPerUser = byDayCumulativeSpendPerUser[['cohort_size', 
																   'payers', 
																   'rev_ppu', 
																   'tot_rev', 
																   'completed']].reset_index()

		combinedTotals = pd.DataFrame(combinedTotals, columns = ['segment', 'payers']).set_index('segment')

		#combined completed flags
		combinedCompleteFlag = pd.DataFrame(combinedCompleteFlag, columns = ['segment', 
																			 'age', 
																			 'combined_complete']).set_index(['segment', 'age']) 

		#combined spend by user
		combinedSpendPerUser = pd.DataFrame(combinedSpendPerUser, columns = ['segment', 
																			 'age', 
																			 'x']).sort_values(by = ['segment', 'age'])		
		combinedSpendPerUser = combinedSpendPerUser.set_index('segment').join(combinedTotals).reset_index()
		combinedSpendPerUser = combinedSpendPerUser.set_index(['segment', 'age']).join(combinedCompleteFlag).reset_index()

		return byDayCumulativeSpendPerUser, byDayConversions

	#queries user retention
	#https://amplitude.zendesk.com/hc/en-us/articles/205469748#retention-analysis
	def getRetention(self,  
					 startDt, 
				 	 finishDt, 
				     frequency = AMPL_FREQ_DAILY, 
					 segment = None,
					 groupBy = None):

		startAction = '_new'
		returnAction = '_all'  #re=\{"event_type":"Play%20Song%20or%20Video"\}
		retentionMode = None   #'n-day'
		retentionBracket = None

		startDt = startDt.replace('-', '')
		finishDt = finishDt.replace('-', '')

		if segment is not None:
			segment = segment.getConditionsUrl()
		else:
			segment = ''

		if groupBy is not None: 	
			groupBy = groupBy.getConditionsUrl()
		else:
			groupBy = ''

		if retentionMode is not None:
			retentionMode = '&rm={0}'.format(retentionMode)		
		else:
			retentionMode = ''	

		if retentionBracket is not None:
			retentionBracket = '&rb={0}'.format(retentionBracket)
		else: 
			retentionBracket = ''

		url = 'https://amplitude.com/api/2/retention?se={{"event_type":"{0}"}}&re={{"event_type":"{1}"}}{2}{3}&start={4}&end={5}&i={6}{7}{8}'.format(startAction, returnAction, retentionMode, retentionBracket, startDt, finishDt, frequency, segment, groupBy)   	
		result = self.queryApi(url)

		byDayRetention = []

		combinedRetention = []

		#for each of the series
		for seriesIndex, seriesName in enumerate(result['data']['seriesLabels']):
			currentSeriesData = result['data']['series'][seriesIndex]   
			
			#day by day values
			for day, dayValues in currentSeriesData['values'].items(): 
				
				for lifetime, value in enumerate(dayValues):
					byDayRetention += [[seriesName, day, lifetime, value['count'], value['outof'], not value['incomplete']]]
			
			#combined values
			for lifetime, value in enumerate(currentSeriesData['combined']):
				combinedRetention += [[seriesName, lifetime, value['count'], value['outof'], not value['incomplete']]]    
			
		byDayRetention = pd.DataFrame(byDayRetention, columns = ['segment', 
																 'dt', 
																 'age', 
																 'retained', 
																 'cohort_size', 
																 'completed'])
		byDayRetention = byDayRetention[byDayRetention.age > 0] #day 0 always duplicates day 1

		combinedRetention = pd.DataFrame(combinedRetention, columns = ['segment', 
																	   'age', 
																	   'retained', 
																	   'cohort_size', 
																	   'completed'])
		combinedRetention = combinedRetention[combinedRetention.age > 0] #day 0 always duplicates day 1

		return byDayRetention

	def getFunnel(self, 
				  funnel,
				  startDt, 
				  finishDt, 
				  mode = 'ordered',
				  new = 'new',  					#active
				  segment = None,
				  groupBy = None,	
				  conversionWindow = 2592000,		#30 days	 
				  limit = 1000, 					#number of group by values returned				   
				  ):

		startDt = startDt.replace('-', '')
		finishDt = finishDt.replace('-', '')

		if segment is not None:
			segment = segment.getConditionsUrl()
		else:
			segment = ''

		if groupBy is not None: 	
			groupBy = groupBy.getConditionsUrl()
		else:
			groupBy = ''

		funnelString = ''.join(['&e={0}'.format(evt.getEventUrl()) for evt in funnel])

		#getting data from amplitude
		url = 'https://amplitude.com/api/2/funnels?{0}&start={1}&end={2}{3}{4}&mode={5}&n={6}&cs={7}&limit={8}'.format(funnelString, startDt, finishDt, segment, groupBy, mode, new, conversionWindow, limit)
		result = self.queryApi(url) 
						
		cumulativeResults = []                
		#for each of the series
		for currentData in result['data']:
			#currentSeriesData = result['data']['series'][seriesIndex]                  
			#print(currentData['groupValue'])
			for eventIndex, eventName in enumerate(currentData['events']):
				cumulativeResults += [[currentData['groupValue'], 
									   eventName, 
									   currentData['cumulativeRaw'][eventIndex],
									   round(currentData['cumulative'][eventIndex] * 100, 2),
									   currentData['stepByStep'][eventIndex],
									   currentData['avgTransTimes'][eventIndex]/1000/60,
									   currentData['medianTransTimes'][eventIndex]/1000/60,
									 ]]
				
		cumulativeResults = pd.DataFrame(cumulativeResults, columns = [ 'Segment', 
																		'Step', 
																		'Unique users', 
																		'% passed', 
																		'perc_from_prev', 
																		'avg_trans_time_min', 
																		'Median time between [min]'])
		cumulativeResults['horizon_days'] = math.ceil(conversionWindow/60/60/24)
		return cumulativeResults

	def getEventSegmentation(self, 
							 event, 
							 startDt, 
							 finishDt, 
							 frequency = AMPL_FREQ_DAILY, 
							 metric = AMPL_METRIC_FORMULA, 			#probably everything can be expressed by a formula
							 limit = 1000, 					        #number of group by values returned
							 segment = None,
							 groupBy = None,
							 formula = AMPL_FORMULA_UNIQUES, 		#only a single formula is supported
							 rollingWindow = None,
							 rollingAverage = None
							 ): 

		startDt = startDt.replace('-', '')
		finishDt = finishDt.replace('-', '')

		if segment is not None:
			segment = segment.getConditionsUrl()
		else:
			segment = ''

		if groupBy is not None: 	
			groupBy = groupBy.getConditionsUrl()
		else:
			groupBy = ''

		if metric != AMPL_METRIC_FORMULA:
			formula = ''
		else:
			formula = '&formula={0}'.format(formula)

		#getting data from amplitude
		url = 'https://amplitude.com/api/2/events/segmentation?e={0}&start={1}&end={2}&i={3}&m={4}{5}{6}&limit={7}{8}'.format(event.getEventUrl(), startDt, finishDt, frequency, metric, segment, groupBy, limit, formula)
		result = self.queryApi(url)     

		dfResult = []
		#for each of the series
		for seriesIndex, seriesName in enumerate(result['data']['seriesLabels']):
			currentSeriesData = result['data']['series'][seriesIndex]   
			
			for xLabelIndex, xLabel in enumerate(result['data']['xValues']):
				dfResult += [[seriesName, xLabel, currentSeriesData[xLabelIndex]]]
		
		try: 
			dfResult = pd.DataFrame(dfResult, columns = ['Segment', 'x', 'y'])
			def segmentToString(segment):
				if isinstance(segment, list): return ', '.join(segment)
				return str(segment)
			dfResult.Segment = dfResult.apply(lambda row: segmentToString(row.Segment), axis = 1)
			dfResult.x = pd.to_datetime(dfResult.x)

			#print(dfResult)
			return(dfResult)
		except:
			return None

	def getEventUniques(self, 
						event, 
						startDt, 
						finishDt, 
						frequency = AMPL_FREQ_DAILY, 
						segment = None, 
						groupBy = None):
		return self.getEventSegmentation(event, 
										 startDt, 
										 finishDt, 
										 frequency = frequency,
										 segment = segment, 
										 groupBy = groupBy,
										 formula = AMPL_FORMULA_UNIQUES)

	def getEventTotals(self, 
					   event, 
					   startDt, 
					   finishDt, 
					   frequency = AMPL_FREQ_DAILY, 
					   segment = None, 
					   groupBy = None):
		return self.getEventSegmentation(event, 
										 startDt, 
										 finishDt, 
										 frequency = frequency,
										 segment = segment, 
										 groupBy = groupBy,
										 formula = AMPL_FORMULA_TOTALS)

	def getEventPropSum(self, event, startDt, finishDt, 
						sumProperty, 							#property to be summed
						groupProperty = None,					#additional groupping on event level				
						frequency = AMPL_FREQ_DAILY,
						segment = None, 
						groupBy = None 							#groupby on global level
						):
		event.resetGroupBy()
		event.groupBy(sumProperty[0], sumProperty[1])
		if groupProperty is not None:
			event.groupBy(groupProperty[0], groupProperty[1])

		return self.getEventSegmentation(event, 
										 startDt, 
										 finishDt, 
										 frequency = frequency,
										 segment = segment, 
										 groupBy = groupBy,
										 formula = AMPL_FORMULA_PROPSUM)

	def getEventFullData(self, event, startDt, finishDt, 
						 frequency = AMPL_FREQ_DAILY,	
						 sumProperty = None, 					#property to be summed
						 groupProperty = None, 					#additional groupping on event level		
						 segment = None, 
						 groupBy = None):

		result = None
		returnColumnsOrder = ['Unique users', 'Total events']
		if sumProperty is not None:
			sumPropName = sumProperty[1]
			returnColumnsOrder += [sumPropName]

			result = self.getEventPropSum(event, 
										  startDt, 
										  finishDt, 
										  sumProperty, 
										  groupProperty = groupProperty,
										  frequency = frequency,
										  segment = segment, 
										  groupBy = groupBy)

			try:
				result = result.rename(columns = {'y': sumPropName}).set_index(['Segment', 
																				'x'])
			except:
				print(result)
				raise

			#in this case we have to cancel all existing group by on event and replace it by
			#additional group by from summation 
			event.resetGroupBy()
			if groupProperty is not None:
				event.groupBy(groupProperty[0], groupProperty[1])			


		dfUniques = self.getEventUniques(event, 
										 startDt, 
										 finishDt,
										 frequency = frequency,
										 segment = segment, 
										 groupBy = groupBy)
		if dfUniques is not None:
			if len(dfUniques.index) > 0:
				dfUniques = dfUniques.rename(columns = {'y': 'Unique users'}).set_index(['Segment', 'x'])

		if result is not None:
			result = result.join(dfUniques)
		else:
			result = dfUniques

		dfTotals = self.getEventTotals(event, 
									   startDt, 
									   finishDt,
									   frequency = frequency,
									   segment = segment, 
									   groupBy = groupBy)
		if dfTotals is not None:
			if len(dfTotals.index) > 0:
				dfTotals = dfTotals.rename(columns = {'y': 'Total events'}).set_index(['Segment', 'x'])

		#result = result.join(dfTotals)
		if result is not None:
			result = result.join(dfTotals)	
			return result[returnColumnsOrder].reset_index()
		else:
			return None

	def getSessionLengthDistro(self, 
							   startDt, 
							   finishDt, 
							   segment = None, 
							   groupBy = None):

		startDt = startDt.replace('-', '')
		finishDt = finishDt.replace('-', '')

		if segment is not None:
			segment = segment.getConditionsUrl()
		else:
			segment = ''

		if groupBy is not None: 	
			groupBy = groupBy.getConditionsUrl()
		else:
			groupBy = ''

		#getting data from amplitude
		url = 'https://amplitude.com/api/2/sessions/length?start={0}&end={1}{2}{3}'.format(startDt, finishDt, segment, groupBy)
		#print(url)
		result = self.queryApi(url) 			

		dfResult = []
		#for each of the series
		for seriesIndex, seriesName in enumerate(result['data']['seriesLabels']):
			currentSeriesData = result['data']['series'][seriesIndex]   

			for xLabelIndex, xLabel in enumerate(result['data']['xValues']):
				dfResult += [[seriesName, xLabel, currentSeriesData[xLabelIndex]]]
				
		dfResult = pd.DataFrame(dfResult, columns = ['Segment', 
													 'Duration', 
													 'Sessions']).groupby(['Segment', 
													 					   'Duration']).agg({'Sessions': 'max'})
		dfResult['% of total'] = dfResult.groupby(level = 0).apply(lambda x: x / float(x.sum()))
		dfResult = dfResult.reset_index()

		return dfResult

	def getSessionAvgLength(self, 
							   startDt, 
							   finishDt, 
							   segment = None, 
							   groupBy = None):

		startDt = startDt.replace('-', '')
		finishDt = finishDt.replace('-', '')

		if segment is not None:
			segment = segment.getConditionsUrl()
		else:
			segment = ''

		if groupBy is not None: 	
			groupBy = groupBy.getConditionsUrl()
		else:
			groupBy = ''

		#getting data from amplitude
		url = 'https://amplitude.com/api/2/sessions/average?start={0}&end={1}{2}{3}'.format(startDt, finishDt, segment, groupBy)
		#print(url)
		result = self.queryApi(url) 	

		dfResult = []
		#for each of the series
		for seriesIndex, seriesName in enumerate(result['data']['seriesLabels']):
			currentSeriesData = result['data']['series'][seriesIndex]   

			for xLabelIndex, xLabel in enumerate(result['data']['xValues']):
				dfResult += [[seriesName, xLabel, currentSeriesData[xLabelIndex]]]
				
		dfResult = pd.DataFrame(dfResult, columns = ['Segment', 'Date', 'Avg session length [sec]'])

		return dfResult

	def getSessionAvgPerUser(self, 
							 startDt, 
							 finishDt, 
							 segment = None, 
							 groupBy = None):

		startDt = startDt.replace('-', '')
		finishDt = finishDt.replace('-', '')

		if segment is not None:
			segment = segment.getConditionsUrl()
		else:
			segment = ''

		if groupBy is not None: 	
			groupBy = groupBy.getConditionsUrl()
		else:
			groupBy = ''

		#getting data from amplitude
		url = 'https://amplitude.com/api/2/sessions/peruser?start={0}&end={1}{2}{3}'.format(startDt, finishDt, segment, groupBy)
		result = self.queryApi(url) 

		dfResult = []
		#for each of the series
		for seriesIndex, seriesName in enumerate(result['data']['seriesLabels']):
			currentSeriesData = result['data']['series'][seriesIndex]   

			for xLabelIndex, xLabel in enumerate(result['data']['xValues']):
				dfResult += [[seriesName, xLabel, currentSeriesData[xLabelIndex]]]
				
		dfResult = pd.DataFrame(dfResult, columns = ['Segment', 
													 'Date', 
													 'Avg session per user'])

		return dfResult		        	