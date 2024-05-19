# meLogger - easy plug and play logger

## Builder

### LoggerBuilder.build

Create a new logger on each call.

    name                logger name
    level               lowest logs level that will be displayed
    formats             a dict to describe the format for each log level
    terminator          end line character
    logs_path           path where logs are going be stored
    file_name           logs file name
    file_terminator     end line character for files
    file_mode           open mode - same as open(...,mode=<mode>)
    file_enc            encoding for file
    file_backups        number of replicas
    file_max_size       max size of a fil

### LoggerBuilder.add_console_handler

Allows to add a console handler on an existing logger.

    logger              existing Logger
    level               lowest logs level that will be displayed
    formats             a dict to describe the format for each log level
    terminator          end line character
    remove_handlers     allows to delete all StreamHandler handlers 

### LoggerBuilder.add_file_handler

Allows to add a file handler on an existing logger.

    logger              existing Logger
    file_level          lowest logs level that will be displayed
	file_formats        a dict to describe the format for each log level
	logs_path           path where logs are going be stored
	file_name           logs file name
	file_terminator     end line character for files
	file_mode           open mode - same as open(...,mode=<mode>)
	file_enc            encoding for file
	file_backups        number of replicas
	file_max_size       max size of a fil
	remove_handlers     allows to delete all StreamHandler handlers

## Logger

This is an extended class of logging.Logger that has an additional level **PLAIN**.

Default methods for generating logs were extended with some additional arguments:

    col_start   [Color start]   ANSI code for color
    pref        [Prefix]        Prefix for that line, it can be a combination of '', ' ', '\t' or '\n' 
    end         [Terminator]    Endline, it can be a combination of '' or '\n'

![warn.png](warn.png)

## Default Formats

    DEBUG      [GREY]         "%(pref)s%(col_start)s%(asctime)s [%(level_name)s] %(module)s (%(process)d) %(message)s%(col_end)s%(terminator)s"
    INFO       [DEFAULT]      "%(pref)s%(col_start)s%(asctime)s [%(level_name)s] %(module)s (%(process)d)%(col_end)s %(message)s%(terminator)s"
    WARN       [YELLOW]       "%(pref)s%(col_start)s%(asctime)s [%(level_name)s] %(module)s (%(process)d)%(col_end)s %(message)s%(terminator)s"
    ERROR      [RED]          "%(pref)s%(col_start)s%(asctime)s [%(level_name)s] %(module)s (%(process)d)%(col_end)s %(message)s%(terminator)s"
    CRITICAL   [STRONG RED]   "%(pref)s%(col_start)s%(asctime)s [%(level_name)s] %(module)s (%(process)d) %(message)s%(col_end)s%(terminator)s"
    PLAIN      [DEFAULT]      "%(pref)s%(col_start)s%(message)s%(col_end)s%(terminator)s"
