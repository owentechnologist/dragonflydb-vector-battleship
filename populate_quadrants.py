import random
import sys
import os
import struct
import uuid
from vector_battleship_create import make_ship_shape_from_anchorXY
from private_stuff import get_redis, get_table_config, close_pool


class Populator:
    def __init__(self, number_of_objects, number_of_quadrants):
        self.ship_types = ['submarine', 'destroyer', 'aircraft_carrier', 'skiff', 'flotsam']
        self.num_of_quadrants = number_of_quadrants
        self.number_of_objects = number_of_objects
        self.battleship_table = os.getenv('BATTLESHIP_TABLE', 'vb.battleship')

    def insert_vectorized_object(self, ship_type, quadrant, anchor_x, anchor_y):
        print(f"\nAttempting to place a '{ship_type}' in quadrant {quadrant} at anchor ({anchor_x}, {anchor_y})")
        r = get_redis()
        config = get_table_config(self.battleship_table)

        vector = make_ship_shape_from_anchorXY(anchor_x, anchor_y, ship_type)
        vec_bytes = struct.pack(f'{len(vector)}f', *[float(v) for v in vector])
        ship_id = str(uuid.uuid4())

        r.hset(f"{config['prefix']}{ship_id}", mapping={
            'battleship_class': ship_type,
            'quadrant': quadrant,
            'anchorpoint': anchor_x + ((anchor_y * 10) - 10),
            'embedding': vec_bytes,
        })

        meta_key = f"meta:{config['index_name']}:max_quadrant"
        current_max = r.get(meta_key)
        if not current_max or quadrant > int(current_max):
            r.set(meta_key, quadrant)

    def run(self):
        print(f'^^^^ POPULATING {self.battleship_table} WITH {self.number_of_objects} OBJECTS ACROSS {self.num_of_quadrants} QUADRANTS ^^^^^')
        current_quadrant = random.randint(1, self.num_of_quadrants)
        for pop_counter in range(1, self.number_of_objects + 1):
            quadrant = (current_quadrant % self.num_of_quadrants) + 1
            current_quadrant += 1
            ship_type = self.ship_types[pop_counter % 5]
            if ship_type == 'flotsam':
                anchor_x, anchor_y = 1, 1
            elif ship_type == 'skiff':
                anchor_x, anchor_y = random.randint(1, 10), random.randint(1, 7)
            elif ship_type == 'destroyer':
                anchor_x, anchor_y = random.randint(2, 9), random.randint(1, 4)
            elif ship_type == 'aircraft_carrier':
                anchor_x, anchor_y = random.randint(1, 2), random.randint(1, 7)
            else:  # submarine
                anchor_x, anchor_y = random.randint(1, 10), random.randint(1, 5)
            self.insert_vectorized_object(ship_type, quadrant, anchor_x, anchor_y)


if __name__ == '__main__':
    pop = Populator(int(sys.argv[1]), int(sys.argv[2]))
    pop.run()
    close_pool()
