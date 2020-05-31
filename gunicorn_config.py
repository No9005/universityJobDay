import multiprocessing

workers = 1
#workers = multiprocessing.cpu_count() * 2 + 1 #multiprocessing causes problems with flask sessions!
bind = 'unix:universityJobDay.sock' # name of sock
umask = 0o007
reload = True

#logging
accesslog = # path to accesslog file. eg: '/var/www/universityJobDay/universityJobDay/logs/access.log'
errorlog = # path to error log file. eg: '/var/www/universityJobDay/universityJobDay/logs/error.log'