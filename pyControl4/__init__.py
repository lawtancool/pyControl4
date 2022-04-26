class C4Entity:
    def __init__(self, C4Director, item_id):
        """Creates a Control4 object.

        Parameters:
            `C4Director` - A `pyControl4.director.C4Director` object that corresponds to the Control4 Director that the device is connected to.

            `item_id` - The Control4 item ID.
        """
        self.director = C4Director
        self.item_id = int(item_id)
