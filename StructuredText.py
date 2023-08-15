#!/usr/bin/python3.10
import os
import sys
import re

"""
# Module 'StructuredText'

The StructuredText format is a simple, flexible, and human-readable 
way to represent key-value pairs, with support for comments and 
multi-line values.

It can be used to store configuration settings, articles, 
transcripts, etc, with metadata, and other textual information,
where human readability is required or desirable.

Requires Python 3.10 or higher.

## 'Strict' Mode
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


"""

def extract(
    input_source: str | dict | list[str], 
    *, keyvar: str | None = None, 
    delvars:list[str]=[],
    quiet: bool = False, 
    strict: bool = False, 
    no_comments: bool = False,
    freetext_name:str = '_FREETEXT_'
  ) -> dict:
  """
  Extracts StructuredText formatted variables from an input source
  that can be a filename, list, or dictionary. 

  `StructuredText.extract` returns data in key:value format as 
  a dictionary.

  Data in `input_source` should contain text lines in the format 
  KEY:VALUE, where KEY is any valid Python variable name. 

  Multi-line values are enclosed in Python-style triple double 
  quotes (\"\"\").

  Blank lines that are not within multi-line values are ignored.

  Lines starting with '#' are treated as comments and are stored
  in a special key variable of '_COMMENT_n'. Optionally, comment
  lines can be ignored using `no_comments=True`.

  If no valid key:value pairs are found in the file, and 
  `Strict` mode is not set, then the entire content of 
  `input_source` is stored and returned in special key variable
  '_FREETEXT_'.

  Args:

  Returns:
  dict: A dictionary where the keys are variable names from the 
  file, and the values are the corresponding values from the file. 
  If no valid variables are found, the dictionary will contain a 
  single item with the key '_FREETEXT_'.

  Example:
  >>> extract('youtube_video.transcript')
  {'VAR1': 'value1', 'VAR2': 'value2', 'VAR3': '\"\"\"\nmultiline value\n\"\"\"'}
  >>> extract('empty.txt')
  {'_FREETEXT_': 'the entire file content'}
  
  An example of a valid StructuredText file would be formatted like this:
  
  ```
  # This is a comment
  VAR1: value1
  
  VAR2: value2
  
  VAR3: \"\"\"
  This is a multi-line
  value of any
  length.

  \"\"\"
  
  VAR4: value4
  
  ```

  """

  source      = ''
  lines:list  = []
  if type(input_source) == str:
    file_path = input_source
    source    = f"file '{file_path}'"
    if not os.path.isfile(file_path):
      print(f"No such {source}", file=sys.stderr)
      sys.exit(1)
    try:
      with open(file_path, 'r') as f:
        file_content = f.read()
    except FileNotFoundError:
      print(f"File '{file_path}' not found", file=sys.stderr)
      sys.exit(1)
    except IOError:
      print(f"File '{file_path}' could not be opened", file=sys.stderr)
      sys.exit(1)
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
    print(f"Invalid type in 'input_source' ('filename', list, or dict)", file=sys.stderr)
    sys.exit(1)

  variables:dict    = {}
  FREETEXT          = ''
  if freetext_name != '_FREETEXT_' \
      and not re.compile(r'^([a-zA-Z][a-zA-Z0-9_]*)$').match(freetext_name):
    print(f"Invalid freetext_name '{freetext_name}'")
    sys.exit(1)
  ERRORS            = ''
  current_var_name  = ''
  current_var_value = ''
  multiline:bool    = False
  key_value_pattern = re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*)$')
  comment_n:int     = 0
  verbose:bool      = not quiet

  for line in lines:
    if multiline:
      if line.rstrip() == '"""':
        # '^"""\s*$' marks the end of a multiline variable
        variables[current_var_name] = current_var_value.strip()
        # shortcut exit if keyvar is found 
        if keyvar and keyvar == current_var_name:
          return { keyvar: current_var_value }
        current_var_name  = ''
        current_var_value = ''
        multiline         = False
      else:
        current_var_value += '\n' + line
    else:
      if line.strip() == '':
        # Ignore all blank lines
        continue
      if line.lstrip().startswith('#'):
        if no_comments:
          continue
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
          if strict: sys.exit(1)
          ERRORS += errmsg + '\n'
        current_var_value = match.group(2).strip()
        if current_var_value == '"""':
          # We have entered a multiline variable declaration
          current_var_value = ''
          multiline         = True
        else:
          # assign single line variable
          variables[current_var_name] = current_var_value
          # shortcut exit if keyvar is found
          if keyvar and keyvar == current_var_name:
            return { keyvar: current_var_value }
          current_var_name  = ''
          current_var_value = ''
      else:
        # line contains no key, dump to FREETEXT if not strict mode
        errmsg = f"No variable key in '{line[:40]}...' in {source}"
        if (verbose or strict) and not keyvar: 
          print(errmsg, file=sys.stderr)
        if strict: sys.exit(1)
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
    if strict: sys.exit(1)
    if verbose: ERRORS += errmsg + '\n'
    FREETEXT = file_content

  if keyvar:
    """ If keyvar is specified, only return that keyvar:value, 
        otherwise return {} """
    # This should not be necessary, as keyvar takes a shortcut
    if keyvar in variables:
      return { keyvar: variables.get(keyvar, '') }
    errmsg = f"Variable '{keyvar}' not found in {source}."
    if verbose or strict: print(errmsg, file=sys.stderr)
    if strict: sys.exit(1)
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
  if ERRORS.strip():
    variables['_ERRORS_'] = ERRORS.strip()

  return variables


