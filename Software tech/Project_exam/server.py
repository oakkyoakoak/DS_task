#!/usr/bin/env python

# This is a simple web server for a traffic counting application.
# It's your job to extend it by adding the backend functionality to support
# recording the traffic in a SQL database. You will also need to support
# some predefined users and access/session control. You should only
# need to extend this file. The client side code (html, javascript and css)
# is complete and does not require editing or detailed understanding.

# import the various libraries needed
import http.cookies as Cookie  # some cookie handling support
from http.server import BaseHTTPRequestHandler, HTTPServer
from sqlite3.dbapi2 import Time  # the heavy lifting of the web server
import urllib  # some url parsing support
import json  # support for json encoding
import sys  # needed for agument
import sqlite3
import random
import datetime
import time
import string


def get_unix_time_traffic():
    given_date = access_database_with_result(
        "traffic.db", "select MAX(time) from traffic where mode=1"
    )[0][0]
    unix_start_date = 0
    unix_end_date = 0
    if given_date != 0:
        year = datetime.datetime.fromtimestamp(given_date).strftime("%Y")
        month = datetime.datetime.fromtimestamp(given_date).strftime("%m")
        date = datetime.datetime.fromtimestamp(given_date).strftime("%d")
        time_start_midnight_date = year + "-" + month + "-" + date + " " + "00:00:00"
        time_start_midnight_date = datetime.datetime.strptime(
            time_start_midnight_date, "%Y-%m-%d %H:%M:%S"
        )
        unix_start_date = int(datetime.datetime.timestamp(time_start_midnight_date))
        time_end_date = year + "-" + month + "-" + date + " " + "23:59:59"
        time_end_date = datetime.datetime.strptime(time_end_date, "%Y-%m-%d %H:%M:%S")
        unix_end_date = int(datetime.datetime.timestamp(time_end_date))
    return unix_start_date, unix_end_date


def get_unix_start_date():
    given_date = access_database_with_result(
        "traffic.db", "select MAX(end) from session"
    )[0][0]
    unix_start_date = 0
    if given_date != 0:
        year = datetime.datetime.fromtimestamp(given_date).strftime("%Y")
        month = datetime.datetime.fromtimestamp(given_date).strftime("%m")
        date = datetime.datetime.fromtimestamp(given_date).strftime("%d")
        time_start_midnight_date = year + "-" + month + "-" + date + " " + "00:00:00"
        time_start_midnight_date = datetime.datetime.strptime(
            time_start_midnight_date, "%Y-%m-%d %H:%M:%S"
        )
        unix_start_date = int(datetime.datetime.timestamp(time_start_midnight_date))
    return unix_start_date


def get_unix_end_date():
    given_date = access_database_with_result(
        "traffic.db", "select MAX(end) from session"
    )[0][0]
    unix_end_date = 0
    if given_date != 0:
        year = datetime.datetime.fromtimestamp(given_date).strftime("%Y")
        month = datetime.datetime.fromtimestamp(given_date).strftime("%m")
        date = datetime.datetime.fromtimestamp(given_date).strftime("%d")
        time_end_date = year + "-" + month + "-" + date + " " + "23:59:59"
        time_end_date = datetime.datetime.strptime(time_end_date, "%Y-%m-%d %H:%M:%S")
        unix_end_date = int(datetime.datetime.timestamp(time_end_date))
    return unix_end_date


def get_unix_start_week():
    given_date = access_database_with_result(
        "traffic.db", "select MAX(end) from session"
    )[0][0]
    unix_start_week = 0
    if given_date != 0:
        year = datetime.datetime.fromtimestamp(given_date).strftime("%Y")
        month = datetime.datetime.fromtimestamp(given_date).strftime("%m")
        date = datetime.datetime.fromtimestamp(given_date).strftime("%d")
        time_start_midnight_date = year + "-" + month + "-" + date + " " + "00:00:00"
        time_start_midnight_week = datetime.datetime.strptime(
            time_start_midnight_date, "%Y-%m-%d %H:%M:%S"
        ) - datetime.timedelta(days=6)
        unix_start_week = int(datetime.datetime.timestamp(time_start_midnight_week))
    return unix_start_week


