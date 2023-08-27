# StructuredText
StructuredText format is a very simple and flexible way to represent textual key-value pairs that are structured, but with high human-readablity, with support for comments and multi-line values.

It can be used to store configuration settings, articles, transcripts, etc, with metadata, and other textual information, where a high degree of human readability is required or desirable.

Requires Python 3.10 or higher.

The `StructuredText` package comprises a Python module, `StructuredText`, and a terminal script, `st.extract`.

The `StructuredText` module imports `os`, `sys`, and `re` only.

The terminal script, `st.extract` also imports the `StructuredText` module (as `st`), `json`, `argparse` and `pydoc`.

## Module 'StructuredText'

StructuredText format is a very simple and flexible way to represent textual key-value pairs that are structured, but with high human-readablity, with support for comments and multi-line values.

Input can be processed in a "Loose" mode, or a "Strict" mode.  In Strict mode StructuredText demands rigid adherance to the standard 'key:value' structure, and returns an error condition when this fails.

A valid single-line keyvar assignment has the following general form:

    `{KEYNAME}[blank]:[blank]{VALUE}`

For example:

    ```
    DATE: 1957-10-04 19:28:34
    ```

A valid multi-line keyvar assignment has the following general form:

    `{KEYNAME}[blank]:[blank]"""\n{VALUE}\n[blank]"""[blank]\n`

For example:

    ```
    ARTICLE: """
    This is a multi-line text.

    This is the next line.

    And the next...
    """
    ```

In both cases, [blank] chars are ignored and do not need to be present.


### 'Strict' Mode
Strict mode in the extract function controls how the function 
behaves when it encounters certain conditions or errors. 
By default, Strict is set to False.

Strict requires that *all* data is formatted in key:value format.

Error Handling: When Strict is set to True, the function prints 
error messages to stderr, and exits the program if certain 
conditions are not met.

Key Handling: If the text contains no key, the content is dumped
to the _FREETEXT_ key unless Strict mode is enabled.

Strict mode enforces a more rigorous set of constraints upon the 
text data within the `extract` function. If data format or issues
occur, an error message will appear, and the program will be 
terminated. 

Strict mode is useful for ensuring that the input data adheres 
to the expected StructuredText format and that any discrepancies 
are handled as critical errors rather than warnings.

### Function extract()
Extracts StructuredText formatted variables from an input source that can be a filename, list, or dictionary. 

  The `StructuredText.extract` function returns data in key:value format as a dictionary.

  Data in `input_source` should contain text lines in the format KEY:VALUE, where KEY is any valid Python variable name. 

  Multi-line values are enclosed in Python-style triple quotes (""").

  Blank lines that are not within multi-line values are ignored.

  Lines starting with '#' are treated as comments and are stored in a special key variable of '_COMMENT_'{n}. Optionally, comment
  lines can be completely ignored using parameter `no_comments=True`.

  If no valid key:value pairs are found in the file, and `Strict` mode is not set, then the entire content of `input_source` is stored and returned in special key variable called '_FREETEXT_'.

  Returns:
  dict: A dictionary where the keys are variable names from the file, and the values are the corresponding values from the file. 
  If no valid variables are found, the dictionary will contain a single item with the key '_FREETEXT_'.

### Function write_dict_to_st( 
    variables:dict, 
    keyvar:str      = None, 
    keyval_sep:str  = ':',    
    filename:str    = None, 
    lf:int          = 2, 
    sep:int         = 1
  ):

  Print out all key variables in 'dict' to file or stdout in `StructuredText` format. 


### Shell Script `st.extract`

```bash
st.extract [-h] [-d DELVARS] [-S] [-n] [-f FREETEXT_NAME] [-s SEP]
                  [-l LF] [-k] [-j] [-o OUTPUT] [-i JSON_INDENT] [-v]
                  filename [keyvar]
```

Extract key variables from Structured Text file.
For Structured Text format see library module StructuredText.py.

#### positional arguments:
  filename              Text file.
  keyvars               Optional key variables to find and return;
                        by default returns all key variables; def. 'None'.

#### options:
  -h, --help            show this help message and exit

  -d DELVARS, --delvars DELVARS
                        List of comma delimited keys to remove from output; def. 'None'.
  
  -S, --strict
                        Impose Strict mode; exit with error if a key variable in aline is not found.
                        If False, all free text is aggregated into key variable _FREETEXT_; def. False.
  
  -n, --no_comments
                        Ignore #comment lines. Default is to not ignore comment lines and store as `_COMMENT_n: comment`; def. 'False'.
  ...
  -f FREETEXT_NAME, --freetext_name FREETEXT_NAME
                        Name of key to collate free text; def. '_FREETEXT_'.
  
  -s SEP, --sep SEP     
                        Number of spaces after ':'; def. '1'.
  
  -l LF, --lf LF        
                        Number of linefeeds printed after each key variable; def. '2'.
  
  -k, --showkeys        
                        Print all keys found in file and exit; def. 'False'
  
  -j, --json            Output raw json; def. 'False'.
  
  -o OUTPUT, --output OUTPUT
                        Output to filename; def 'None'.
  
  -i JSON_INDENT, --json_indent JSON_INDENT
                        JSON output indent, integer or 'none'; def. '2'.
  
  -v, --verbose         Be not quiet; def. 'False'.

