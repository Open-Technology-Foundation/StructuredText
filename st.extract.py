#!/usr/bin/python
"""
usage: st.extract [-h] [-d DELVARS] [-S] [-n] [-f FREETEXT_NAME] [-s SEP]
                  [-l LF] [-k] [-j] [-o OUTPUT] [-i JSON_INDENT] [-v]
                  filename [keyvar]

Extract key variables from Structured Text file.
For Structured Text format see library module StructuredText.

positional arguments:
  filename              Text file.
  keyvar                Optional key variable to find and return;
                        by default returns all key variables; def. 'None'.

options:
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

Examples:

"""
import os
import sys
import StructuredText as st
import argparse
import pydoc

if __name__ == '__main__':
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
      help=f'Impose Strict mode; exit with error if a key variable is not\n'
            'found in a line. If False, all free text is aggregated into\n'
            "keyvar _FREETEXT_; def. '%(default)s'.")
  p.add_argument('-e', '--no_errors', action='store_true', default=False, 
      help=f'Do not generate _ERRORS_ keyvar in output. Default is to\n'
            "generate _ERRORS_ keyvar if errors occur; if set to True,\n"
            "disables Strict mode (-S); def. '%(default)s'.")
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
        delvars:list[str]=[],
        quiet: bool = False, 
        strict: bool = False, 
        no_comments: bool = False,
        freetext_name:str = '_FREETEXT_'
      ) -> dict:
    """
    variables = st.extract(
        args.filename, 
        keyvar=args.keyvar,
        delvars=delvars_list,
        quiet=quiet, 
        strict=args.strict,
        no_comments=args.no_comments,
        no_errors=args.no_errors,
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
    st.write_dict_to_st(
        variables, 
        sep=args.sep, 
        lf=args.lf, 
        filename=args.output
      )

  except KeyboardInterrupt:
    print('^C\n', file=sys.stderr)
    sys.exit(1)

#fin
