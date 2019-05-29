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
	"apiKey":		"%YOUR_API_KEY_HERE%",
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


And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc
