import random
import time,sys,os

from vector_battleship_create import make_ship_shape_from_anchorXY
from private_stuff import vector_search, destroy_ship, get_max_quadrants, close_pool
''' 
This class provides the behavior of an automated player who:
1. picks a quadrant at random
2. picks a ship type at random
3. picks an anchor point at random
4. checks for collision between ship at anchor point in quadrant and ships in vector database
5. prints out result
6. sleeps for provided sleeptime when it detects similar ships in the same quadrant and hones in on same quadrant 
7. will switch its target ship type to match nearest ship if argument list includes the value: True
python3 battle_bot.py <acceptable similarity to drive behavior> <sleep time in millis> <should switch ship type>
python3 battle_bot.py 65 100 False

'''

class AutomatedPlayer:
    def __init__(self, match_percentage_threshold, max_attempts, sleep_when_honing_millis, should_switch_ship_type):
        self.battleship_table = os.getenv("BATTLESHIP_TABLE", "battleship")
        self.match_percentage_threshold = match_percentage_threshold
        self.max_attempts = int(max_attempts)
        self.sleep_when_honing_millis=int(sleep_when_honing_millis) * .001
        if(should_switch_ship_type == "True"):
            self.should_switch_ship_type = True
        else:
            self.should_switch_ship_type = False
        self.ship_types = ['submarine', 'destroyer', 'aircraft_carrier', 'skiff']
        self.max_quadrants = self.get_max_quadrants()
        self.quadrants = list(range(1, self.max_quadrants + 1)) # table may be loaded with up to 1 million
        
        print(f"should_switch_ship_type == {self.should_switch_ship_type}")
        

    def think_and_offer_next_guess(self, guesses_memory_list):
        """
        Determines the next move. Logic:
        - If no memory, start at Q1 (1,1).
        - If last guess was a total miss (0.0), increment quadrant.
        - If last guess was a hit/improvement, continue scanning current quadrant.
        """
        # 1. Initial Case: No prior guesses
        history_exists = False
        trend_warmer = False
        if not guesses_memory_list:
            new_guess = (1, 1, 1, 0.0) # (quadrant, y, x, score)
            guesses_memory_list.append(new_guess)
            return new_guess

        # 2. Extract last result
        last_quad, last_y, last_x, last_score = guesses_memory_list[-1]
        
        new_quad = last_quad
        new_y, new_x = last_y, last_x

        # 3. Extract nearness trend from prior guesses:
        if len(guesses_memory_list) >= 2:
            history_exists = True
            history_quad, history_y, history_x, history_score = guesses_memory_list[-2]
        if history_exists == True and last_score > history_score:
            trend_warmer = True
        elif history_exists == True and last_score <= history_score:
            trend_warmer = False
        # 4. Quadrant Rotation Logic
        # If score is 0, we move to the next quadrant and reset coords
        if last_score == 0.0:
            new_quad = last_quad + 1 if last_quad < self.max_quadrants else 1
            new_y, new_x = 1, 1
        else:
            # 5. Intra-Quadrant Scanning Logic (Warmer/Honing)
            if (not history_exists) or trend_warmer:
                # WARMEST/INITIAL: Continue the scan
                if last_y < 10:
                    new_y = last_y + 1
                elif last_x < 10:
                    new_y = 1
                    new_x = last_x + 1
                else:
                    # Reached 10,10 - force quadrant shift
                    last_score = 0.0 

            elif not trend_warmer:
                # COLDER: The last move was a mistake. 
                # Try jumping to the next column and resetting Y to 1 
                # to "clear" the cold zone.
                if last_x < 10:
                    new_x = last_x + 1
                    new_y = 1
                else:
                    # X is exhausted
                    last_score = 0.0

            # Final Safety Clamp: Ensure we never go below 1 or above 10
            new_x = max(1, min(10, new_x))
            new_y = max(1, min(10, new_y))

            # 6. Quadrant Transition (Triggered by score 0 or exhaustion)
            if last_score == 0.0:
                new_quad = (last_quad % self.max_quadrants) + 1
                new_y, new_x = 1, 1

        new_guess_tuple = (new_quad, new_y, new_x, 0.0)
        guesses_memory_list.append(new_guess_tuple)
        return new_guess_tuple
    
    def get_max_quadrants(self):
        max_quadrants = get_max_quadrants(self.battleship_table)
        print(f"max quadrants == {max_quadrants}")
        return max_quadrants
                        

    def run(self):
        duration = 0
        attempt_limit = self.max_attempts
        attempt_counter = 0
        guesses_memory_list = [] # Stores (quad, y, x, score)
        
        # State tracking
        target_ship_type = self.switch_target_ship_type("skiff") # variance in starting ship is fun!
        target_ship_reuse_count = 0
        
        print("🚀 Initializing Systematic Search...")

        while attempt_counter < attempt_limit:
            attempt_counter += 1
            
            # 1. Ask the 'thinker' for the next coordinate/quadrant
            current_guess = self.think_and_offer_next_guess(
                guesses_memory_list
            )
            
            # Unpack the guess (Note: we use [-1] from the list modified by the thinker)
            quadrant, anchor_y, anchor_x, _ = current_guess
            
            # 2. Construct the vector and run the search
            vector = make_ship_shape_from_anchorXY(anchor_x, anchor_y, target_ship_type)

            try:
                match_found = False
                time_before = time.time_ns()
                results = vector_search(self.battleship_table, quadrant, vector, self.match_percentage_threshold)
                duration = (time.time_ns() / 1000000) - (time_before / 1000000)
                print(f"Vector Query Took: {duration:.3f} ms")

                if results:
                    best = results[0]
                    ship_class = best['ship_class']
                    score = best['match_percentage']
                    anchor_pt = best['anchorpoint']

                    print(f"Attempt {attempt_counter}: Q{quadrant} (down:{anchor_x},across:{anchor_y}) -> MATCH: {score}%  against ship_type {ship_class}")

                    if ship_class == 'flotsam':
                        score = 0.0
                        print(f"Closest match is {ship_class} near that location - CHANGING TARGET QUADRANT")

                    guesses_memory_list[-1] = (quadrant, anchor_y, anchor_x, score)

                    if score == 100.0:
                        print(f"\n🎯 PERFECT HIT! Ship {best['uuid']} destroyed at {anchor_pt}.")
                        self.blast_ship_out_of_existence(best['uuid'])
                        return

                    if score > self.match_percentage_threshold and ship_class == target_ship_type:
                        print(f"📡 Honing in... Current count: {target_ship_reuse_count}")
                        target_ship_reuse_count += 1
                        time.sleep(self.sleep_when_honing_millis)
                        match_found = True
                    elif score > self.match_percentage_threshold and ship_class != target_ship_type:
                        if self.should_switch_ship_type:
                            print(f"SURPRISE!  Targeting discovered {ship_class} near that location")
                            target_ship_reuse_count = 0
                            time.sleep(self.sleep_when_honing_millis)
                            target_ship_type = ship_class
                            match_found = True

                if not match_found:
                    print(f"Attempt {attempt_counter}: Q{quadrant} (down:{anchor_x},across:{anchor_y}) -> No detections.")
                    guesses_memory_list[-1] = (quadrant, anchor_y, anchor_x, 0.0)
                    if self.should_switch_ship_type:
                        print(f"SHOULD SWITCH -->  {self.should_switch_ship_type}")
                        target_ship_type = self.switch_target_ship_type(target_ship_type)
                    if target_ship_reuse_count > 9:
                        quadrant = quadrant + 1
                        target_ship_reuse_count = 0

            except Exception as e:
                print(f"❌ Error: {e}")

        print(f"\nLimit reached. Total attempts: {attempt_counter}")

    def switch_target_ship_type(self,prior_ship_type):
        target_ship_type = prior_ship_type
        target_ship_type = random.choice(self.ship_types)
        #print(f"SHOULD SWITCH ==> {self.should_switch_ship_type} switching to {target_ship_type}")
        return target_ship_type

    def blast_ship_out_of_existence(self, pk):
        print(f'\n\n%^%^%^%^***. KABLOOEY!!!!! \n\ndeleting ship with UUID == {pk}')
        try:
            destroy_ship(self.battleship_table, pk)
        except Exception as e:
            print(f"❌ Error during deletion of ship {pk}: \n{e}")

# --- Likely entry point for the python interpretor ---
if __name__ == "__main__":
    if(len(sys.argv)==1):
        print("You need at least the first arg of the following ordered args: <percentage> <max_attempts> <sleep_time> <should_switch>")
        print("Example: python3 battle_bot.py 65 1000 0 False")
        print("Example: python3 battle_bot.py 85")
        sys.exit(0)
    max_attempts = 300 # default
    should_switch_ship = False # an aggressive bot will greedily blow up any ship near its target location
    honing_sleep_time=200 #millis
    percentage_match_target = 65.00
    if(len(sys.argv)>1):
        percentage_match_target = float(sys.argv[1])
    if(len(sys.argv)>2):
        max_attempts = sys.argv[2]
    if(len(sys.argv)>3):
        honing_sleep_time=sys.argv[3]
    if(len(sys.argv)>4):
        should_switch_ship = sys.argv[4]
    player = AutomatedPlayer(percentage_match_target,max_attempts,honing_sleep_time,should_switch_ship)
    
    player.run()
    close_pool()
