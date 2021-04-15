class Validation:
    """
    Methods: set_params, check_desc, check_mode, check_group, check_payment_mode, check_all_input, check_routes
    Attributes: config, b1_desc, b2_desc, mode, group, payment_mode
    """

    def __init__(self, config):
        self.config = config
        self.b1_desc = None
        self.b2_desc = None
        self.mode = None
        self.group = None
        self.payment_mode = None

    def set_params(self, entry_dict):
        """
        :param entry_dict: input is a dictionaries containing required inputs
        :return: sets the values of the attributes based on the input
        """
        self.b1_desc = entry_dict.get("start", None)
        self.b2_desc = entry_dict.get("end", None)
        self.mode = entry_dict.get("mode", None)
        self.group = entry_dict.get("group", None)
        self.payment_mode = entry_dict.get("payment_mode", None)

    def check_desc(self):
        """
        :return: checks if either the description of bus stop 1 or 2 is a NoneType
        """
        if self.b1_desc or self.b2_desc is None:
            return "Please choose another bus stop."
        return None

    def check_mode(self):
        """
        :return: checks if mode is a NoneType and whether mode satisfies the presets
        """
        if self.mode is None:
            return "Please indicate whether you wish to sort the result by distance or fare."
        else:
            if self.mode.lower() not in self.config.MODE:
                return "Please enter a valid mode to sort by."
        return None

    def check_group(self):
        """
        :return: checks if group is a NoneType and whether group satisfies the presets
        """
        if self.group is None:
            return "Please enter the payment group which you belong to."
        else:
            if self.group not in self.config.GROUP:
                return "PLease enter a valid payment group."
        return None

    def check_payment_mode(self):
        """
        :return: checks if payment_mode is a NoneType and whether payment_mode satisfies the presets
        """
        if self.payment_mode is None:
            return "Please enter your mode of payment."
        else:
            if self.payment_mode not in self.config.PAYMENT_MODE:
                return "Please enter a valid mode of payment."
        return None

    def check_all_input(self):
        """
        :return: runs check on description, mode, group and payment_mode and returns the result
        """
        temp = (
            self.check_desc(),
            self.check_mode(),
            self.check_group(),
            self.check_payment_mode()
        )
        if temp != (None,)*4:
            passed = True
        else:
            passed = False
        return temp, passed

    @staticmethod
    def check_routes(bus_routes, b1, b2):
        """
        :param bus_routes: a string indicating the bus route
        :param b1: description of bus stop 1
        :param b2: description of bus stop 2
        :return: returns an error message and the test result
        """
        passed = True
        if len(bus_routes) == 0:
            err_msg = f"No direct bus between {b1} and {b2}."
            passed = False
            return err_msg, passed
        return None, passed