def get_unix_end_week():
    get_unix_end_week = get_unix_end_date()
    return get_unix_end_week


def get_unix_end_month():
    get_unix_end_month = get_unix_end_date()
    return get_unix_end_month


def get_unix_now():
    unix_now = int(time.time())  # given date
    return unix_now


def format_datetime(time):
    unix = datetime.datetime.fromtimestamp(time).strftime("%Y-%m-%d %H:%M:%S")
    datetime_f = datetime.datetime.strptime(unix, "%Y-%m-%d %H:%M:%S")
    return datetime_f


def get_unix_start_month():
    given_date = access_database_with_result(
        "traffic.db", "select MAX(end) from session"
    )[0][0]
    full_date_unix = 0
    if given_date != 0:
        given_date_format = format_datetime(given_date)
        year_check = given_date_format.year
        this_month = given_date_format.month
        this_date = given_date_format.day
        if year_check % 4 == 0:
            year_case = {
                0: 31,
                1: 31,
                2: 29,
                3: 31,
                4: 30,
                5: 31,
                6: 30,
                7: 31,
                8: 31,
                9: 30,
                10: 31,
                11: 30,
                12: 31,
            }
        else:
            year_case = {
                0: 31,
                1: 31,
                2: 28,
                3: 31,
                4: 30,
                5: 31,
                6: 30,
                7: 31,
                8: 31,
                9: 30,
                10: 31,
                11: 30,
                12: 31,
            }

        max_last_month = year_case[(this_month - 1) % 12]

        if this_date + 1 > max_last_month:
            date_last_month = 1
        else:
            date_last_month = this_date + 1

        if (this_month - 1) % 12 == 0 and date_last_month != 1:
            year = year_check - 1
        else:
            year = year_check

        if this_month - 1 == 0 and date_last_month != 1:
            last_month = 12
        elif date_last_month != 1:
            last_month = this_month - 1
        else:
            last_month = this_month

    full_date = (
        str(year) + "-" + str(last_month) + "-" + str(date_last_month) + " 00:00:00"
    )
    full_date_format = datetime.datetime.strptime(full_date, "%Y-%m-%d %H:%M:%S")
    full_date_unix = int(datetime.datetime.timestamp(full_date_format))

    return full_date_unix


def check_punc(text):
    response = False
    for c in text:
        if c in string.punctuation:
            response = True
    if text.strip() == "":
        response = True
    if any(a.isupper() for a in text):
        response = True
    return response


def access_database(dbfile, query, word_query=""):
    connect = sqlite3.connect(dbfile)
    cursor = connect.cursor()
    cursor.execute(query, word_query)
    connect.commit()
    connect.close()


# access_database requires the name of an sqlite3 database file and the query.
# It returns the result of the query
def access_database_with_result(dbfile, query, word_query=""):
    connect = sqlite3.connect(dbfile)
    cursor = connect.cursor()
    rows = cursor.execute(query, word_query).fetchall()
    connect.commit()
    connect.close()
    return rows


def build_response_refill(where, what):
    """This function builds a refill action that allows part of the
    currently loaded page to be replaced."""
    return {"type": "refill", "where": where, "what": what}


def build_response_redirect(where):
    """This function builds the page redirection action
    It indicates which page the client should fetch.
    If this action is used, only one instance of it should
    contained in the response and there should be no refill action."""
    return {"type": "redirect", "where": where}


def handle_validate(iuser, imagic):
    """Decide if the combination of user and magic is valid"""
    ## alter as required
    if iuser == "!" and imagic == "":
        return False
    elif iuser == "" and imagic == "":
        return False
    else:
        check = access_database_with_result(
            "traffic.db",
            "select * from session where userid=@0 and magic=@1;",
            (iuser, imagic),
        )
        if len(check) > 0:
            return True
        else:
            return False


