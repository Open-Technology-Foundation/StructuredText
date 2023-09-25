#!/usr/bin/env python3.10
"""
# Module 'StructuredText'
 
The StructuredText format is a simple, flexible, and human-readable 
way to represent key-value pairs, with support for comments and 
multi-line values.

It can be used to store configuration settings, articles, 
transcripts, etc, with metadata, and other textual information,
where human readability is required or desirable.

Requires Python 3.10 or higher.

See the associated `st.extract` application script that uses this 
module at the shell.

## 'Strict' Mode
Strict mode in the extract function controls how the function 
behaves when it encounters certain conditions or errors. 
By default, Strict is set to False.

Strict requires that *all* data in the input source is formatted 
in `key:value` format.

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


"""
__version__ = '0.8.31'

import os
import sys
import re

class StructuredTextError(Exception):
    pass

class InvalidInputTypeError(StructuredTextError):
    pass

class DuplicateKeyError(StructuredTextError):
    pass

class FileNotFoundError(StructuredTextError):
    pass

def extract(
    input_source: str | dict | list[str], 
    *, 
    keyvars:list[str] | None  = [], 
    delvars:list[str] | None  = [],
    keyval_sep:str       = ':',    
    quiet: bool          = False, 
    strict: bool         = False, 
    no_comments: bool    = False,
    no_errors:bool       = False,
    freetext_name:str    = '_FREETEXT_'
  ) -> dict:
  """
  Extracts StructuredText formatted variables from an input source
  that can be a filename, list, or dictionary. 

  `StructuredText.extract` returns data from input source in the
  form of a `key:value` `dict` type.

  Data in/from `input_source` should contain text lines in the 
  format `key:value`, where `key` is any valid Python variable name. 
  Eg,
    DATE: 02/06/1957 00:02:00 

  Enclose multi-line values with Pythonesque triple-quotes (\""").
  Eg, 
    DATE_TIME_LOCATION: \"""
      DATE: 02/06/1957 
      TIME: 02:00:00
      LOCATION: Bali
      In Bali, the date is 02/06/1957 at 02:00:00.
    \"""

  Blank lines not within multi-line values are ignored.
  Lines starting with '#' are treated as comments and are stored
  in a special key variable of '_COMMENT_n'. Optionally, comment
  lines can be ignored using `no_comments=True`.
  If no valid key:value pairs are found in the file, and 
  `Strict` mode is not set, then the entire content of 
  `input_source` is stored and returned in special key variable
  '_FREETEXT_'.

  Args:
    input_source:   If `str`, denotes a filename to read.
                    If `dict`|`list`, denotes a dictionary or list. 
    keyvar:         If specified, only the `keyvar` variable from 
                    the list will be returned. 
                    Otherwise, all variables will be returned. 
    keyval_sep:     Separator string between `key` and `value`. 
                    Default ':'.
    delvars:        If a `list` of variables to remove from the 
                    output.
    quiet:          If True, warnings are not displayed. 
                    Default False.
    strict:         Strict mode. Default False.  All variables in 
                    input_source must be strictly complient with 
                    StructuredText format, otherwise an error is 
                    invoked. 
    no_comments:    If True, comments in the input_source are not 
                    outputted. Default False.
    no_errors:      bool      = False,
    freetext_name:  Name of keyvar where unstructured text is 
                    stored. Default is '_FREETEXT_'.

  Returns:
  dict: A dictionary where the keys are variable names from the 
  file, and the values are the corresponding values from the file. 
  If no valid variables are found, the dictionary will contain a 
  single item with the key '_FREETEXT_'.

  Example:
  >>> import StructuredText as st
  >>> st.extract('test01.transcript')
  {'VAR1': 'value1', 'VAR2': 'value2', 'VAR3': '\"\"\"\nmultiline value\n\"\"\"'}
  >>> st.extract('empty.txt')
  {'_FREETEXT_': 'the entire file content'}
  
  An example of a valid StructuredText file would be formatted like this:
  
  ```structuredtext
  # StructuredText Example format.

  # Each comment line is stored in the
  # special keyvars _COMMENT_n (unless disabled).
  PROJECT_NAME: Seeking Dharma

  TITLE: Aspects of Secularised Dharmas

  DATESTAMP: 02/06/1957 02:00:00
  LOCATION: Bali

  # Blank lines between the keyvars above 
  # are ignored.
  # Blank lines in a multi-line keyvar 
  # (like below) are *not* ignored.
  
  DESCRIPTION: \"""
  Cherrypicking The Dharma?
  Yes. I mean No. I mean, "The" Dharma??
  There are many dharmas.  
  Not all have a capital D.
  But many have commonalities in terms of
  values and practice.
  
  So it's not really cherrypicking.
  It's more like pickpocketing.

  Pickpocketing from the various dharmas, 
  both the flawed and the admirable, 
  from ancient to present times, 
  from whoever they are, and 
  from wherever they may be.

  It's about selecting basic wisdoms 
  and practices, that most suit our own 
  conditions and paths,
  from the commonality of the global wise.

  This commonality is a great resource for
  developing resilient personal and group 
  dharmas that are able to influence and 
  guide with wisdom and compassion, as an 
  alternative to reactivity and hate.
  \"""

  DEV_NOTE: \"""
  There is a limitation when assigning values 
  in multi-line keyvars where the value contains
  embedded triple-quotes (\""").

  Takeaway: Multi-line keyvar values need to 
  have embedded triple-quotes escaped, 
  eg, \"""
  \"""

  # Document ID
  ID: OKUSI420

  ```
  """

  source      = ''
  lines:list  = []
  if type(input_source) == str:
    file_path = input_source
    source    = f"file '{file_path}'"
    if not os.path.isfile(file_path):
      raise FileNotFoundError(f"No such {source}")
    try:
      with open(file_path, 'r') as f:
        file_content = f.read()
    except FileNotFoundError:
      raise FileNotFoundError(f"File '{file_path}' not found")
    except IOError:
      raise FileNotFoundError(f"File '{file_path}' could not be opened")
    # read text into lines list
    lines = file_content.splitlines()
  elif type(input_source) == list:
    source  = 'list'
    lines   = input_source
  elif type(input_source) == dict:
    source = 'dictionary'
    for key, value in input_source.items():
      if '\n' in value:
        lines.append(f'{key}:"""')
        lines.extend(value.splitlines())
        lines.append('"""')
      else:
        lines.append(f'{key}:{value}')
  else:
    raise InvalidInputTypeError(f"Invalid type in 'input_source' ('filename', list, or dict)")

  variables:dict    = {}
  FREETEXT          = ''
  if freetext_name != '_FREETEXT_' \
      and not re.compile(r'^([a-zA-Z][a-zA-Z0-9_]*)$').match(freetext_name):
    raise StructuredTextError(f"Invalid freetext_name '{freetext_name}'")
  ERRORS            = ''
  current_var_name  = ''
  current_var_value = ''
  multiline:bool    = False
  keyvar            = True if keyvars else False
  key_value_pattern = re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*' + re.escape(keyval_sep) + r'\s*(.*)$')

  comment_n:int     = 0
  verbose:bool      = not quiet

  for line in lines:
    if multiline:
      if re.search(r'^\s*\"\"\"\s*$', line):
        # r'^\s*\"\"\"\s*$' marks the end of a multiline variable
        if keyvars:
          if current_var_name in keyvars:
            variables[current_var_name] = current_var_value
            keyvars.remove(current_var_name)
            # shortcut exit if keyvars is now empty 
            if not keyvars: return variables
        else:
          variables[current_var_name] = current_var_value
        current_var_name  = ''
        current_var_value = ''
        multiline         = False
      else:
        current_var_value += ('\n' if current_var_value else '') + line
    else:
      if line.strip() == '':
        # Ignore all blank lines between keyvar declarations
        continue
      if line.lstrip().startswith('#'):
        if no_comments or keyvars: continue
        # Create `_COMMENT_?` variable from lines starting with '#'
        line = line.lstrip().lstrip('#').lstrip()
        comment_n+=1
        variables[f'_COMMENT_{comment_n}'] = line
        continue

      match = key_value_pattern.match(line)
      if match:
        # A new variable declaration
        current_var_name  = match.group(1).strip()
        # check for duplicate keys
        if current_var_name in variables:
          errmsg = f"Duplicate key '{current_var_name}' in {source}"
          if verbose or strict: print(errmsg, file=sys.stderr)
          if strict:
            raise StructuredTextError(errmsg)
          ERRORS += errmsg + '\n'
        current_var_value = match.group(2).strip()
        if current_var_value == '"""':
          # We have entered a multiline variable declaration
          current_var_value = ''
          multiline         = True
        else:
          if keyvar:
            if current_var_name in keyvars:
              variables[current_var_name] = current_var_value
              keyvars.remove(current_var_name)
              # shortcut exit if keyvars is now empty 
              if not keyvars: return variables
          else:
            variables[current_var_name] = current_var_value
          current_var_name  = ''
          current_var_value = ''
      else:
        # line contains no key, dump to FREETEXT if not strict mode
        errmsg = f"No variable key in '{line[:40]}...' in {source}"
        if (verbose or strict) and not keyvar: 
          print(errmsg, file=sys.stderr)
        if strict:
          raise StructuredTextError(errmsg)
        ERRORS += errmsg + '\n'
        FREETEXT += line.replace('"""', '\\"\\"\\"') + '\n'

  # Capture any trailing variable not terminated by """
  if current_var_name and not multiline:
    variables[current_var_name] = current_var_value.strip()

  """ If no variables were initialised, then assign entire 
      input_source contents to special variable FREETEXT """
  if not variables:
    errmsg = f"No key variables found in {source}"
    if verbose or strict:
      print(errmsg, file=sys.stderr)
    if strict:
      raise StructuredTextError(errmsg)
    if verbose: ERRORS += errmsg + '\n'
    FREETEXT = file_content

  if keyvars:
    """ 
    There's still content in the keyvars array, meaning not
    found 
    """
    errmsg = f"Variable/s '{keyvars}' not found in {source}."
    if verbose or strict: print(errmsg, file=sys.stderr)
    if strict:
      raise StructuredTextError(errmsg)
    ERRORS += errmsg + '\n'
    return {}

  if delvars:
    for key in delvars:
      if key in variables:
        del variables[key]
      else:
        errmsg = f"Variable '{key}' could not be deleted from {source}."
        if verbose or strict: print(errmsg, file=sys.stderr)
        ERRORS += errmsg + '\n'

  # If non-key:value text lines were found, then store them in 
  # special key variable _FREETEXT_
  if FREETEXT.strip():
    if '_TEXT_' in variables:
      FREETEXT = variables['_TEXT_'].strip() + '\n' + FREETEXT.strip()
      del variables['_TEXT_']
    if '_FREETEXT_' in variables:
      FREETEXT = variables['_FREETEXT_'].strip() + '\n' + FREETEXT.strip()
      del variables['_FREETEXT_']
    elif freetext_name in variables:
      FREETEXT = variables[freetext_name].strip() + '\n' + FREETEXT.strip()
    variables[freetext_name] = FREETEXT.strip()

  # If error messages were generated, then store them in 
  # special key variable _ERRORS_.
  if '_ERRORS_' in variables:
    # Delete any previous _ERRORS_ in input_source
    del variables['_ERRORS_']
  if ERRORS.strip() and not no_errors:
    variables['_ERRORS_'] = ERRORS.strip()

  return variables


