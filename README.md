[![Coverage Status](https://img.shields.io/coveralls/carlosp420/VoSeq.svg)](https://coveralls.io/r/carlosp420/VoSeq?branch=master)

Windows    | Linux
---------- | --------
[![Build status](https://ci.appveyor.com/api/projects/status/0ba440vjw8811845/branch/master?svg=true)](https://ci.appveyor.com/project/carlosp420/voseq/branch/master) | [![Build Status](https://travis-ci.org/carlosp420/VoSeq.svg)](https://travis-ci.org/carlosp420/VoSeq)

# VoSeq is being rewritten
We are rebuilding VoSeq from scratch. We decided to migrate from PHP to Python
by using the framework Django. We also moved from MySQL to PostgreSQL.

You can still download the old VoSeq v1.7.4 from [here](https://github.com/carlosp420/VoSeq/releases/tag/v1.7.4).
But be aware that we will not be doing major maintenance of that code.

Here is a test installation of the old VoSeq (v1.7.0) <http://www.nymphalidae.net/VoSeq/>

More details about the migration can be found in our [discussion list](https://groups.google.com/forum/#!topic/voseq-discussion-list/wQ-E0Xcimgw).

VoSeq 2.0.0 is the future!

# Configuration
You need to install the dependencies:

```shell
pip install -r requirements/dev.txt
```

Download and install `elasticsearch` from here: http://www.elasticsearch.org/overview/elkdownloads/
You can install the `.deb` file. Start the service with the following command:

```shell
sudo service elasticsearch start
```

Create a `config.json` file to keep the database variables:
```javascript
{
    "SECRET_KEY": "create_a_secret_key",
    "DB_USER": "postgres",
    "DB_PASS": "database_password",
    "DB_NAME": "voseq",
    "DB_PORT": "5432",
    "DB_HOST": "localhost",
    "GOOGLE_MAPS_API_KEY": "get_a_google_map_api_key"
}
```

Create a PostgreSQL database (replace x.x for 9.3 or 9.4):

```shell
sudo apt-get install postgresql postgresql-contrib postgresql-server-dev-x.x
sudo su postgres
```

Create new role by typing:
```shell
createuser --interactive
```

Create a password for this user:
```shell
psql
postgres=# ALTER ROLE postgres WITH PASSWORD 'hu8jmn3';
```

Create a database for Voseq:
```shell
postgres=# create database voseq;
```

# Migrate VoSeq database
You need to dump your MySQL database into a XML file:

```shell
mysqldump --xml voseq_database > dump.xml
```

Then use our script to migrate all your VoSeq data into a PostGreSQL database.

```shell
make migrations
python migrate_db.py dump.xml
```

It might issue a warning message:

```
WARNING:: Could not parse dateCreation properly.
WARNING:: Using empty as date for `time_edited` for code Your_Vocher_Code
```

It means that the creation time for your voucher was probably empty or similar
to `0000-00-00`. In that case the date of creation for your voucher will be
empty. This will not cause any trouble when running VoSeq. You can safely
ignore this message.

Create an index for all the data in your database:

```shell
make index
```

Start the development server:

```shell
make serve
```

Open this URL in your web browser and you are ready to start using VoSeq:
`http://127.0.0.1:8000/`

# Test database for development
You can use test data to populate your PostgreSQL database, useful for 
development.

Create a PostgreSQL database:

```shell
sudo su postgres
psql
postgres=# create database voseq;
```

Create tables for the database:

```shell
make migrations
```

Import test data for your database:

```shell
make import
```

Start the server:
```shell
make serve
```

And point your web browser to:  `http://127.0.0.1:8000/`