def handle_delete_session(iuser, imagic):
    """Remove the combination of user and magic from the data base, ending the login"""
    response = []
    parameter = 0
    handle_logout_request(iuser, imagic, parameter)
    ## alter as required
    response.append(build_response_refill("message", "user in-use."))
    user = "!"
    magic = ""

    return [user, magic, response]


def handle_login_request(iuser, imagic, parameters):
    """A user has supplied a username (parameters['usernameinput'][0])
    and password (parameters['passwordinput'][0]) check if these are
    valid and if so, create a suitable session record in the database
    with a random magic identifier that is returned.
    Return the username, magic identifier and the response action set."""
    response = []
    if handle_validate(iuser, imagic) == True:
        # the user is already logged in, so end the existing session.
        handle_delete_session(iuser, imagic)
    try:
        username = parameters["usernameinput"][0]
        password = parameters["passwordinput"][0]
    except KeyError:
        response.append(
            build_response_refill("message", "Please input username and password")
        )
        user = "!"
        magic = ""
        return [user, magic, response]

    ## alter as required (done-login one person)
    check = access_database_with_result(
        "traffic.db",
        "select * from users where username= @0 and password= @1;",
        (username, password),
    )

    if len(check) > 0:
        response.append(build_response_redirect("/page.html"))
        magic = random.randint(1, 10000000000000)
        time = get_unix_now()
        userid = access_database_with_result(
            "traffic.db", "select userid from users where username=@0;", (username,)
        )[0][0]
        access_database(
            "traffic.db",
            "INSERT INTO \
                session (userid,magic,start,end) VALUES \
                (@0,@1,@2,0)",
            (userid, magic, time),
        )
        user = userid

    else:  ## The user is not valid
        response.append(build_response_refill("message", "Invalid password"))
        user = "!"
        magic = ""
    return [user, magic, response]


def handle_add_request(iuser, imagic, parameters):
    """The user has requested a vehicle be added to the count
    parameters['locationinput'][0] the location to be recorded
    parameters['occupancyinput'][0] the occupant count to be recorded
    parameters['typeinput'][0] the type to be recorded
    Return the username, magic identifier (these can be empty  strings) and the response action set."""
    user = iuser
    magic = imagic
    response = []
    ## alter as required
    if handle_validate(iuser, imagic) != True:
        # Invalid sessions redirect to login
        response.append(build_response_redirect("/index.html"))
    else:  ## a valid session so process the addition of the entry.

        try:
            location = parameters["locationinput"][0]
            occupant = parameters["occupancyinput"][0]
            type_name = parameters["typeinput"][0]
            if check_punc(location) != True:
                type_dict = {
                    "car": 0,
                    "van": 1,
                    "truck": 2,
                    "taxi": 3,
                    "other": 4,
                    "motorbike": 5,
                    "bicycle": 6,
                    "bus": 7,
                }
                type = type_dict[type_name]
                time_now = get_unix_now()
                location = location.strip()
                session_id = access_database_with_result(
                    "traffic.db",
                    "select sessionid from session where magic=@0",
                    (imagic,),
                )[0][0]
                number_row = (
                    len(
                        access_database_with_result(
                            "traffic.db", "select * from traffic"
                        )
                    )
                    + 1
                )
                access_database(
                    "traffic.db",
                    "INSERT INTO traffic VALUES (@0,@1,@2,@3,@4,@5,1)",
                    (number_row, session_id, time_now, type, occupant, location),
                )
                count_1 = len(
                    access_database_with_result(
                        "traffic.db",
                        "select * from traffic where mode=1 and sessionid=@0",
                        (session_id,),
                    )
                )
                response.append(build_response_refill("message", "Entry added."))
                response.append(build_response_refill("total", str(count_1)))
            else:
                response.append(build_response_refill("message", "Invalid input"))
        except KeyError:
            response.append(build_response_refill("message", "Invalid input"))
    return [user, magic, response]


