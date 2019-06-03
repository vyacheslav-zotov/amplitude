# Amplitude REST API Connector

This is a simple library for connecting to [Amplitude's REST API](https://amplitude.zendesk.com/hc/en-us/articles/205469748-Dashboard-Rest-API-Export-Amplitude-Dashboard-Data#query-parameters ) with Python. All responces from the API are converted into Pandas data frames. 
You can also give a try to [marmurar's Pyamplitude library](https://github.com/marmurar/pyamplitude).

The main goal of the project is to help product analysts from getting lost in swarms of identical Amplitude dashboards.

## Getting Started

### Prerequisites

This library was developed under Python 3.6.7 and Ubuntu 18.04.1 LTS.

Before you start please install the following libraries:
- pycurl
- pandas

In case you have troubles installing pycurl, please follow [this instruction](https://stackoverflow.com/questions/37669428/error-in-installation-pycurl-7-19-0).

### Installing

1. Download and extract amplitude_API.py and amplitude_config.json project's files into your project directory;
2. Find your Amplitude API Key and Secret Key. For this, in Amplitude go to Manage Data -> %YOUR_PROJECT% -> Project settings;
3. Modify amplitude_config.json like this:

```json
{
	"apiKey":	"%YOUR_API_KEY_HERE%",
	"secretKey":	"%YOUR_SECREY_KEY_HERE%"
}
```

4. Import the library to your project:

```python
from amplitude_API import *
amplitude = amplitudeAPI('amplitude_config.json')
```

5. Query sample data:

```python
from amplitude_API import *
amplitude = amplitudeAPI('amplitude_config.json')
```

## Documentation

### Library structure
- amplitudeEvent - a proxy class, implementing Amplitude's event filtering and grouping logic. For example, a structure like this:

![alt text](https://github.com/vyacheslav-zotov/amplitude/blob/master/docs/event_example.jpg "Event example")

can be translated into: 

```python
followPlaylist = amplitudeEvent('Follow Playlist')
followPlaylist.andIs('user', 'Country', ['United%20States', 'Germany'])
followPlaylist.andIsNot('event', 'Genre_Type', ['Rock', 'HipHop'])
followPlaylist.groupBy('user', ['device_type']) #see AMPL_SYSTEM_PROPERTIES constant for Amplitude system property aliases
followPlaylist.groupBy('event', ['Source']) #Amplitude's REST API allows up to 2 group-by dimensions
```

- amplitudeSegment - another proxy class, implementing Amplitude's user segment logic. For example, a segment like this:

![alt text](https://github.com/vyacheslav-zotov/amplitude/blob/master/docs/segment_example.jpg "Segment example")

can be defined as:

```python
sfUsers = amplitudeSegment()
sfUsers.andIs('City', ['San%20Francisco'])
sfUsers.andIs('Version', ['1.0', '1.1'])
```

- amplitudeUserPropertyGroupBy - yet another proxy class, implementing Amplityde's group by user property logic (group by section under segment definitions):

![alt text](https://github.com/vyacheslav-zotov/amplitude/blob/master/docs/group_by_example.jpg "Group by example")

this group by can be represented as:

```python
groupByDeviceType = amplitudeUserPropertyGroupBy(['device_type'])
```

- amplitudeAPI - the main class, implementing all interactions with Amplitude's REST API;

### amplitudeAPI methods
- queryApi - a core method providing all interactions between the library and Amplitude's API
- getEvents - returns a list of all events available for a given project (see [API reference](https://amplitude.zendesk.com/hc/en-us/articles/205469748-Dashboard-Rest-API-Export-Amplitude-Dashboard-Data#events-list));
- getDataFromExistingChart - returns the data from a pre-defined chart (see [API reference](https://amplitude.zendesk.com/hc/en-us/articles/205469748-Dashboard-Rest-API-Export-Amplitude-Dashboard-Data#results-from-an-existing-chart));
- getAnnotations - returns a list of user-defined annotations (see [API reference](https://amplitude.zendesk.com/hc/en-us/articles/205469748-Dashboard-Rest-API-Export-Amplitude-Dashboard-Data#annotations)); 
- getUserActivity - returns event history for a given user (see [API reference](https://amplitude.zendesk.com/hc/en-us/articles/205469748-Dashboard-Rest-API-Export-Amplitude-Dashboard-Data#user-activity));
- getLTV - queries LTV data (see [API reference](https://amplitude.zendesk.com/hc/en-us/articles/205469748-Dashboard-Rest-API-Export-Amplitude-Dashboard-Data#revenue%C2%A0ltv));
- getRetention - gets retention information (see [API reference](https://amplitude.zendesk.com/hc/en-us/articles/205469748-Dashboard-Rest-API-Export-Amplitude-Dashboard-Data#retention-analysis));
- getFunnel - a generalized procedure for creating event funnels (see [API reference](https://amplitude.zendesk.com/hc/en-us/articles/205469748-Dashboard-Rest-API-Export-Amplitude-Dashboard-Data#funnel-analysis));
- getEventSegmentation - a core function for querying event time series from Amplitude (see [API reference](https://amplitude.zendesk.com/hc/en-us/articles/205469748-Dashboard-Rest-API-Export-Amplitude-Dashboard-Data#event-segmentation));
- getEventUniques - queries DAU for a given event (see [API reference](https://amplitude.zendesk.com/hc/en-us/articles/205469748-Dashboard-Rest-API-Export-Amplitude-Dashboard-Data#event-segmentation));
- getEventTotals - retruns total counts for a given event (see [API reference](https://amplitude.zendesk.com/hc/en-us/articles/205469748-Dashboard-Rest-API-Export-Amplitude-Dashboard-Data#event-segmentation));
- getEventPropSum - applies a given formula (e.g. PROPSUM) to a selected event (see [API reference](https://amplitude.zendesk.com/hc/en-us/articles/205469748-Dashboard-Rest-API-Export-Amplitude-Dashboard-Data#event-segmentation));
- getEventFullData - returns DAU, total event counts and PROPSUM for a given event and event property (e.g. $price). Basically, this procedure combines the results from getEventUniques, getEventTotals and getEventPropSum in a single data frame;
- getSessionLengthDistro - gets a distribution of sessions lengths for a given time frame (see [API reference](https://amplitude.zendesk.com/hc/en-us/articles/205469748-Dashboard-Rest-API-Export-Amplitude-Dashboard-Data#session-length-distribution));
- getSessionAvgLength - queries average session length (see [API reference](https://amplitude.zendesk.com/hc/en-us/articles/205469748-Dashboard-Rest-API-Export-Amplitude-Dashboard-Data#average-session-length));
- getSessionAvgPerUser - returns an average number of induvidual sessions (see [API reference](https://amplitude.zendesk.com/hc/en-us/articles/205469748-Dashboard-Rest-API-Export-Amplitude-Dashboard-Data#average-sessions-per-user));

#### getEvents
The following code will give you a list of all active events for your project:

```python
events = amplitude.getEvents()
events = events[~events.non_active] 
events.name.unique()
```

#### getDataFromExistingChart
The following code will return a json structure, containing the data from the specified dashboard. 

```python
amplitude.getDataFromExistingChart(%CHART_ID_STRING%)
```
You can obtain %CHART_ID_STRING% by creating a new chart, saving it and copying the id from chart's URL. For example:

```
https://analytics.amplitude.com/demo/chart/2qsp75u/edit/ouxuadr
```
translates into **%CHART_ID_STRING% = ouxuadr**

#### getAnnotations
The following code will get a list of Amplitude's data annotations with labels that contain product version information (e.g. v1.0, v2.0, etc):

```python
amplitude.getAnnotations(labelFilter = '^v[0-9]+\.[0-9]$').sort_values(by = 'startDt')
```
Resulting data frame will contain the following fields:
* startDt - label's date;	
* finishDt - next label's date minus 1 day; 	
* duration - difference between finishDt and startDt in days;
* label - annotation's label; 	
* details - annotation's description.

#### getUserActivity
The following code will return a json, containing 1000 most recent events for %AMPLITUDE_USER_ID_INT% user:

```python
amplitude.getUserActivity(%AMPLITUDE_USER_ID_INT%)
```

#### getLTV
The following code snippet will return two dataframes - one for ARPPU data and another one containing conversion stats:

```python
dfARPPU, dfConv = amplitude.getLTV('2019-05-01', '2019-05-07', segment = None, groupBy = None)
```

Both data frames have almost identical structure:
* segment - a result of groupBy condition. For example, if you group the data by user's country, Segment will contain contry names;
* dt - new user aquisition date;
* age - days since user aquisition day;
* cohort_size - number of new users, aquired at a particular day;	
* payers - number of paying users within a cohort (within 30 days since the initial aquisition day);	
* rev_ppu - average revenue per paying user at a given age (tot_rev/payers);
* tot_rev - total cumulative revenue at a given age;
* new_payers - number of users, who converted at a given age;	
* conv - total number of converted users at a given age;
* completed - whether 30 days passed since the initial aquisition day.

You can turn asbolute numbers into aggregates and percents by grouping the dataframe like this:
```python
dfARPPU = dfARPPU.groupby('age').agg({'cohort_size': 'sum', 
                                      'payers': 'sum', 
                                      'tot_rev': 'sum', 
                                      'completed': 'min'})
dfARPPU = dfARPPU[dfARPPU.completed]
dfARPPU['rev_ppu'] = dfARPPU.tot_rev / dfARPPU.payers	

dfConv = dfConv.groupby('age').agg({'cohort_size': 'sum', 
                                    'payers': 'sum', 
                                    'conv': 'sum', 
                                    'completed': 'min'})
dfConv = dfConv[dfConv.completed]
dfConv['conv_perc'] = dfConv.conv / dfConv.cohort_size				 
```


#### getRetention
The following code will return a data frame, containing retention information:

```python
dfRetention = amplitude.getRetention('2019-05-01', '2019-05-07', segment = None, groupBy = None)
```
The structure of the resulting data frame:
* segment - a result of groupBy condition. For example, if you group the data by user's country, Segment will contain contry names;
* dt - new user aquisition date;
* age - days since user aquisition day;	
* retained - number of users retained at a given age;	
* cohort_size - number of new users, aquired at a particular day;
* completed - whether 30 days passed since the initial aquisition day.

You can than turn asbolute numbers into aggregates and percents by grouping the dataframe like this:

```python
dfRetention = dfRetention.groupby('age').agg({'cohort_size': 'sum', 
                                              'retained': 'sum', 
                                              'completed': 'min'})
dfRetention = dfRetention[dfRetention.completed]
dfRetention['ret_perc'] = dfRetention.retained / dfRetention.cohort_size					      
```

#### getFunnel
```python
#?????????????? Examples here
```
#### getEventSegmentation
```python
#?????????????? Examples here
```
#### getEventUniques
```python
#?????????????? Examples here
```
#### getEventTotals
```python
#?????????????? Examples here
```
#### getEventPropSum
```python
#?????????????? Examples here
```
#### getEventFullData
```python
#?????????????? Examples here
```
#### getSessionLengthDistro
```python
#?????????????? Examples here
```
#### getSessionAvgLength
```python
#?????????????? Examples here
```
#### getSessionAvgPerUser
```python
#?????????????? Examples here
```

## Known limitations
1. The following features are still missing:
- Active and new user counts;
- User composition;
- User search;
- Real time active users;
2. Query cost calculations aren't implemented yet (as for 5/30/2019);
3. It's unclear from Amplitudes REST API documentation how to make user segments, reffering to only new users:
![alt text](https://github.com/vyacheslav-zotov/amplitude/blob/master/docs/new_segment.jpg "New users only segment")

## Running the tests

This project doesn't have any tests implemented primarily because Amplitude's free demos don't support REST API.

## Authors

* **Vyacheslav Zotov** - *Initial work* - [vyacheslav-zotov](https://github.com/vyacheslav-zotov)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
