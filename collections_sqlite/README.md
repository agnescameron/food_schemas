## Collections in SQLite format

Collections should be formatted as folders, named for the date they were generated (in the format mm_dd_yy). For days where more than 1 version is produced, name is mm_dd_yy-number, with numbers starting at 1.

Each folder should contain the meta-schema generated for that version, plus a copy of the generated sqlite database (note: the database may also be exported as a set of CSVs, which can live in the folder, though the table names will need to be changed from URIs as they are invalid file names).

Each folder may also contain a README giving additional version information.

For an example, check out 12_28_20.