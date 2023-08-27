#!/usr/bin/env python
"""
usage: st.extract [-h] [-d DELVARS] [-S] [-e] [-n] [-f FREETEXT_NAME]
                  [-p KEYVAL_SEP] [-P KEYVAL_OUTPUT_SEP] [-s SEP] [-l LF] [-k]
                  [-j] [-o OUTPUT] [-i JSON_INDENT] [-v]
                  filename [keyvar]

Extract key variables from StructuredText file.

For StructuredText format see library module StructuredText.

positional arguments:
  filename              Text file to read into StructuredText format.
  keyvar                Optional key variable to find and return;
                        by default returns all key variables.

options:
  -h, --help            show this help message and exit
  -d DELVARS, --delvars DELVARS
                        List of comma delimited keys to remove from output;
                        def. None.
  -S, --strict          Impose Strict mode; exit with error if a key variable
                        is not found in a line. If False, all free text is
                        aggregated into keyvar _FREETEXT_; def. False.
  -e, --no_errors       Do not generate _ERRORS_ keyvar in output. Default is
                        to generate _ERRORS_ keyvar if errors occur; if set to
                        True, disables Strict mode (-S); def. False.
  -n, --no_comments     Ignore #comment lines. Default is to not ignore comment
                        line and store as '_COMMENT_n: comment text';
                        def. False.
  -f FREETEXT_NAME, --freetext_name FREETEXT_NAME
                        Name of key to collate free text; def. '_FREETEXT_'.
  -p KEYVAL_SEP, --keyval_sep KEYVAL_SEP
                        Key:Value separator; def. ':'.
  -P KEYVAL_OUTPUT_SEP, --keyval_output_sep KEYVAL_OUTPUT_SEP
                        Key:Value separator for output; def. ':'.
  -s SEP, --sep SEP     Number of spaces after ':' (keyval_sep); def. 1.
  -l LF, --lf LF        Number of linefeeds printed after each key variable;
                        def. 2.
  -k, --showkeys        Print all keys found in file and exit;
                        def. False
  -j, --json            Output raw json; def. False.
  -o OUTPUT, --output OUTPUT
                        Output to filename; def None.
  -i JSON_INDENT, --json_indent JSON_INDENT
                        JSON output indent, integer or 'none';
                        def. 2.
  -v, --verbose         Be not quiet; def. False.

"""
import os
import sys
import StructuredText as st
import argparse
import pydoc
 
