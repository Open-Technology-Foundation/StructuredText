# StructuredText
The StructuredText format is a simple, flexible, and human-readable  way to represent key-value pairs, with support for comments and  multi-line values.

### USAGE:
`st.extract` [-h] [-d DELVARS] [-S] [-n] [-f FREETEXT_NAME] [-s SEP]
                  [-l LF] [-k] [-j] [-o OUTPUT] [-i JSON_INDENT] [-v]
                  filename [keyvar]

Extract key variables from Structured Text file.
For Structured Text format see library module StructuredText.

#### positional arguments:
  filename              Text file.
  keyvar                Optional key variable to find and return;
                        by default returns all key variables; def. 'None'.

#### options:
  -h, --help            show this help message and exit

  -d DELVARS, --delvars DELVARS
                        List of comma delimited keys to remove from output; def. 'None'.
  
  -S, --strict          Impose Strict mode; exit with error if a key variable in aline is not found.
                        If False, all free text is aggregated into key variable_FREETEXT_; def. 'False'.
  
  -n, --no_comments     Ignore #comment lines. Default is to not ignore comment lines
                        and store as '_COMMENT_n: comment'; def. 'False'.
  
  -f FREETEXT_NAME, --freetext_name FREETEXT_NAME
                        Name of key to collate free text; def. '_FREETEXT_'.
  
  -s SEP, --sep SEP     Number of spaces after ':'; def. '1'.
  
  -l LF, --lf LF        Number of linefeeds printed after each key variable; def. '2'.
  
  -k, --showkeys        Print all keys found in file and exit; def. 'False'
  
  -j, --json            Output raw json; def. 'False'.
  
  -o OUTPUT, --output OUTPUT
                        Output to filename; def 'None'.
  
  -i JSON_INDENT, --json_indent JSON_INDENT
                        JSON output indent, integer or 'none'; def. '2'.
  
  -v, --verbose         Be not quiet; def. 'False'.