def write(variables:dict, *, 
      keyvar=None, 
      filename=None, 
      lf:int=2, 
      sep:int=1):
  """ Print out key variables in the 'dict' one by one in 
      StructuredText format. """
  hfile    = open(filename, 'w') if filename else sys.stdout 
  printend = '\n' * max(0, lf)
  sepc     = ' '  * max(0, sep)
  for key, value in variables.items():
    if keyvar:
      if keyvar != key: continue
      if '\n' in value:
        # guard for nested terminating """
        valueq = value.replace('"""\n', '\"\"\"\n')
        print(f'{key}:{sepc}\"\"\"\n{valueq}\n\"\"\"', end=printend, file=hfile)
      elif key.startswith('_COMMENT_'):
        print(f'#{sepc}{value}', end=printend, file=hfile)
      else:
        print(f'{key}:{sepc}{value}', end=printend, file=hfile)
      if filename: hfile.close()
      return True
    if '\n' in value:
      valueq = value.replace('"""\n', '\"\"\"\n')
      print(f'{key}:{sepc}\"\"\"\n{valueq}\n\"\"\"', end=printend, file=hfile)
    elif key.startswith('_COMMENT_'):
      print(f'#{sepc}{value}', end=printend, file=hfile)
    else:
      print(f'{key}:{sepc}{value}', end=printend, file=hfile)
  if filename: hfile.close()
  return True


# ==============================================================================
#!/usr/bin/python
#import os
#import sys
#import StructuredText as st

if __name__ == '__main__':
  import argparse
  import pydoc
  script_name = os.path.basename(__file__)
  p = argparse.ArgumentParser(
      description='Extract key variables from Structured Text file.\n'
        'For Structured Text format see library module StructuredText.',
      epilog='Examples:\n',
      formatter_class=argparse.RawTextHelpFormatter)
  p.add_argument('filename', 
      help=f'Text file.')
  p.add_argument('keyvar', nargs='?',   default=None, 
      help=f'Optional key variable to find and return;\n'
            "by default returns all key variables; def. '%(default)s'.")
  p.add_argument('-d', '--delvars',     type=str, default=None, 
      help=f"List of comma delimited keys to remove from output; def. '%(default)s'.")
  p.add_argument('-S', '--strict',      action='store_true', default=False, 
      help=f'Impose Strict mode; exit with error if a key variable in a'
            'line is not found.\n'
            "If False, all free text is aggregated into key variable"
            "_FREETEXT_; def. '%(default)s'.")
  p.add_argument('-n', '--no_comments', action='store_true', default=False, 
      help=f'Ignore #comment lines. Default is to not ignore comment lines\n'
            "and store as '_COMMENT_n: comment'; def. '%(default)s'.")
  p.add_argument('-f', '--freetext_name', type=str, default='_FREETEXT_', 
      help=f"Name of key to collate free text; def. '%(default)s'.")
  p.add_argument('-s', '--sep',         type=int, default=1, 
      help=f"Number of spaces after ':'; def. '%(default)s'.")
  p.add_argument('-l', '--lf',          type=int, default=2, 
      help=f"Number of linefeeds printed after each key variable; def. '%(default)s'.")
  p.add_argument('-k', '--showkeys',    action='store_true', default=False, 
      help=f"Print all keys found in file and exit; def. '%(default)s'")
  p.add_argument('-j', '--json',        action='store_true', default=False, 
      help=f"Output raw json; def. '%(default)s'.")
  p.add_argument('-o', '--output',      default=None, 
      help=f"Output to filename; def '%(default)s'.")
  p.add_argument('-i', '--json_indent', default='2', 
      help=f"JSON output indent, integer or 'none'; def. '%(default)s'.")
  p.add_argument('-v', '--verbose',     action='store_true', default=False, 
      help=f"Be not quiet; def. '%(default)s'.")
  def print_help_paged():
    help_text = p.format_help()
    pydoc.pager(help_text)
  p.print_help = print_help_paged

  args = p.parse_args()
  if not os.path.exists(args.filename):
    print(f"{script_name}: {args.filename} does not exist.", file=sys.stderr)
    sys.exit(1)

  if args.delvars:
    delvars_list  = args.delvars.replace(',',' ').split()
  else:
    delvars_list = None

  quiet = False if args.verbose else True
  try:
    """
    def extract(
        input_source: str | dict | list[str], 
        *, 
        keyvar: str | None = None, 
        delvars:list[str]=[],
        quiet: bool = False, 
        strict: bool = False, 
        no_comments: bool = False,
        freetext_name:str = '_FREETEXT_'
      ) -> dict:
    """
    variables = extract(
        args.filename, 
        keyvar=args.keyvar,
        delvars=delvars_list,
        quiet=quiet, 
        strict=args.strict,
        no_comments=args.no_comments,
        freetext_name=args.freetext_name
      )

    if not variables:
      sys.exit(1)

    # Show found keys only then exit
    if args.showkeys:
      for key in variables: print(key)
      sys.exit(0)

    # Print out raw json then exit
    if args.json:
      import json
      indent = None if args.json_indent == '' \
          or args.json_indent.lower() == 'none' \
          else max(0, int(args.json_indent))
      with open(args.output, 'w') if args.output else sys.stdout as hfile:
        print(json.dumps(variables, indent=indent), file=hfile)
      sys.exit(0)

    # Write out variables in StructuredText format to args.output
    write(
        variables, 
        sep=args.sep, 
        lf=args.lf, 
        filename=args.output
      )

  except KeyboardInterrupt:
    print('^C\n', file=sys.stderr)
    sys.exit(1)

#fin