def write_dict_to_st(
    variables:dict, 
    *, 
    keyvar:str      = None, 
    keyval_sep:str  = ':',    
    filename:str    = None, 
    lf:int          = 2, 
    sep:int         = 1,
    multiline       = 1
  ):
  """
    Print out all key variables in 'dict' to 
    StructuredText format to file or stdout. 
  """
  hfile    = open(filename, 'w') if filename else sys.stdout 
  printend = '\n' * max(0, lf)
  sepc     = ' '  * max(0, sep)
  for key, value in variables.items():
    if keyvar:
      if keyvar != key: continue
      if '\n' in value:
        # guard for nested terminating """
        valueq = value.replace('"""\n', '\"\"\"\n')
        print(f'{key}{keyval_sep}{sepc}\"\"\"\n{valueq}\n\"\"\"', end=printend, file=hfile)
      elif key.startswith('_COMMENT_'):
        print(f'#{sepc}{value}', end=printend, file=hfile)
      else:
        print(f'{key}{keyval_sep}{sepc}{value}', end=printend, file=hfile)
      if filename: hfile.close()
      return True
    if '\n' in value:
      if not multiline:
        #valueq = value.replace('"', '\\"')
        valueq = value.replace('\n', '\\\n').replace('"', '\\"')
        print(f"{key}{keyval_sep}{sepc}\"{valueq}\"", end=printend, file=hfile)
      else:
        valueq = value.replace('"""\n', '\"\"\"\n')
        print(f'{key}{keyval_sep}{sepc}\"\"\"\n{valueq}\n\"\"\"', end=printend, file=hfile)
    elif key.startswith('_COMMENT_'):
      # comments are kept together
      print(f'#{sepc}{value}', 
        end=('\n' if len(printend) else printend), 
        file=hfile)
    else:
      qt=''
      if (not multiline) and ' ' in value:
         value = value.replace('"', '\\"')
         qt='"'
      print(f'{key}{keyval_sep}{sepc}{qt}{value}{qt}', end=printend, file=hfile)
  if filename: hfile.close()
  return True

#fin
