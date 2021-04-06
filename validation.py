class Validation:

    def __init__(self, config):
        self.config = config
        self.b1_desc = None
        self.b2_desc = None
        self.mode = None
        self.group = None
        self.payment_mode = None

    def set_params(self, entry_dict):
        self.b1_desc = entry_dict["start"]
        self.b2_desc = entry_dict["end"]
        self.mode = entry_dict["mode"]
        self.group = entry_dict["group"]
        self.payment_mode = entry_dict["payment_mode"]

    def check_desc(self):
        if self.b1_desc or self.b2_desc is None:
            return "Please choose another bus stop."
        return None

    def check_mode(self):
        if self.mode is None:
            return "Please indicate whether you wish to sort the result by distance or fare."
        else:
            if self.mode.lower() not in self.config.MODE:
                return "Please enter a valid mode to sort by."
        return None

    def check_group(self):
        if self.group is None:
            return "Please enter the payment group which you belong to."
        else:
            if self.group not in self.config.GROUP:
                return "PLease enter a valid payment group."
        return None

    def check_payment_mode(self):
        if self.payment_mode is None:
            return "Please enter your mode of payment."
        else:
            if self.payment_mode not in self.config.PAYMENT_MODE:
                return "Please enter a valid mode of payment."
        return None

    def check_all_input(self):
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
        passed = True
        if len(bus_routes) == 0:
            err_msg = f"No direct bus between {b1} and {b2}."
            passed = False
            return err_msg, passed
        return None, passed
