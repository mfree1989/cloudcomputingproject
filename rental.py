from os import remove
import Pyro5
from Pyro5 import *
from Pyro5.api import *
import datetime
# import * means import everything


@expose
@Pyro5.server.expose
@behavior(instance_mode="single")
class rental(object):
    def __init__(self):
        self.users = {}
        self.manufacturer = {}
        self.rental_car = {}
        self.not_rented_cars = []
        self.rented_cars = []
        self.users_cars_out = {}
        self.user_history = {}

# task 1: adds a user to the system
    @Pyro5.server.expose
    def add_user(self, user_name, user_number):
        if user_name not in self.users.keys():
            self.users[user_name] = user_number
            self.users_cars_out[user_name] = []
            # using dictionaries to store user inputs, we use the [] to tell  python it's going to be stored in the dictionary
            # this function is used to add a new user to the list in the empty dictionary in self.users; [] is the 'method' that adds the value of the user name and number to the dictionary

# task 2: displays the inputed added user data
    @Pyro5.server.expose
    def return_users(self):
        user_data = []
        for key, value in self.users.items():
            user_data.append((key, value))
        return user_data
        # in order to display information stored in the self.users dictionary, we are appending the information into a 'mini list' so that it can be returned as user data

# task 3: adds a car manufacturer to the system and checks if it exists, if it doesn't exists it's added to the dictionary to be displayed in task 4
    @Pyro5.server.expose
    def add_manufacturer(self, manufacturer_name, manufacturer_country):
        if manufacturer_name not in self.manufacturer.keys():
            self.manufacturer[manufacturer_name] = manufacturer_country

# task 4: returns all associated pieces of information relating to the set of manufacturers
    @Pyro5.server.expose
    def return_manufacturers(self):
        name_country = []
        for key, vlaue in self.manufacturer.items():
            name_country.append((key, vlaue))
        return name_country

# task 5: add a new rental car to the system
    @Pyro5.server.expose
    def add_rental_car(self, manufacturer_name, car_model):
        if car_model not in self.rental_car.keys():
            self.rental_car[car_model] = manufacturer_name
        self.not_rented_cars.append(car_model)

# task 6: displays not rented cars by turning the information sotred in the dictionary rental_cars into a list which is defined as car_data
    @Pyro5.server.expose
    def return_cars_not_rented(self):
        car_data = []
        for car in self.not_rented_cars:
            car_data.append((car, self.rental_car[car]))
        return car_data
        # car = the name of the car added in list of not_rented_cars
        # self.rental_car = the manufactuer name
        # [car] = we are telling the dictionary we want a specific car to be appended to the car_data variable

# task 7: rents only one of a specific car model, to a specific user, on a specific date etc.
    @Pyro5.server.expose
    def rent_car(self, user_name, car_model, year, month, day):
        if (car_model) not in self.not_rented_cars:
            return 0
        else:
            self.not_rented_cars.remove(car_model)
            self.rented_cars.append(car_model)
            if user_name not in self.user_history.keys():
                self.user_history[user_name] = []
            self.user_history[user_name].append(
                [car_model, 0, datetime.datetime(year, month, day), ""])
            # 3d dictionary
            # this statement calls the user and adds to the list the model and the datetime they rented it
            self.users_cars_out[user_name].append(car_model)
            # dictionary of users and list of the cars they have out (since users can rent many cars, it will show all the cars the user has out)
            # (user-name) tells the dictionary who to call
            # .append(car_model) tells the list we got from the dicionary who to attach the car model to
            return 1

# task 8: returns information about cars currently rented
    @Pyro5.server.expose
    def return_cars_rented(self):
        car_data = []
        for car in self.rented_cars:
            car_data.append((car, self.rental_car[car]))
        return car_data

# task 9: returns rented car and ammends to user's rental history
    @Pyro5.server.expose
    def end_rental(self, user_name, car_model, year, month, day):
        if car_model not in self.users_cars_out[user_name]:
            return
        self.users_cars_out[user_name].remove(car_model)
        self.not_rented_cars.append(car_model)
        self.rented_cars.remove(car_model)
        for history in self.user_history[user_name]:
            if history[0] == car_model and history[1] == 0:
                history[1] = 1
                history[3] = datetime.datetime(year, month, day)

# task 10: removes all cars not rented
    @Pyro5.server.expose
    def delete_car(self, car_model):
        for car in self.not_rented_cars:
            if car == car_model:
                self.not_rented_cars.remove(car)

# task 11: deletes a specified user from the system
    @Pyro5.server.expose
    def delete_user(self, user_name):
        if user_name in self.user_history.keys():
            # if the user is in the user history dictionary, we don't want to remove them!
            return
        self.users.pop(user_name)
        # BUTTTTT if they're not in the user history POP IT OUT
        self.users_cars_out.pop(user_name)

# task 12: returns all car modules rented previously by a user where the corresponding rental and return dates both lie between a specified start and end date
    @Pyro5.server.expose
    def user_rental_date(self, user_name, start_year, start_month, start_day, end_year, end_month, end_day):
        StartTime = datetime.datetime(start_year, start_month, start_day)
        rented_cars = []
        EndTime = datetime.datetime(end_year, end_month, end_day)
        for history in self.user_history[user_name]:
            if history[1] == 1 and history[2] > StartTime and history[3] < EndTime:

                rented_cars.append(history[0])
        return rented_cars


daemon = Daemon()
serve({rental: "example.rental"}, daemon=daemon, use_ns=True)
