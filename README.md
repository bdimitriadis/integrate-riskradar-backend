# INTEGRATE Riskradar backend services
INTEGRATE backend services, are necessary for the INTEGRATE web and mobile applications. Tokenization and various other functionalities regarding Riskradar toolkit (Questionnaires' flowcharts, RiskCalclulator assessment etc.) are supported by the current services.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites
Things you need to install on your system:

```
* Python 3.x.x (tried with 3.8.13)

* Install necessary python packages via: pip install -r requirements.txt
```

## Deployment

* Adjust settings in the config.py file to your own system/setup settings.
* In FlaskApp.py adjust **app.config.from_object('config.DevelopmentConfig')** line properly (using _DevelopmentConfig_, _ProductionConfig_ or _TestingConfig_ as argument to the _from_object_ module).
* In db_helper.py adjust **conf = config.DevelopmentConfig** line properly (using _DevelopmentConfig_, _ProductionConfig_ or _TestingConfig_).
* Just run FlaskApp.py in the local directory with python3 on your local machine **for development and testing purposes**.
* To deploy the project **on a live system**, follow the instruction given by the official documentation of flask on http://flask.pocoo.org/docs/0.12/deploying/

## Built With

* [Python 3.8.13](http://www.python.org/) - Developing with the best programming language
* [Flask 2.2.2](http://flask.pocoo.org/) - Flask web development, one drop at a time

## Authors

* **Christine Kakalou** and **Vlasios Dimitriadis** - *Initial work* - [integrate-riskradar-backend](https://github.com/bdimitriadis/integrate-riskradar-backend)
