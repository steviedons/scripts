import urllib
import re
import json
import smtplib
from datetime import datetime

no_shares = 1585

def scrape(url_to_open, regex):
    html_open = urllib.urlopen(url_to_open)
    html = html_open.read()
    pattern = re.compile(regex)
    value = re.findall(pattern, html)
    return value


def noticeEMail(usr, psw, fromaddr, toaddr, subject, msg):
    """
    Sends an email message through GMail once the script is completed.
    Developed to be used with AWS so that instances can be terminated
    once a long job is done. Only works for those with GMail accounts.
    starttime : a datetime() object for when to start run time clock
 
    usr : the GMail username, as a string
 
    psw : the GMail password, as a string
    fromaddr : the email address the message will be from, as a string
    toaddr : a email address, or a list of addresses, to send the
    message to
    """
    # Initialize SMTP server
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(usr, psw)
    # Send email
    senddate = datetime.strftime(datetime.now(), '%Y-%m-%d')
    m = "Date: %s\r\nFrom: %s\r\nTo: %s\r\nSubject: %s\r\nX-Mailer: My-Mail\r\n\r\n" % (
        senddate, fromaddr, toaddr, subject)
    server.sendmail(fromaddr, toaddr, m + msg)
    server.quit()


def get_share_price():
    # price = scrape("http://uk.finance.yahoo.com/q?s=ERIC-B.ST", '<span id="yfs_l84_eric-b.st">(.+?)</span>')
    price = scrape("http://uk.finance.yahoo.com/q?s=ERIC-B.ST", 'data-reactid="250">(.+?)</span>')
    exrate = scrape("http://themoneyconverter.com/GBP/SEK.aspx", 'SEK/GBP = (.+?)</div>')

    value = (float(price[0]) / float(exrate[0])) * no_shares

    output = {'today': str(datetime.today()), 'todays_price': float(price[0]), 'todays_exchange': float(exrate[0]),
              'total_value': value}
    output_subject = "Total share value: %.2f" % output['total_value']
    output_msg = "Time the check was made: %s\nTodays share price: %.2f\nToday's exchange rate: %.2f\n" % (
        output['today'], output['todays_price'], output['todays_exchange'])

    print output_subject
    print output_msg

    with open('/home/steve/share_ouput.log', 'a') as f:
        json.dump(output, f, indent=2)

    noticeEMail('steviedonsnotif@gmail.com', '0TlKCN27ytHa', 'steviedonsnotif@gmail.com', 'steviedons@gmail.com',
                output_subject, output_msg)


if __name__ == '__main__':
    get_share_price()