def handle_undo_request(iuser, imagic, parameters):
    """The user has requested a vehicle be removed from the count
    This is intended to allow counters to correct errors.
    parameters['locationinput'][0] the location to be recorded
    parameters['occupancyinput'][0] the occupant count to be recorded
    parameters['typeinput'][0] the type to be recorded
    Return the username, magic identifier (these can be empty  strings) and the response action set."""
    ## alter as required
    user = iuser
    magic = imagic
    response = []
    if handle_validate(iuser, imagic) != True:
        # Invalid sessions redirect to login
        response.append(build_response_redirect("/index.html"))
    else:  ## a valid session so process the recording of the entry.
        user = iuser
        magic = imagic
        session_id = access_database_with_result(
            "traffic.db", "select sessionid from session where magic=@0", (imagic,)
        )[0][0]

        try:
            location = parameters["locationinput"][0]
            occupant = parameters["occupancyinput"][0]
            type = parameters["typeinput"][0]
            type_dict = {
                "car": 0,
                "van": 1,
                "truck": 2,
                "taxi": 3,
                "other": 4,
                "motorbike": 5,
                "bicycle": 6,
                "bus": 7,
            }

        except KeyError:
            response.append(
                build_response_refill("message", "missing location try again")
            )
            return [user, magic, response]
        location = location.strip()
        check = access_database_with_result(
            "traffic.db",
            "select * from traffic where sessionid=@0 and type=@1 and occupancy=@2 and location=@3 and mode=1",
            (session_id, type_dict[type], occupant, location),
        )
        if len(check) > 0 and check_punc(location) == False:
            record_id = check[-1][0]
            access_database(
                "traffic.db",
                "update traffic set mode=2 where recordid=@0",
                (record_id,),
            )
            time_now = get_unix_now()
            count = len(
                access_database_with_result("traffic.db", "select * from traffic")
            )
            access_database(
                "traffic.db",
                "insert into traffic values(@0,@1,@2,@3,@4,@5,0)",
                (count + 1, session_id, time_now, type_dict[type], occupant, location),
            )
            response.append(build_response_refill("message", "Entry Un-done."))
            count_1 = len(
                access_database_with_result(
                    "traffic.db",
                    "select * from traffic where mode=1 AND sessionid=@0",
                    (session_id,),
                )
            )
            response.append(build_response_refill("total", str(count_1)))
        elif check_punc(location) == False:
            response.append(build_response_refill("message", "Input not existing"))
        else:
            response.append(build_response_refill("message", "Invalid input"))

    return [user, magic, response]


def handle_back_request(iuser, imagic, parameters):
    """This code handles the selection of the back button on the record form (page.html)
    You will only need to modify this code if you make changes elsewhere that break its behaviour"""
    user = iuser
    magic = imagic
    check = access_database_with_result(
        "traffic.db",
        "select * from session where userid=@0 and magic=@1 and end != 0",
        (iuser, imagic),
    )
    response = []
    ## alter as required
    if handle_validate(iuser, imagic) != True:
        response.append(build_response_redirect("/index.html"))

    elif len(check) > 0:
        response.append(build_response_redirect("/index.html"))
        response.append(build_response_refill("message", "Session already ended"))
    else:
        response.append(build_response_redirect("/summary.html"))
    return [user, magic, response]


def handle_logout_request(iuser, imagic, parameters):
    """This code handles the selection of the logout button on the summary page (summary.html)
    You will need to ensure the end of the session is recorded in the database
    And that the session magic is revoked."""

    response = []
    ## alter as required
    time_logout = get_unix_now()
    access_database(
        "traffic.db", "update session set end=@0 where magic=@1", (time_logout, imagic)
    )
    response.append(build_response_redirect("/index.html"))
    user = "!"
    magic = ""
    return [user, magic, response]


