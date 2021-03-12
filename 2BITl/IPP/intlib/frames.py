"""
Name: frames.py
Main file: interpret.py
Caption:  Handles the frames of IPPcode20
Author: Magdaléna Ondrušková <xondru16@stud.fit.vutbr.cz>
Date: 29.03.2020
"""
from intlib.error import *


class Frames:
    def __init__(self):
        self.local_frame = None
        self.temporary_frame = None
        self.global_frame = []
        self.stack_frame = []

    def add_to_GF(self, variable):
        """
        Function adds variable to Global Frame
        Firstly, checks if the variable is not already defined in Global Frame
        Success = False  - variable doesn't exist in Global Frame so var can be added into Global Frame
        :param variable: variable to be added into Global Frame
        """
        success, var = self.get_from_GF(variable.name)
        if success is False:
            self.global_frame.append(variable)
        else:
            raise ERRSemantic("Trying to add already existing variable in global frame. ")

    def add_to_TF(self, variable):
        """
        Function adds variable to Temporary Frame
        Firstly, checks if the variable is not already defined in Temporary Frame
        Success = False  - variable doesn't exist in Temporary Frame so var can be added into Temporary Frame
        :param variable: variable to be added into Temporary Frame
        """
        if self.temporary_frame is None:
            raise ERRNotExistFrame("Trying to add variable to not-existing temporary frame.")
        success, var = self.get_from_TF(variable.name)
        if success is False:
            self.temporary_frame.append(variable)
        else:
            raise ERRSemantic("Variable {} already exists in temporary frame.".format(variable.name))

    def add_to_LF(self, variable):
        """
        Function adds variable to Local Frame
        Firstly, checks if the variable is not already defined in Local Frame
        Success = False  - variable doesn't exist in Local Frame so var can be added into Local Frame
        :param variable: variable to be added into Local Frame
        """
        if self.local_frame is None:
            raise ERRNotExistFrame("Trying to add variable to not-existing local frame.")
        success, var = self.get_from_LF(variable.name)
        if success is False:
            self.local_frame.append(variable)
        else:
            raise ERRSemantic("Variable {} already exists in local frame.".format(variable.name))

    def get_from_GF(self, name):
        """
        Function finds variable in Global Frame.
        :param name: Name of variable that I'm looking for
        :return: If var already exists in Global Frame, function returns True and existing var,
                    else function returns False and the name of variable
        """
        for var in self.global_frame:
            if var.name == name:
                return True, var
        return False, name

    def get_from_TF(self, name):
        """
        Function finds variable in Temporary Frame.
        :param name: Name of variable that I'm looking for
        :return: If var already exists in Temporary Frame, function returns True and existing var,
                    else function returns False and the name of variable
        """
        if self.temporary_frame is None:
            raise ERRNotExistFrame("Trying to get variable from not-existing temporary frame.")
        for var in self.temporary_frame:
            if var.name == name:
                return True, var
        return False, name

    def get_from_LF(self, name):
        """
        Function finds variable in Local Frame.
        :param name: Name of variable that I'm looking for
        :return: If var already exists in Local Frame, function returns True and existing var,
                    else function returns False and the name of variable
        """
        if self.local_frame is None:
            raise ERRNotExistFrame("Trying to get variable from not-existing local frame.")
        for var in self.local_frame:
            if var.name == name:
                return True, var
        return False, name

    def push_frame(self):
        """
        Function push frame to the frame stack
        """
        if self.temporary_frame is None:
            raise ERRNotExistFrame("Frame doesn't exist!")
        else:
            self.stack_frame.append(self.temporary_frame)
            self.local_frame = self.temporary_frame
            self.temporary_frame = None

    def pop_frame(self):
        """
        Function pop frame from frame stack
        """
        if len(self.stack_frame) < 1:
            raise ERRNotExistFrame("Local frame doesnt exist on frame stack - it's empty.")
        else:
            self.temporary_frame = self.stack_frame.pop()
            try:
                self.local_frame = self.stack_frame[-1]
            except IndexError:
                self.local_frame = None
