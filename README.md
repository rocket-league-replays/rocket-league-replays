# Rocket League Replays

Rocket League Replays is a fansite focused on providing post-match analysis of games played in Rocket League.  It allows users to upload their Rocket League .replay files, have them analysed and data displayed.

This repository contains all of the code required to run the application, as well as the worker services which are used to process the data.

## Installation

Rocket League Replays only works with Python 3, it is not compatible with Python 2.

### Clone the repository onto your machine and change into the folder

```
$ git clone git@github.com:rocket-league-replays/rocket-league-replays.git
$ cd rocket-league-replays/
```

### Create and activate a virtual environment (recommended)

Note: I'm using pyvenv, but you can also use virtualenv, virtualenvwrapper or any other alternative.

```
$ pyvenv-3.5 .venv
$ . .venv/bin/activate
```

### Install the Python requirements

Note: If you get a `clang` error on OS X try installing the Command Line Tools, then running `xcode-select --install`

```
$ pip install -r requirements.txt
```

### Install the front-end requirements

Note: It's recommended to use NVM to manage your node.js version. An .nvmrc file is included in the project.

```
$ nvm use
$ npm i
$ python manage.py collectstatic -l --noinput
$ npm run dev
```

### Configure the database

Note: If you're on OS X, the recommendation is to use [Postgres.app](http://postgresapp.com/).

```
$ createdb rocket_league
$ python manage.py migrate
```

### Run the server

```
$ python manage.py runserver_plus
```

You can then view the main parts of the site:

* Replay listing: http://127.0.0.1:8000/replays/
* Replay pack listing: http://127.0.0.1:8000/replay-packs/
* API: http://127.0.0.1:8000/api/
* Streams: http://127.0.0.1:8000/streams/
* Adminstration system: http://127.0.0.1:8000/admin/

If you need the Javascript code to run, then you should use port 3000 rather than 8000 (with `npm run dev` running at the same time as `runserver`).  To access the adminstration system you will need a login.  The easiest way to get an admin account is to run:

```
$ python manage.py createsuperuser
```

Follow the prompts and a user will be created which you can use to log in to the adminstration system.

### Getting a detailed replay parse

If you want to generate the more complex stats, you'll need to get the application to run the [Octane](https://github.com/tfausak/octane/) binaries. The easiest way to do this is to open up a Python shell:

```
$ python manage.py shell_plus
```

Then you can run the following code:

```
r = Replay.objects.get(pk=1)
r.processed = False
r.crashed_heatmap_parser = False
r.save(parse_netstream=True)
```

To process a different replay, simply change `pk=1` to reference your replay object.  The Octane binaries are automatically updated when you use `runserver`.

## Development notes

### Git Flow
The project uses Git Flow - though somewhat loosely these days.  Feature branches are the most commonly used aspect of this workflow, just to keep new changes out of the develop branch until they're ready.  The site used to use releases, but that has been somewhat discontinued in favour of faster released from `develop`.

### Code style

The project code should conform to the standards of PEP8 and isort. In addition, the front-end systems have their own requirements which are enforced as a part of `npm run dev`.  The Python code styles are not currently strictly enforced.


### Cron jobs

There are a number of cronjobs required for smooth operation of the website, they are as follows:


#### get_league_ratings

This job updates the current player rankings.  It collects all of the Steam IDs from across the site and updates their league rating values.

```
26,56 * * * * python manage.py get_league_ratings --settings=rocket_league.settings.production
```

#### social_post

This job is for pushing out the 'match of the day' to reddit and Twitter.

```
0 20 * * * python manage.py social_post --settings=rocket_league.settings.production
```

#### generate_replay_packs

Replay packs are no longer generated on-demand, rather they're generated ahead of time and are then available for users to download.

```
* * * * * python manage.py generate_replay_packs --settings=rocket_league.settings.production
```

#### get_patrons

This job uses the Patreon API to pull in the current list of Patreons so that they can receive their benefits.  

```
*/10 * * * * python manage.py get_patrons --settings=rocket_league.settings.production
```

Annoyingly, Patreon requires the access token be refreshed every 30 days, so sometimes this can stop working for seemingly no reason, but the access token is usually the culprit.  To refresh the token, make the following cURL request:

```
curl -X POST -F "grant_type=refresh_token" -F "refresh_token=<value>" -F "client_id=<value>" -F "client_secret=<value>" "http://api.patreon.com/oauth2/token"
```

The `client_id` and `client_secret` values come from the developers section of the Patreon website, the `refresh_token` comes from the previous refresh response.  This is the reason why the refresh value is stored in the [secrets.py](#secretspy) file. 


### Worker servers

The worker servers use a combination of Celery and Redis to communicate jobs across the internal private network.  Celery is kept running on the worker servers using Supervisor. The Supervisor configuration for Celery is as follows:

```
# cat /etc/supervisor/conf.d/celery.conf
[program:celery]
environment=DJANGO_SETTINGS_MODULE="rocket_league.settings.production"
directory=/var/www/rocket-league-replays
command=/var/www/rocket-league-replays/.venv/bin/celery -A rocket_league.apps.replays worker --loglevel=info -Q tournament,priority,general
stdout_logfile=/var/log/celeryd.log
stderr_logfile=/var/log/celeryd.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
user=celery
```

When a request for a replay to be processed is about to sent out, it's assigned to a specific queue. This queue is determined by the Patreon status of a user ([relevant code here](https://github.com/rocket-league-replays/rocket-league-replays/blob/4ec54da45ef01d28664354ccaa93ef23cfd0ac50/rocket_league/apps/replays/models.py#L510-L520)).  The worker servers are then assigned to specific queues.  If you have a 2 worker setup both workers would have tournament and priority, but only one would have general. This leads to a natural priorisation of non-general jobs.

### secrets.py

You'll notice a message appear whenever you do anything with `python manage.py`, it will read something like this:

> Secrets config not found, environment variables have not been set.

This file contains all of the passwords, API keys and methods which the site needs to be able to communicate with various third-party services. This file lives at `rocket_league/settings/secrets.py`.  The basic structure looks like this:

```
import os

os.environ['TWITTER_API_KEY'] = ''
os.environ['TWITTER_API_SECRET'] = ''
os.environ['TWITTER_ACCESS_TOKEN'] = ''
os.environ['TWITTER_ACCESS_SECRET'] = ''

os.environ['REDDIT_USERNAME'] = ''
os.environ['REDDIT_PASSWORD'] = ''

os.environ['DATABASE_USER'] = ''
os.environ['DATABASE_PASSWORD'] = ''
os.environ['DATABASE_HOST'] = ''

os.environ['AWS_ACCESS_KEY_ID'] = ''
os.environ['AWS_SECRET_ACCESS_KEY'] = ''

os.environ['PATREON_CLIENT_ID'] = ''
os.environ['PATREON_CLIENT_SECRET'] = ''
os.environ['PATREON_ACCESS_TOKEN'] = ''
os.environ['PATREON_REFRESH_TOKEN'] = ''

os.environ['SLACK_URL'] = ''

os.environ['REDIS_MASTER_PASSWORD'] = ''
os.environ['REDIS_SLAVE_PASSWORD'] = ''
os.environ['REDIS_HOST'] = ''
```

This file should _not_ be added to version control, especially not with the values inserted.