def handle_summary_request(iuser, imagic, parameters):
    """This code handles a request for an update to the session summary values.
    You will need to extract this information from the database.
    You must return a value for all vehicle types, even when it's zero."""
    user = ""
    magic = ""
    response = []
    ## alter as required
    if handle_validate(iuser, imagic) != True:
        response.append(build_response_redirect("/index.html"))
    else:
        session_id = access_database_with_result(
            "traffic.db", "select sessionid from session where magic=@0", (imagic,)
        )[0][0]
        car = access_database_with_result(
            "traffic.db",
            "SELECT COUNT(recordid) FROM traffic WHERE sessionid =@0 AND type = '0' AND mode = 1 ",
            (session_id,),
        )
        taxi = access_database_with_result(
            "traffic.db",
            "SELECT COUNT(recordid) FROM traffic WHERE sessionid =@0 AND type = '3' AND mode = 1 ",
            (session_id,),
        )
        bus = access_database_with_result(
            "traffic.db",
            "SELECT COUNT(recordid) FROM traffic WHERE sessionid =@0 AND type = '7' AND mode = 1 ",
            (session_id,),
        )
        motorbike = access_database_with_result(
            "traffic.db",
            "SELECT COUNT(recordid) FROM traffic WHERE sessionid =@0 AND type = '5' AND mode = 1 ",
            (session_id,),
        )
        bicycle = access_database_with_result(
            "traffic.db",
            "SELECT COUNT(recordid) FROM traffic WHERE sessionid =@0 AND type = '6' AND mode = 1 ",
            (session_id,),
        )
        van = access_database_with_result(
            "traffic.db",
            "SELECT COUNT(recordid) FROM traffic WHERE sessionid =@0 AND type = '1' AND mode = 1 ",
            (session_id,),
        )
        truck = access_database_with_result(
            "traffic.db",
            "SELECT COUNT(recordid) FROM traffic WHERE sessionid =@0 AND type = '2' AND mode = 1 ",
            (session_id,),
        )
        other = access_database_with_result(
            "traffic.db",
            "SELECT COUNT(recordid) FROM traffic WHERE sessionid =@0 AND type = '4' AND mode = 1 ",
            (session_id,),
        )

        count_car = car[0][0]
        count_taxi = taxi[0][0]
        count_bus = bus[0][0]
        count_motorbike = motorbike[0][0]
        count_bicycle = bicycle[0][0]
        count_van = van[0][0]
        count_truck = truck[0][0]
        count_other = other[0][0]
        count_total = (
            count_car
            + count_taxi
            + count_bus
            + count_motorbike
            + count_bicycle
            + count_van
            + count_truck
            + count_other
        )

        response.append(build_response_refill("sum_car", count_car))
        response.append(build_response_refill("sum_taxi", count_taxi))
        response.append(build_response_refill("sum_bus", count_bus))
        response.append(build_response_refill("sum_motorbike", count_motorbike))
        response.append(build_response_refill("sum_bicycle", count_bicycle))
        response.append(build_response_refill("sum_van", count_van))
        response.append(build_response_refill("sum_truck", count_truck))
        response.append(build_response_refill("sum_other", count_other))
        response.append(build_response_refill("total", count_total))
    return [user, magic, response]


def cal_hour(start, end, start_midnight):
    start_datetime = format_datetime(start)
    end_datetime = format_datetime(end)
    start_midnight_datetime = format_datetime(start_midnight)
    if start_datetime <= start_midnight_datetime:
        diff_hours = ((end_datetime - start_midnight_datetime).total_seconds()) / 3600
    else:
        diff_hours = ((end_datetime - start_datetime).total_seconds()) / 3600

    return diff_hours


