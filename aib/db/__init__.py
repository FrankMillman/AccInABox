"""
The "db" package is responsible for all database activity.

It can talk to the following RDMS's -

* MS Sql Server
* PostgreSQL on Linux
* sqlite3

Definitions
 
* active_company - the company actually making the various requests
 
* defn_company - if not the same as active_company, get the table definitions
                   from a different company
 
* data_company - if not the same as active_company, get the table data
                   from a different company
"""