if __name__ == '__main__':
  script_name = os.path.basename(__file__)
  # Manually check for the presence of '-V' or '--version'
  if '-V' in sys.argv or '--version' in sys.argv:
    print(st.__version__)
    sys.exit(0)
  p = argparse.ArgumentParser(
      description='Extract key variables from StructuredText file.\n\n'
        'For StructuredText format see library module StructuredText.',
      epilog='Examples:\n',
      formatter_class=argparse.RawTextHelpFormatter)

  p.add_argument('filename', 
      help=f'Text file to read into StructuredText format.')

  p.add_argument('keyvars', nargs='?', default=None, 
      help= 'List of comma-delimited keys to find and return, \n'
            'separated by commas; \n'
            'by default returns all key variables.')

  p.add_argument('-d', '--delvars', type=str, default=None, 
      help= "List of comma delimited keys to remove from output; \n" 
            "def. %(default)s.")

  p.add_argument('-S', '--strict', action='store_true', default=False, 
      help= 'Impose Strict mode; exit with error if a key variable \n' 
            'is not found in a line. If False, all free text is \n' 
            "aggregated into keyvar _FREETEXT_; def. %(default)s.")

  p.add_argument('-e', '--no_errors', action='store_true', default=False, 
      help= 'Do not generate _ERRORS_ keyvar in output. Default is \n'
            'to generate _ERRORS_ keyvar if errors occur; if set to \n'
            'True, disables Strict mode (-S); def. %(default)s.')

  p.add_argument('-n', '--no_comments', action='store_true', default=False, 
      help= 'Ignore #comment lines. Default is to not ignore comment \n'
            "line and store as '_COMMENT_n: comment text'; \n" 
            'def. %(default)s.')

  p.add_argument('-f', '--freetext_name', type=str, default='_FREETEXT_', 
      help= "Name of key to collate free text; def. '%(default)s'.")

  p.add_argument('-p', '--keyval_sep', type=str, default=':', 
      help= "Key:Value separator; def. '%(default)s'.")

  p.add_argument('-P', '--keyval_output_sep', type=str, default=':', 
      help= "Key:Value separator for output; def. '%(default)s'.")

  p.add_argument('-s', '--sep', type=int, default=1, 
      help= "Number of spaces after ':' (keyval_sep); def. %(default)s.")

  p.add_argument('-l', '--lf', type=int, default=2, 
      help= "Number of linefeeds printed after each key variable;\n"
            "def. %(default)s.")

  p.add_argument('-k', '--showkeys', action='store_true', default=False, 
      help= "Print all keys found in file and exit;\n"
            "def. %(default)s")

  p.add_argument('-j', '--json', action='store_true', default=False, 
      help= "Output raw json; def. %(default)s.")

  p.add_argument('-o', '--output', default=None, 
      help= "Output to filename; def %(default)s.")

  p.add_argument('-i', '--json_indent', default='2', 
      help= "JSON output indent, integer or 'none';\n" 
            "def. %(default)s.")

  p.add_argument('-v', '--verbose', action='store_true', default=False, 
      help= "Be not quiet; def. %(default)s.")

  p.add_argument('-V', '--version', action='store_true', default=False, 
      help= "Display version and exit; def. %(default)s.")

  def print_help_paged():
    help_text = p.format_help()
    pydoc.pager(help_text)
  p.print_help = print_help_paged

  args = p.parse_args()
  # print version and exit
  if args.version:
    print(__version__)
    sys.exit(0)
  if not os.path.exists(args.filename):
    print(f"{script_name}: {args.filename} does not exist.", file=sys.stderr)
    sys.exit(1)

  if args.keyvars:
    keyvars_list  = args.keyvars.replace(',',' ').split()
  else:
    keyvars_list = None

  if args.delvars:
    delvars_list  = args.delvars.replace(',',' ').split()
  else:
    delvars_list = None

  quiet = False if args.verbose else True

  # if no_errors specified, disable Strict
  if args.no_errors:
    args.strict = False
  
  try:
    """
    # from module StructuredText.py
    def extract(
        input_source: str | dict | list[str], 
        *, 
        keyvar: str | None = None, 
        keyval_sep: str=':',
        delvars:list[str]=[],
        quiet: bool = False, 
        strict: bool = False, 
        no_errors: bool = False,
        no_comments: bool = False,
        freetext_name:str = '_FREETEXT_'
      ) -> dict:
    """
    variables = st.extract(
        args.filename, 
        keyvars=keyvars_list,
        delvars=delvars_list,
        keyval_sep=args.keyval_sep,
        quiet=quiet, 
        strict=args.strict,
        no_errors=args.no_errors,
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
      with open(args.output, 'w') \
          if args.output else sys.stdout as hfile:
        print(json.dumps(variables, indent=indent), file=hfile)
      sys.exit(0)

    # Write out variables in StructuredText format to args.output
    """
    def write_dict_to_st(
      variables:dict, 
      *, 
      keyvar:str      = None, 
      keyval_sep:str  = ':',    
      filename:str    = None, 
      lf:int          = 2, 
      sep:int         = 1
    ):
    """
    st.write_dict_to_st(
        variables, 
        keyval_sep=args.keyval_output_sep,
        sep=args.sep, 
        lf=args.lf, 
        filename=args.output
      )

  except KeyboardInterrupt:
    print('^C\n', file=sys.stderr)
    sys.exit(1)

#fin