# HTTPRequestHandler class
class myHTTPServer_RequestHandler(BaseHTTPRequestHandler):

    # GET This function responds to GET requests to the web server.
    def do_GET(self):

        # The set_cookies function adds/updates two cookies returned with a webpage.
        # These identify the user who is logged in. The first parameter identifies the user
        # and the second should be used to verify the login session.
        def set_cookies(x, user, magic):
            ucookie = Cookie.SimpleCookie()
            ucookie["u_cookie"] = user
            x.send_header("Set-Cookie", ucookie.output(header="", sep=""))
            mcookie = Cookie.SimpleCookie()
            mcookie["m_cookie"] = magic
            x.send_header("Set-Cookie", mcookie.output(header="", sep=""))

        # The get_cookies function returns the values of the user and magic cookies if they exist
        # it returns empty strings if they do not.
        def get_cookies(source):
            rcookies = Cookie.SimpleCookie(source.headers.get("Cookie"))
            user = ""
            magic = ""
            for keyc, valuec in rcookies.items():
                if keyc == "u_cookie":
                    user = valuec.value
                if keyc == "m_cookie":
                    magic = valuec.value
            return [user, magic]

        # Fetch the cookies that arrived with the GET request
        # The identify the user session.
        user_magic = get_cookies(self)

        print(user_magic)

        # Parse the GET request to identify the file requested and the parameters
        parsed_path = urllib.parse.urlparse(self.path)

        # Decided what to do based on the file requested.

        # Return a CSS (Cascading Style Sheet) file.
        # These tell the web client how the page should appear.
        if self.path.startswith("/css"):
            self.send_response(200)
            self.send_header("Content-type", "text/css")
            self.end_headers()
            with open("." + self.path, "rb") as file:
                self.wfile.write(file.read())
            file.close()

        # Return a Javascript file.
        # These tell contain code that the web client can execute.
        elif self.path.startswith("/js"):
            self.send_response(200)
            self.send_header("Content-type", "text/js")
            self.end_headers()
            with open("." + self.path, "rb") as file:
                self.wfile.write(file.read())
            file.close()

        # A special case of '/' means return the index.html (homepage)
        # of a website
        elif parsed_path.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("./index.html", "rb") as file:
                self.wfile.write(file.read())
            file.close()

        # Return html pages.
        elif parsed_path.path.endswith(".html"):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("." + parsed_path.path, "rb") as file:
                self.wfile.write(file.read())
            file.close()

        # The special file 'action' is not a real file, it indicates an action
        # we wish the server to execute.
        elif parsed_path.path == "/action":
            self.send_response(200)  # respond that this is a valid page request
            # extract the parameters from the GET request.
            # These are passed to the handlers.
            parameters = urllib.parse.parse_qs(parsed_path.query)

            if "command" in parameters:
                # check if one of the parameters was 'command'
                # If it is, identify which command and call the appropriate handler function.
                if parameters["command"][0] == "login":
                    [user, magic, response] = handle_login_request(
                        user_magic[0], user_magic[1], parameters
                    )
                    # The result of a login attempt will be to set the cookies to identify the session.
                    set_cookies(self, user, magic)
                elif parameters["command"][0] == "add":
                    [user, magic, response] = handle_add_request(
                        user_magic[0], user_magic[1], parameters
                    )
                    if (
                        user == "!"
                    ):  # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, "", "")
                elif parameters["command"][0] == "undo":
                    [user, magic, response] = handle_undo_request(
                        user_magic[0], user_magic[1], parameters
                    )
                    if (
                        user == "!"
                    ):  # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, "", "")
                elif parameters["command"][0] == "back":
                    [user, magic, response] = handle_back_request(
                        user_magic[0], user_magic[1], parameters
                    )
                    if (
                        user == "!"
                    ):  # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, "", "")
                elif parameters["command"][0] == "summary":
                    [user, magic, response] = handle_summary_request(
                        user_magic[0], user_magic[1], parameters
                    )
                    if (
                        user == "!"
                    ):  # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, "", "")
                elif parameters["command"][0] == "logout":
                    [user, magic, response] = handle_logout_request(
                        user_magic[0], user_magic[1], parameters
                    )
                    if (
                        user == "!"
                    ):  # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, "", "")
                else:
                    # The command was not recognised, report that to the user.
                    response = []
                    response.append(
                        build_response_refill(
                            "message", "Internal Error: Command not recognised."
                        )
                    )

            else:
                # There was no command present, report that to the user.
                response = []
                response.append(
                    build_response_refill(
                        "message", "Internal Error: Command not found."
                    )
                )

            text = json.dumps(response)
            print(text)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(text, "utf-8"))

        elif self.path.endswith("/statistics/hours.csv"):
            ## if we get here, the user is looking for a statistics file
            ## this is where requests for /statistics/hours.csv should be handled.
            ## you should check a valid user is logged in. You are encouraged to wrap this behavour in a function.
            response = []
            iuser = user_magic[0]
            imagic = user_magic[1]
            check = 0
            text = "Username,Day,Week,Month\n"
            if handle_validate(iuser, imagic) != True:
                # response.append(build_response_redirect('/index.html'))
                self.send_response(404)
                self.end_headers()
            else:
                start_date = get_unix_start_date()
                end_date = get_unix_end_date()

                if start_date != 0 and end_date != 0:
                    check = access_database_with_result(
                        "traffic.db",
                        "select * from session WHERE end != 0 and end between @0 and @1",
                        (start_date, end_date),
                    )
                dict_user = {
                    1: "test1",
                    2: "test2",
                    3: "test3",
                    4: "test4",
                    5: "test5",
                    6: "test6",
                    7: "test7",
                    8: "test8",
                    9: "test9",
                    10: "test10",
                }
                dict_total = {
                    1: {"day": 0, "week": 0, "month": 0},
                    2: {"day": 0, "week": 0, "month": 0},
                    3: {"day": 0, "week": 0, "month": 0},
                    4: {"day": 0, "week": 0, "month": 0},
                    5: {"day": 0, "week": 0, "month": 0},
                    6: {"day": 0, "week": 0, "month": 0},
                    7: {"day": 0, "week": 0, "month": 0},
                    8: {"day": 0, "week": 0, "month": 0},
                    9: {"day": 0, "week": 0, "month": 0},
                    10: {"day": 0, "week": 0, "month": 0},
                }

                if check != 0:
                    for i in check:
                        userid = i[1]
                        total_hour_d = dict_total[userid]["day"]
                        start_record = i[3]
                        end_recod = i[4]
                        dict_total[userid]["day"] = total_hour_d + cal_hour(
                            start_record, end_recod, start_date
                        )

                    start_week = get_unix_start_week()
                    end_week = get_unix_end_week()
                    check = access_database_with_result(
                        "traffic.db",
                        "select * from session WHERE end !=0 and end between @0 and @1",
                        (start_week, end_week),
                    )

                    for i in check:
                        userid = i[1]
                        total_hour_d = dict_total[userid]["week"]
                        start_record = i[3]
                        end_recod = i[4]
                        dict_total[userid]["week"] = total_hour_d + cal_hour(
                            start_record, end_recod, start_week
                        )

                    #### month
                    start_month = get_unix_start_month()
                    end_month = get_unix_end_month()
                    check = access_database_with_result(
                        "traffic.db",
                        "select * from session WHERE end !=0 and end between @0 and @1",
                        (start_month, end_month),
                    )

                    for i in check:
                        userid = i[1]
                        total_hour_d = dict_total[userid]["month"]
                        start_record = i[3]
                        end_recod = i[4]
                        dict_total[userid]["month"] = total_hour_d + cal_hour(
                            start_record, end_recod, start_month
                        )

                    for i in range(len(dict_total)):
                        dict_total[i + 1]["day"] = round(dict_total[i + 1]["day"], 1)
                        dict_total[i + 1]["week"] = round(dict_total[i + 1]["week"], 1)
                        dict_total[i + 1]["month"] = round(
                            dict_total[i + 1]["month"], 1
                        )

                for i in range(len(dict_total)):
                    text += "{},{},{},{}\n".format(
                        dict_user[i + 1],
                        dict_total[i + 1]["day"],
                        dict_total[i + 1]["week"],
                        dict_total[i + 1]["month"],
                    )

                encoded = bytes(text, "utf-8")
                self.send_response(200)
                self.send_header("Content-type", "text/csv")
                self.send_header(
                    "Content-Disposition",
                    'attachment; filename="{}"'.format("hours.csv"),
                )
                self.send_header("Content-Length", len(encoded))
                self.end_headers()
                self.wfile.write(encoded)

        elif self.path.endswith("/statistics/traffic.csv"):
            ## if we get here, the user is looking for a statistics file
            ## this is where requests for  /statistics/traffic.csv should be handled.
            ## you should check a valid user is checked in. You are encouraged to wrap this behavour in a function.
            response = []
            iuser = user_magic[0]
            imagic = user_magic[1]
            if handle_validate(iuser, imagic) != True:
                # response.append(build_response_redirect('/index.html'))
                self.send_response(404)
                self.end_headers()
                # return [iuser,imagic,response]
            else:
                text = "This should be the content of the csv file."
                text = "Location,Type,Occupancy1,Occupancy2,Occupancy3,Occupancy4\n"
                start = get_unix_time_traffic()[0]
                end = get_unix_time_traffic()[1]

                if start != 0 and end != 0:
                    prepare_dist_3 = access_database_with_result(
                        "traffic.db",
                        "SELECT DISTINCT location, type, occupancy, count(*) from traffic WHERE mode=1 and time between @0 and @1 GROUP by location, type, occupancy",
                        (start, end),
                    )
                    prepare_dist_2 = access_database_with_result(
                        "traffic.db",
                        "SELECT DISTINCT location, type from traffic WHERE mode=1 and time between @0 and @1",
                        (start, end),
                    )

                    row = []
                    for i in prepare_dist_2:
                        if i[0:2] not in row:
                            my_list = list(i[0:2])
                            row.append(my_list)
                    for j in row:
                        for k in range(4):
                            j.append(0)
                            k += 1
                    index_occ_type = 2
                    index_occ_num = 3
                    for i in row:
                        location = i[0]
                        type = i[1]
                        for j in prepare_dist_3:
                            if location == j[0] and type == j[1]:
                                i[j[index_occ_type] + 1] = j[index_occ_num]
                    for i in row:
                        dict_type = {
                            0: "car",
                            1: "van",
                            2: "truck",
                            3: "taxi",
                            4: "other",
                            5: "motorbike",
                            6: "bicycle",
                            7: "bus",
                        }
                        text += "{},{},{},{},{},{}\n".format(
                            i[0], dict_type[i[1]], i[2], i[3], i[4], i[5]
                        )
                encoded = bytes(text, "utf-8")
                self.send_response(200)
                self.send_header("Content-type", "text/csv")
                self.send_header(
                    "Content-Disposition",
                    'attachment; filename="{}"'.format("traffic.csv"),
                )
                self.send_header("Content-Length", len(encoded))
                self.end_headers()
                self.wfile.write(encoded)
        else:
            # A file that does n't fit one of the patterns above was requested.
            self.send_response(404)
            self.end_headers()
        return


def run():
    """This is the entry point function to this code."""
    print("starting server...")
    ## You can add any extra start up code here
    # Server settings
    # Choose port 8081 over port 80, which is normally used for a http server
    if len(sys.argv) < 2:  # Check we were given both the script name and a port number
        print("Port argument not provided.")
        return
    server_address = ("127.0.0.1", int(sys.argv[1]))
    httpd = HTTPServer(server_address, myHTTPServer_RequestHandler)
    print("running server on port =", sys.argv[1], "...")
    httpd.serve_forever()  # This function will not return till the server is aborted.


run()
