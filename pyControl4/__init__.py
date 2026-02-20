from __future__ import annotations

from pyControl4.director import C4Director


class C4Entity:
    def __init__(self, director: C4Director, item_id: int):
        """Creates a Control4 object.

        Parameters:
            `director` - A `pyControl4.director.C4Director` object that corresponds
                to the Control4 Director that the device is connected to.

            `item_id` - The Control4 item ID.
        """
        self.director = director
        self.item_id = int(item_id)
