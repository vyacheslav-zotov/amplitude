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
- amplitudeEvent - ????????
- amplitudeSegment - ????????
- amplitudeUserPropertyGroupBy - ????????
- amplitudeAPI - ????????

### amplitudeAPI methods
- queryApi - ????????
- getEvents - ????????
- getDataFromExistingDashboard - ????????
- getAnnotations - ????????
- getUserActivity - ????????
- getLTV - ????????
- getRetention - ????????
- getFunnel - ????????
- getEventSegmentation - ????????
- getEventUniques - ????????
- getEventTotals - ????????
- getEventPropSum - ????????
- getEventFullData - ????????
- getSessionLengthDistro - ????????
- getSessionAvgLength - ????????
- getSessionAvgPerUser - ????????

#### getDataFromExistingDashboard
?????????????? Examples here
#### getAnnotations
?????????????? Examples here
#### getUserActivity
?????????????? Examples here
#### getLTV
?????????????? Examples here
#### getRetention
?????????????? Examples here
#### getFunnel
?????????????? Examples here
#### getEventSegmentation
?????????????? Examples here
#### getEventUniques
?????????????? Examples here
#### getEventTotals
?????????????? Examples here
#### getEventPropSum
?????????????? Examples here
#### getEventFullData
?????????????? Examples here
#### getSessionLengthDistro
?????????????? Examples here
#### getSessionAvgLength
?????????????? Examples here
#### getSessionAvgPerUser
?????????????? Examples here

## Known limitations
1. The following features are still missing:
- Active and new user counts;
- User composition;
- User search;
- Real time active users;
2. It's unclear from Amplitudes REST API documentation how to make user segments, reffering to only new users:
![alt text](https://github.com/vyacheslav-zotov/amplitude/blob/master/docs/new_segment.jpg "New users only segment")

## Running the tests

This project doesn't have any tests implemented primarily because Amplitude's free demos don't support REST API.

## Authors

* **Vyacheslav Zotov** - *Initial work* - [vyacheslav-zotov](https://github.com/vyacheslav-zotov)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
