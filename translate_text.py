import sqlite3
    

# Create a SQL connection to our SQLite database
con = sqlite3.connect("db.sqlite3")


def add_translation(table_name, field_name, row_id, lang_code, translated_text):
    
    # update that row in the table
    sql = ''' UPDATE ''' + table_name + '''
              SET ''' + field_name + '''_''' + lang_code + ''' = ?
              WHERE Page_ptr_id = ?'''
              
    # execute the sql command
    cur = con.cursor()
    cur.execute(sql, (translated_text, row_id))
    con.commit()



# get information about the translated field
table_name = "home_transhomepage"
field_name = "Body"
lang_code = "FR"
translated_text = "NEW FR TRANSLATION"
row_id = 4

#add_translation(table_name, field_name, row_id, lang_code, translated_text)




    
