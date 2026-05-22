import os, sys
from vector_battleship_create import make_ship_shape_from_anchorXY
from populate_quadrants import Populator
from private_stuff import ensure_indices,vector_search, destroy_ship, close_pool

# invoke this program like this:
# python human_player.py <match_percentage_threshold> <max_attempts>
# python human_player.py 55 20

class HumanPlayer:
    def __init__(self, match_percentage_threshold, max_attempts):
        self.ship_types = ['submarine', 'destroyer', 'aircraft_carrier', 'skiff']
        self.quadrants = [1, 2, 3, 4]
        self.match_percentage_threshold = match_percentage_threshold
        self.max_attempts = max_attempts
        self.battleship_table = os.getenv('BATTLESHIP_TABLE', 'vb.battleship')

    def run(self):
        print('\n ******* BEGINNING PLAYER TARGETING ATTEMPTS ********\n')
        attempt_counter=1
        while attempt_counter<=self.max_attempts:
            usr_input=''
            while usr_input=='':
                usr_input=input('enter a number between 1 and 4 for the quadrant ')
                if usr_input=='end':
                    close_pool()
                    sys.exit(0)
                quadrant=int(usr_input)
            ship_type_num=''
            while ship_type_num=='':
                ship_type_num=input('Enter a number corresponding to a ship type: 1 (destroyer) 2 (skiff) 3 (submarine) 4 (aircraft_carrier)  ')
                if ship_type_num=='end':
                    sys.exit(0)
            if ship_type_num=='1':
                ship_type='destroyer'
            elif ship_type_num=='2':
                ship_type='skiff'
            elif ship_type_num=='3':
                ship_type='submarine'
            elif ship_type_num=='4':
                ship_type='aircraft_carrier'
            anchor_y=int(input('enter a number between 1 and 10 for the y (down) coordinate '))
            anchor_x=int(input('enter a number between 1 and 10 for the x (over) coordinate '))
            print(f"\nTargeting a '{ship_type}' in quadrant {quadrant} at anchor ({anchor_y} , {anchor_x})")
            vector = make_ship_shape_from_anchorXY(anchor_x, anchor_y, ship_type)

            try:
                results = vector_search(self.battleship_table, quadrant, vector, self.match_percentage_threshold)
                if results:
                    print(f"\nAt least one ship detected in quadrant {quadrant}:")
                    for match in results:
                        print(f"  - Detected_Ship_Class: {match['ship_class']}, Match_Percentage: {match['match_percentage']}%")
                        if match['match_percentage'] > 99.99:
                            print(f"\n\n\t<****> AFTER {attempt_counter} ATTEMPTS <****> \n\n\t\tPERFECT HIT -- EXITING PROGRAM")
                            self.blast_ship_out_of_existence(match['uuid'])
                            close_pool()
                            sys.exit(0)
                else:
                    print("No similar and/or nearby ships detected in quadrant.")
                attempt_counter += 1
            except Exception as e:
                print(f"❌ Error during processing: {e}")

        ## end of condition check for attempt_counter<max_attempts
        print('\n\n\t<****> You have used up all your attempts, Exiting...\n')
        close_pool()
        sys.exit(0)


    def explain_game_play(self):
        explain_string = """Welcome to battleship!
        Battleships live in 1 of 4 quadrants
        Battleships have anchor points defined as an X,Y coordinate
        X values can be between 1 and 10
        Y values can be between 1 and 10

        You play by guessing the ship_type, anchor location of a battleship, and its quadrant.
        To target a battleship, you provide an X,Y coordinate and a quadrant
        You will be prompted to enter each value on a separate line:
        Quadrant
        ship_type
        Y
        X

        Good LucK!  Now, go sink a Battleship!"""
        print(explain_string)
        input('\nHit enter to continue...')

    def blast_ship_out_of_existence(self, pk):
        print(f'\n\n%^%^%^%^***. KABLOOEY!!!!! \n\ndeleting ship with UUID == {pk}')
        try:
            destroy_ship(self.battleship_table, pk)
        except Exception as e:
            print(f"❌ Error during deletion of ship {pk}: \n{e}")


    # loops so that a user can add arbitrary number of ships:
    def ask_place_another(self):
        decision='y'
        while(decision=='y' or decision=='Y'):
            decision = input('Do you wish to add a ship to the database? (y / n)  ')
            if decision=='end':
                close_pool()
                sys.exit(0)
            if (decision=='y' or decision=='Y'):
                self.place_new_ship()


    # inserts a new row into the database that represents a ship at a location in a quadrant
    def place_new_ship(self):
        usr_input=''
        while usr_input=='':
            usr_input=input('enter a number between 1 and 4 for the quadrant ')
            if usr_input=='end':
                close_pool()
                sys.exit(0)
            quadrant=int(usr_input)
        ship_type_num=''
        while ship_type_num=='':
            ship_type_num=input('Enter a number corresponding to a ship type: 1 (destroyer) 2 (skiff) 3 (submarine) 4 (aircraft_carrier)  ')
            if ship_type_num=='end':
                close_pool()
                sys.exit(0)
        if ship_type_num=='1':
            ship_type='destroyer'
        elif ship_type_num=='2':
            ship_type='skiff'
        elif ship_type_num=='3':
            ship_type='submarine'
        elif ship_type_num=='4':
            ship_type='aircraft_carrier'
        anchor_y=int(input('enter a number between 1 and 10 for the y (down) coordinate '))
        anchor_x=int(input('enter a number between 1 and 10 for the x (over) coordinate '))

        pop = Populator(1, 1)
        pop.insert_vectorized_object(ship_type, quadrant, anchor_x, anchor_y)
            

# --- Likely entry point for the python interpretor ---
if __name__ == '__main__':
    ensure_indices()
    player = HumanPlayer(float(sys.argv[1]), int(sys.argv[2]))
    player.explain_game_play()
    player.ask_place_another()
    player.run()
    close_pool()
