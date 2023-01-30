#Program reads a csv file; parses text; and displays formatted information to user.

#Given constraints:
#1. Phone number must be in the form 999-999-9999
#2. ID must be two letters followed by 4 digits

#Given assumptions:
#1. ID and phone number data might not adhere to correct standards
#2. Middle initials might not be present
#3. Last name, first name, and middle initial might not follow capitalized form


import sys
import re
import pickle

#define a Person class to hold parsed information
class Person:
    def __init__(self, last, first, mi, id, phone):
        self.last = last
        self.first = first
        self.mi = mi
        self.id = id
        self.phone = phone

    #Method to display each employee's information
    def display(self):
        print(f'Employee id: {self.id}')
        print(f'Employee Name: {self.first} {self.mi} {self.last}')
        print(f'Employee Phone: {self.phone}')


def processFile(fName):
    
    #Set regex patterns to check for invalid id and phone number
    pattern_id = re.compile('[A-Z]{2}\d{4}')
    pattern_phone = re.compile('\d{3}-\d{3}-\d{4}')

    #Initialize dictionary to store employees' information
    person_dictionary = dict()

    print("Opening and reading file....\n")

    #Open file for reading data
    with open(fName, 'r') as f:

        #Remove new line characters and store each line inside an array
        lines = f.read().splitlines()
        
        #Skip the header line and iterate through employee data
        for line in lines[1:]:

            #Parse information, unpack data, and store them in variables
            p_last, p_first, p_mi, p_id, p_phone = line.split(',')
            
            #Capitalize last and first name
            p_last, p_first = p_last.capitalize(), p_first.capitalize()

            #Set middle initial to X if no middle initial; otherwise, set middle initial to capitalized version
            p_mi = 'X' if (not p_mi) else p_mi.capitalize()

            #Keep prompting user to enter valid id if program detects invalid id
            while not re.fullmatch(pattern_id, p_id):
                print(f'ID invalid: {p_id}')
                print('ID is two letters followed by 4 digits')
                p_id = input('Please enter a valid ID: ')

            #Keep prompting user to enter valid phone number if program detects invalid phone number
            while not re.fullmatch(pattern_phone, p_phone):
                print(f'Phone {p_phone} is invalid')
                print('Phone number follows the form 123-456-7890')
                p_phone = input('Please enter a valid phone number: ')

            #Exit program if there are duplicate ID keys in dictionary
            if p_id in person_dictionary:
                print(f'Error: ID {p_id} already exists in dictionary')
                exit()

            #Store employees' information and ID keys in the dictionary 
            person_dictionary[p_id] = Person(p_last, p_first, p_mi, p_id, p_phone)
        
        return person_dictionary

def main():

    #Set initial file name
    fileName = ''

    #Check if user provided a file path argument; otherwise, print error message and exit
    if len(sys.argv) > 1:
        fileName = sys.argv[1]
    else:
        print('Error: No argument provided')
        exit()
    
    #Save employees' information in a dictionary
    person_dictionary = processFile(fileName)

    #Save dictionary to pickle file
    print("\nSaved person_dictionary as pickle file\n")
    pickle.dump(person_dictionary, open('person_dictionary.p', 'wb'))

    #Load pickle file
    print("Loaded pickle file\n")
    input_dictionary = pickle.load(open('person_dictionary.p', 'rb'))
    
    #Display employee list; iterate through dictionary and call the display method
    print("Employee list:")

    for person in person_dictionary:
        print("\n")
        person_dictionary[person].display()
    

if __name__ == '__main__':
    main()