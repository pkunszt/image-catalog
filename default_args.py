def default_arguments(parser):
    parser.add_argument('--host', type=str, help='the host where elastic runs. Default: localhost')
    parser.add_argument('--port', type=int, help='the port where elastic runs. Default: 9200')
    parser.add_argument('--index', type=str, help='the index in elastic to use. Defauls to ''catalog''')
