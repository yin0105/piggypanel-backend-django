# Piggy Panel - Django/Python Repository

This repository is the back end Django/Python code, the piggypanel-react repository is the React client code

React JS Demo URL : https://demo.piggypanel.com/
Django Admin  URL : https://demo.piggypanel.com:8000/admin

Credentials can be provided on request

# System Overview
The goal of this application is to connect to a Zoho CRM via API and allow the dynamic creation of browse/edit screens.

Zoho
The communication between the Python back end and Zoho works as:
A cron job on the server runs every 5 minutes to perform a BULK API call to Zoho to pull down new records/changes to records
However the React JS Client, whenever a SAVE is made by a user - this is pushed directly to Zoho

So saves from the React front end are instant in Zoho, but changes in Zoho can take up to 5 minutes to sync down.


Django Admin 
The concept was to allow fields from Zoho to be dymanically added to Browse/Edit screens on the React front end
Menu items:
Leads -> Browse Leads Layout  -- This allows to select which field will show in the Leads Browse screen on React
Leads -> Add/Edit Lead Layout

Contacts -> Browse Contacts Layout
Contacts -> Add/Edit Contact Layout



# Current issues:
- Users say that sometimes when they click "Save & Edit Next Record" some of the values displayed on the client fields are not correct, they seem to be cached from a previous record.
- When a Record is saved, it can happen that if you go Next then Previous - back onto that record - the values that were saved are not showing on the fields!
- 



