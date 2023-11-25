# meLogger - easy plug and play logger

## Builder

Provide a singleton instance for you application by execution method **LoggerBuilder.get_logger**.

Arguments available.

    name – Logger name
    level – Lowest logs level that will be displayed
    formats – A dict to describe the format for each log level
    terminator – end line character
    logs_path – path where logs are going be stored
    file_name – logs file name
    file_terminator – end line character for files
    file_mode – open mode - same as open(...,mode=<mode>)
    file_enc – encoding for file
    file_backups – number of replicas
    file_max_size – max size of a fil

## Logger

This is an extended class of logging.Logger that has an additional level **PLAIN** a custom ways to change the colors on each log message.

    info_green - Force next INFO log to be green
    info_color - Allows to set a color for next INFO log message
    plain - Print message without any format. Has 2 args: 
            Color - change the color for next message\n
            end - end line character override for next message

For each log message we can modify inline the color and terminator as follows:

    logger.warning("First dummy message")
    logger.warning("Dummy warning message", extra={"col_start": Colors.COL.BLUE, "end": "\n\n"})
    logger.warning("Third dummy message")

![warn.png](warn.png)

## Default Formats

    DEBUG - GREY          - "%(start)s%(col_start)s%(asctime)s [%(levelname)s] %(module)s (%(process)d) %(message)s%(col_end)s%(terminator)s"),
    INFO - DEFAULT        - "%(start)s%(col_start)s%(asctime)s [%(levelname)s] %(module)s (%(process)d)%(col_end)s %(message)s%(terminator)s"),
    WARN - YELLOW         - "%(start)s%(col_start)s%(asctime)s [%(levelname)s] %(module)s (%(process)d)%(col_end)s %(message)s%(terminator)s"),
    ERROR - RED           - "%(start)s%(col_start)s%(asctime)s [%(levelname)s] %(module)s (%(process)d)%(col_end)s %(message)s%(terminator)s"),
    CRITICAL - STRONG RED - "%(start)s%(col_start)s%(asctime)s [%(levelname)s] %(module)s (%(process)d) %(message)s%(col_end)s%(terminator)s"),
    PLAIN - DEFAULT       - "%(start)s%(col_start)s%(message)s%(col_end)s%(terminator)s")