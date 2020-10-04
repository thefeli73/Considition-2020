# import api
import time
import sys
from sys import exit
from game_layer import GameLayer
import traceback

timeUntilRunEnds = 30

api_key = "74e3998d-ed3d-4d46-9ea8-6aab2efd8ae3"
# The different map names can be found on considition.com/rules
map_name = "training1"  # TODO: You map choice here. If left empty, the map "training1" will be selected.

game_layer = GameLayer(api_key)
state = game_layer.game_state
usePrebuiltStrategy = False


def main():

    #game_layer.force_end_game()
    game_layer.new_game(map_name)
    print("Starting game: " + game_layer.game_state.game_id)
    game_layer.start_game()
    # exit game after timeout
    start_time = time.time()
    while game_layer.game_state.turn < game_layer.game_state.max_turns:
        try:
            linus_take_turn()
        except:
            print(traceback.format_exc())
            game_layer.end_game()
            exit()
        time_diff = time.time() - start_time
        if time_diff > timeUntilRunEnds:
            game_layer.end_game()
            exit()
    print("Done with game: " + game_layer.game_state.game_id)
    print("Final score was: " + str(game_layer.get_score()["finalScore"]))

def linus_take_turn(i):
    freeSpace = []

    state = game_layer.game_state
    for x in range(len(state.map)-1):
        for y in range(len(state.map)-1):
            if state.map[x][y] == 0:
                freeSpace.append((x,y))

    #print(mylist)

    #if (i == 0 or i%5 == 0)and i<26:
    #    game_layer.place_foundation(freeSpace[(i//5)+2], game_layer.game_state.available_residence_buildings[i//5].building_name)

    if (game_layer.game_state.turn == 0):
        game_layer.place_foundation(freeSpace[2], game_layer.game_state.available_residence_buildings[0].building_name)
    the_first_residence = state.residences[0]
    if the_first_residence.build_progress < 100:
        game_layer.build(freeSpace[2])
    if len(state.residences) == 1:
        game_layer.place_foundation(freeSpace[3], game_layer.game_state.available_residence_buildings[5].building_name)
    the_second_residence = state.residences[1]
    if the_second_residence.build_progress < 100:
        game_layer.build(freeSpace[3])
    if len(state.residences) == 2:
        game_layer.place_foundation(freeSpace[5], game_layer.game_state.available_residence_buildings[0].building_name)
    the_third_residence = state.residences[2]
    if the_third_residence.build_progress < 100:
        game_layer.build(freeSpace[5])
    if len(state.residences) == 3:
        game_layer.place_foundation((4,4), game_layer.game_state.available_residence_buildings[4].building_name)
    the_fourth_residence = state.residences[3]
    if the_fourth_residence.build_progress < 100:
        game_layer.build((4,4))

    if len(state.residences) == 4:
        game_layer.place_foundation((4,5), game_layer.game_state.available_residence_buildings[4].building_name)
    the_fifth_residence = state.residences[4]
    if the_fifth_residence.build_progress < 100:
        game_layer.build((4,5))

    if len(state.residences) == 5:
        game_layer.place_foundation((4,6), game_layer.game_state.available_residence_buildings[4].building_name)
    the_sixth_residence = state.residences[5]
    if (the_sixth_residence.build_progress < 100) and game_layer.game_state.funds > 4000:
        game_layer.build((4,6))

    elif the_first_residence.health < 70:
        game_layer.maintenance(freeSpace[2])
    elif the_second_residence.health < 70:
        game_layer.maintenance(freeSpace[3])
    elif the_third_residence.health < 70:
        game_layer.maintenance(freeSpace[5])
    elif the_fourth_residence.health < 70:
        game_layer.maintenance((4,4))
    elif the_fifth_residence.health < 70:
        game_layer.maintenance((4,5))
    elif the_sixth_residence.health < 70:
        game_layer.maintenance((4,6))
    elif (the_second_residence.health > 70) and not len(state.utilities) > 0:
        game_layer.place_foundation(freeSpace[4], game_layer.game_state.available_utility_buildings[2].building_name)
    elif (state.utilities[0].build_progress < 100):
        game_layer.build(freeSpace[4])


    #elif (game_layer.game_state.turn > 35) and not len(state.utilities) > 1:
    #    game_layer.place_foundation((4,6), game_layer.game_state.available_utility_buildings[1].building_name)
    #elif (state.utilities[1].build_progress < 100):
    #    game_layer.build((4,6))

    elif (game_layer.game_state.turn % 10 == 0):
        adjustEnergy2(the_first_residence, 21)
    elif (game_layer.game_state.turn % 5 == 0):
        adjustEnergy2(the_second_residence, 21)
    elif (game_layer.game_state.turn % 5 == 1):
        adjustEnergy2(the_third_residence, 21)
    elif (game_layer.game_state.turn % 5 == 2):
        adjustEnergy2(the_fourth_residence, 21)
    elif (game_layer.game_state.turn % 5 == 3):
        adjustEnergy2(the_fifth_residence, 21)
    elif (game_layer.game_state.turn % 5 == 4):
        adjustEnergy2(the_sixth_residence, 21)
    else:
    # messages and errors for console log
        game_layer.wait()
    for message in game_layer.game_state.messages:
        print(message)
    for error in game_layer.game_state.errors:
        print("Error: " + error)

