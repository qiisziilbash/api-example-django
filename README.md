# drchrono virtual hackathon project 

## TODO
Doctor:
- [x] show scheduled appointments, checked-in patients (waiting times)
- [x] change the status of the check-ins
- [x] show statistics : number of patients, checked-ins, wait times
- [x] auto update of the dashboard
     - [x] webhook verification
     - [x] django channel
- [x] put a running clock for checked in patients
- [x] EXTRA: show appointments in different days
- [x] EXTRA: show today's date

Kiosk:
- [x] check-in: confirm, update change

Authentication:
- [x] set up the kiosk and dashboard
- [x] deauthorize 
- [x] show limited access in dashboard if patients wants to access
- [x] EXTRA: refresh the token access
- [x] redirect everything to setup if not authorized


Tests:
- [x] check in backend for uniqueness of 'In Session' appointments

### Webhook instructions
Tunnel your localhost using: 
$ ssh -R 80:localhost:8000 ssh.localhost.run
and add the callback url in drchrono's API

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

