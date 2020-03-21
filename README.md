# drchrono virtual hackathon project 

## TODO
Doctor:
-[ ] show scheduled appointments, checked-in patients (waiting times)
-[ ] change the status of the check-ins
-[ ] show statistics : number of patients, checked-ins, wait times
-[ ] auto update of the dashboard
-[ ] EXTRA: show appointments in different days

Kiosk:
-[ ] check-in: confirm, update change

Authentication:
-[ ] set up the kiosk and dashboard
-[ ] EXTRA: refresh the token access


### Doctor Dashboard
Description here

### Check-in kiosk

Description here

### Requirements
- a free [drchrono.com](https://www.drchrono.com/sign-up/) account
- [docker](https://www.docker.com/community-edition) (optional)


#### API token 
The first thing to do is get an API token from drchrono.com, and connect this local application to it!

This project has `social-auth` preconfigured for you. The `social_auth_drchrono/` contains a custom provider for
[Python Social Auth](http://python-social-auth.readthedocs.io/en/latest/) that handles OAUTH through drchrono. It should
 require only minimal configuration and tweaking. 

1) Log in to [drchrono.com](https://www.drchrono.com)
2) Go to the [API management page](https://app.drchrono.com/api-management/)
3) Make a new application
4) Copy the `SOCIAL_AUTH_CLIENT_ID` and `SOCIAL_AUTH_CLIENT_SECRET` to your `docker/environment` file.
5) Set your redirect URI to `http://localhost:8080/complete/drchrono/`


### Dev environment Setup
If you're familiar with it, docker should take care of all the dependencies for you. It will create one container with 
all the python dependencies.The project uses SQLite3 as a database back-end, so you shouldn't need to mess with anything 
to get django up and running. See `docker-compose.yml` for details.

``` 
$ git clone git@github.com:drchrono/api-example-django.git hackathon
$ docker-compose up
```

If you don't want to use docker, that's fine too! The project is fairly small and self-contained. You can probably get all
the dependencies installed and running on your favorite platform with `pip install -r requirements.txt && python manage.py runserver`. You'll have to configure the `CLIENT_ID` and `CLIENT_SECRET` variables by hand, though.

Once the dev server is running, connect with a browser to [http://localhost:8080/setup]() and use the web to authorize 
the application.


### Happy Hacking!
If you have trouble at any point in the setup process, feel free to reach out to the developer
who introduced you to the project. We try to minimize setup friction, but sometimes things go wrong, and we genuinely 
appreciate feedback about how to make things better!
