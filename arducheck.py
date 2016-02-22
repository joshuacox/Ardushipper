#! /usr/bin/env python

###############################################################################
# Thalhalla ardushipper code
#
# Notes
# - The RHEL boxes I work on are currently limited to Python 2.6.6, hence the
#   use of (deprecated) optparse. If I can ever get them all updated to
#   Python 2.7 (or better yet, 3.3), I'll switch to argparse
# - This template runs in 2.6-3.3. Any changes made will need to be appropriate
#   to the Python distro you want to use
#
###############################################################################

__author__ = 'Josh Cox'
__version__= 0.1

from optparse import OptionParser, OptionGroup
import logging as log
import serial
import syslog
from time import sleep

## These will override any args passed to the script normally. Comment out after testing.
#testargs = '--help'
#testargs = '--version'
#testargs = '-vvv'

def main():
    ## Parse command-line arguments
    args, args2 = parse_args()

    """ Main plugin logic goes here """
    log.debug('Main Logic')
    nagiosExitCode = 0
    nagiosExitMessage = 'OK: Humidity is normal'
    log.debug('Starting Serial')
    ser = serial.Serial(args.device, 115200, timeout=15)
    # a write to serial is necessary
    # to kick off arduino
    ser.write("hello")
    #log.debug('Opening Syslog')
    #syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_DAEMON)
    count = 0
    bsq26humidity = -1;
    log.debug('Opening While loop')
    while True:
        ser.write("1")
        count = 1;
        rawdata = ser.readline()
        buff1 = "%s" % rawdata.split(b'\0',1)[0]
        data = "%s" % buff1.strip()
        log.debug('data:')
        log.debug(data)
        if "BSQ26-ENDTRANSMISSION" in data:
            count+= 1
        if "BSQ26-Humidity" in data:
            bsq26humidity = data.split(' ')[1]
            log.debug('Humidity:')
            log.debug(data)
        if count > 1:
            log.debug('break')
            break
        if count > 0:
            if not data.isspace():
                if len(data) > 0:
                    log.debug('Got:', data)
                    #syslog.syslog(str(data))
            sleep(0.5)
        ser.write("1")
    ser.close()

    floatHumidity = float( bsq26humidity )
    nagiosExitMessage = 'OK: Humidity is normal'
    nagiosExitMessage = 'OK: Humidity', floatHumidity 'is normal'

    if floatHumidity < args.lowarn:
        nagiosExitCode = 1
        nagiosExitMessage = WARN: Humidity floatHumidity is low, under threshold args.lowarn
    if floatHumidity < args.locrit:
        nagiosExitCode = 2
        nagiosExitMessage = 'CRITICAL: Humidity', floatHumidity ,'is extremely low, under threshold', args.locrit
    if floatHumidity > args.warn:
        nagiosExitCode = 1
        nagiosExitMessage = 'WARN: Humidity', floatHumidity ,'is high, over threshold', args.warn
    if floatHumidity > args.crit:
        nagiosExitCode = 2
        nagiosExitMessage = 'CRITICAL: Humidity', floatHumidity ,'is extremely high, over threshold', args.crit
    if floatHumidity == -1:
        nagiosExitCode = 3
        nagiosExitMessage = 'UNKNOWN: Humidity is unknown', floatHumidity


    """ Main plugin logic ends here """


    ## Uncomment to test logging levels against verbosity settings
    # log.debug('debug message')
    # log.info('info message')
    # log.warning('warning message')
    # log.error('error message')
    # log.critical('critical message')
    # log.fatal('fatal message')

    #gtfo(0)
    gtfo(nagiosExitCode, nagiosExitMessage)


def parse_args():
    """ Parse command-line arguments """

    parser = OptionParser(usage='usage: %prog [-v|vv|vvv] [options]',
                          version='{0}: v.{1} by {2}'.format('%prog', __version__, __author__))

    ## Verbosity (want this first, so it's right after --help and --version)
    parser.add_option('-v', help='Set verbosity level',
                      action='count', default=0, dest='v')

    ## CLI arguments specific to this script
    group = OptionGroup(parser,'Plugin Options')
    group.add_option('-x', '--extra', help='Your option here',
                     default=None)

    ## Common CLI arguments
    parser.add_option('-c', '--critical', help='Set the critical threshold. Default: %(default)s',
                      default=85, type=float, dest='crit', metavar='##')
    parser.add_option('-w', '--warning', help='Set the warning threshold. Default: %(default)s',
                      default=75, type=float, dest='warn', metavar='##')
    parser.add_option('-l', '--locrit', help='Set the low critical threshold. Default: %(default)s',
                      default=4, type=float, dest='locrit', metavar='##')
    parser.add_option('-n', '--lowarn', help='Set the low warning threshold. Default: %(default)s',
                      default=8, type=float, dest='lowarn', metavar='##')
    parser.add_option('-d', '--device', help='Set the device to listen to. Default: %(default)s',
                      default='/dev/USB0', dest='device', metavar='##')

    parser.add_option_group(group)

    ## Try to parse based on the testargs variable. If it doesn't exist, use args
    try:
        args, args2 = parser.parse_args(testargs.split())
    except NameError:
        args, args2 = parser.parse_args()

    ## Set the logging level based on the -v arg
    log.getLogger().setLevel([log.ERROR, log.WARN, log.INFO, log.DEBUG][args.v])

    log.debug('Parsed arguments: {0}'.format(args))
    log.debug('Other  arguments: {0}'.format(args2))

    return args, args2

def gtfo(exitcode, message=''):
    """ Exit gracefully with exitcode and (optional) message """

    log.debug('Exiting with status {0}. Message: {1}'.format(exitcode, message))

    if message:
        print(message)
    exit(exitcode)

if __name__ == '__main__':
    ## Initialize logging before hitting main, in case we need extra debuggability
    log.basicConfig(level=log.DEBUG, format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
    main()
