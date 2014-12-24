# table definition - N/A

# column definitions - N/A

# virtual column definitions - N/A

# cursor definitions
cursors = []

cursors.append({
    'cursor_name': 'db_tables',
    'descr': 'Database tables',
    'columns': [
        ('table_name', 160, False, False, False, None, None),
        ('short_descr', 250, True, False, False, None, None),
        ('defn_company', 80, False, True, False, None, None),
        ('table_created', 80, False, True, False, None, None),
        ],
    'filter': [],
    'sequence': [('table_name', False)],
    'default': True
    })
