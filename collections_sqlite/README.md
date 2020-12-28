## Collections in SQLite format

Collections should be formatted as folders, named for the date they were generated (in the format mm_dd_yy). For days where more than 1 version is produced, name is mm_dd_yy-number, with numbers starting at 1.

Each folder should contain the meta-schema, generated for that version, plus a csv file for each table in the SQLite database. Note that these files won't export with URI table names, so the names of each table are shortened.