"""
The "db" package is responsible for all database activity.

It can communicate with the following RDMS's -

* PostgreSQL
* MS Sql Server
* sqlite3

The package contains the following modules -

* `db.connection` Classes and functions relating to a database connection.
    * `db.conn_mssql` Classes and functions specific to MS Sql Server
    * `db.conn_pgsql` Classes and functions specific to PostgreSQL
    * `db.conn_sqlite3` Classes and functions specific to sqlite3
* `db.cursor` Classes and functions relating to a database cursor.
    * `db.cur_mssql` Classes and functions specific to MS Sql Server
    * `db.cur_pgsql` Classes and functions specific to PostgreSQL
    * `db.cur_sqlite3` Classes and functions specific to sqlite3
* `db.objects` Classes that represent database objects.
* `db.object_fields` Classes that represent database fields.
* `db.cache` A cache to store commonly used data objects.
* `db.dflt_xml` Evaluate a dflt_rule from a `db.objects.Column` definition and return the result.
* `db.actions_xml` Actions can be set up to be called at various database events.
* `db.checks` Certain 'validation' steps in col_checks are coded in Python, and stored here.
* `db.create_table` Take a table definition from db_tables/columns and create a database table.
* `db.create_view` Take a view definition from db_views/view_cols and create a database view.
"""