def take_turn():
    if not usePrebuiltStrategy:
        # TODO Implement your artificial intelligence here.
        # TODO Take one action per turn until the game ends.
        # TODO The following is a short example of how to use the StarterKit


        # messages and errors for console log
        for message in game_layer.game_state.messages:
            print(message)
        for error in game_layer.game_state.errors:
            print("Error: " + error)


    # pre-made test strategy
    # which came with
    # starter kit
    if usePrebuiltStrategy:
        state = game_layer.game_state
        if len(state.residences) < 1:
            for i in range(len(state.map)):
                for j in range(len(state.map)):
                    if state.map[i][j] == 0:
                        x = i
                        y = j
                        break
            game_layer.place_foundation((x, y), game_layer.game_state.available_residence_buildings[0].building_name)
        else:
            the_only_residence = state.residences[0]
            if the_only_residence.build_progress < 100:
                game_layer.build((the_only_residence.X, the_only_residence.Y))
            elif the_only_residence.health < 50:
                game_layer.maintenance((the_only_residence.X, the_only_residence.Y))
            elif the_only_residence.temperature < 18:
                blueprint = game_layer.get_residence_blueprint(the_only_residence.building_name)
                energy = blueprint.base_energy_need + 0.5 \
                         + (the_only_residence.temperature - state.current_temp) * blueprint.emissivity / 1 \
                         - the_only_residence.current_pop * 0.04
                game_layer.adjust_energy_level((the_only_residence.X, the_only_residence.Y), energy)
            elif the_only_residence.temperature > 24:
                blueprint = game_layer.get_residence_blueprint(the_only_residence.building_name)
                energy = blueprint.base_energy_need - 0.5 \
                         + (the_only_residence.temperature - state.current_temp) * blueprint.emissivity / 1 \
                         - the_only_residence.current_pop * 0.04
                game_layer.adjust_energy_level((the_only_residence.X, the_only_residence.Y), energy)
            elif state.available_upgrades[0].name not in the_only_residence.effects:
                game_layer.buy_upgrade((the_only_residence.X, the_only_residence.Y), state.available_upgrades[0].name)
            else:
                game_layer.wait()
        for message in game_layer.game_state.messages:
            print(message)
        for error in game_layer.game_state.errors:
            print("Error: " + error)

def chartMap():
    availableTiles = []
    for x in range(len(state.map) - 1):
        for y in range(len(state.map) - 1):
            if state.map[x][y] == 0:
                availableTiles.append((x, y))

if __name__ == "__main__":
    main()
