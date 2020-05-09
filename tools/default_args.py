def elastic_arguments(parser):
    parser.add_argument('--host', type=str, help='the host where elastic runs. Default: localhost')
    parser.add_argument('--port', type=int, help='the port where elastic runs. Default: 9200')
    parser.add_argument('--index', type=str, help='the index in elastic to use. Defauls to ''catalog''')


def upload_arguments(parser):
    parser.add_argument('--recursive', '-r', action='store_true', help='Recurse into subdirectories. Defaults to FALSE')
    parser.add_argument('--move', '-m', action='store_true', help='Move the files, don\'t just copy them')
    parser.add_argument('--quiet', '-q', action='store_true', help='Recurse into subdirectories. Defaults to FALSE')
    parser.add_argument('--dryrun', '-d', action='store_true', help="""Do a dry run only, print what would be done. 
    Defaults to FALSE""")


def root_arguments(parser):
    parser.add_argument('--nas_root', type=str, help='Use this as catalog root on NAS')
    parser.add_argument('--dropbox_root', type=str, help='Use this as catalog root on Dropbox')
