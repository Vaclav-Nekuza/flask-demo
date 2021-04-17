# database setup
# this has to correspond to information in docker-compose or already running postgres database
DB_USER = "demo_user"
DB_PASS = "demo_pass"
DB_HOST = "postgres"  # only in case of using docker-compose otherwise use localhost
DB_PORT = "5432"
DB_NAME = "demo_db"
SCHEMA_NAME = "demo"
DB_CONN = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'general': {'format': 'Demo: %(asctime)s;%(levelname)s;%(message)s'},
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'general',
            'stream': 'ext://sys.stdout',
        },
        'system_logger': {
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'general',
            'address': ('syslog', 514),
            # 'level': 'DEBUG',
            'level': 'INFO',
            # 'level': 'WARNING',
            # 'level': 'ERROR',
            # 'level': 'CRITICAL',
        },
    },
    'loggers': {
        'flask.app': {
            # 'level': 'DEBUG',
            'level': 'INFO',
            # 'level': 'WARNING',
            # 'level': 'ERROR',
            # 'level': 'CRITICAL',
            'handlers': ['system_logger', 'console'],
            'propagate': False}
    }
}