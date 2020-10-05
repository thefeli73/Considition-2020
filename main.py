# import api
import time
import sys
from sys import exit
from game_layer import GameLayer
import game_state
import traceback

api_key = "74e3998d-ed3d-4d46-9ea8-6aab2efd8ae3"
# The different map names can be found on considition.com/rules
map_name = "training1"  # TODO: You map choice here. If left empty, the map "training1" will be selected.

game_layer = GameLayer(api_key)
state = game_layer.game_state
usePrebuiltStrategy = False
timeUntilRunEnds = 50
rounds_between_energy = 5
utilities = 3

EMA_temp = None
building_under_construction = None
availableTiles = []


def main():
    #game_layer.force_end_game()
    game_layer.new_game(map_name)
    print("Starting game: " + game_layer.game_state.game_id)
    game_layer.start_game()
    # exit game after timeout
    start_time = time.time()
    chartMap()
    global EMA_temp
    while game_layer.game_state.turn < game_layer.game_state.max_turns:
        try:
            if EMA_temp is None:
                EMA_temp = game_layer.game_state.current_temp
            ema_k_value = (2/(rounds_between_energy+1))
            EMA_temp = game_layer.game_state.current_temp * ema_k_value + EMA_temp*(1-ema_k_value)
            take_turn()
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


def take_turn():
    if not usePrebuiltStrategy:
        # TODO Implement your artificial intelligence here.
        # TODO Take one action per turn until the game ends.
        # TODO The following is a short example of how to use the StarterKit
        if something_needs_attention():
            pass
        else:
            develop_society()
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

def develop_society():
    state = game_layer.game_state
    if len(state.residences) < 5:
        build("Apartments")
    elif len(state.utilities) < 1:
        build("WindTurbine")
    elif state.funds > 25000 and len(game_layer.game_state.residences) < 11:
        build("HighRise")
    else:
        game_layer.wait()

def something_needs_attention():
    print("Checking for emergencies")
    global building_under_construction
    global edit_temp
    global maintain
    state = game_layer.game_state

    #check if temp needs adjusting
    edit_temp = (False, 0)
    for i in range(len(state.residences)):
        if (state.turn % rounds_between_energy == i) and not state.residences[i].build_progress < 100:
            edit_temp = (True, i)

    #check if need for maintainance
    maintain = (False, 0)
    for i in range(len(state.residences)):
        if state.residences[i].health < 41+rounds_between_energy*game_layer.get_residence_blueprint(state.residences[i].building_name).decay_rate:
            maintain = (True, i)

    if maintain[0]:
        game_layer.maintenance((state.residences[maintain[1]].X, state.residences[maintain[1]].Y))
        return True
    elif edit_temp[0]: #adjust temp of building
        adjustEnergy(state.residences[edit_temp[1]])
        return True
    elif building_under_construction is not None: #finish construction
        if (len(game_layer.game_state.residences) >= building_under_construction[2]) and (game_layer.game_state.residences[building_under_construction[2]].build_progress < 100):
            game_layer.build((building_under_construction[0], building_under_construction[1]))
            return True
        elif (len(game_layer.game_state.utilities)-1 >= building_under_construction[2]) and (game_layer.game_state.utilities[building_under_construction[2]].build_progress < 100):
            game_layer.build((building_under_construction[0], building_under_construction[1]))
            return True
        else:
            building_under_construction = None
            return False
    else:
        return False

def chartMap():
    state = game_layer.game_state
    for x in range(len(state.map) - 1):
        for y in range(len(state.map) - 1):
            if state.map[x][y] == 0:
                availableTiles.append((x, y))
    optimizeAvailableTiles()

def adjustEnergy(currentBuilding):
    global rounds_between_energy
    global EMA_temp
    blueprint = game_layer.get_residence_blueprint(currentBuilding.building_name)
    outDoorTemp = game_layer.game_state.current_temp * 2 - EMA_temp

    temp_acceleration = (2*(21 - currentBuilding.temperature)/(rounds_between_energy))

    effectiveEnergyIn = ((temp_acceleration - 0.04 * currentBuilding.current_pop + (currentBuilding.temperature - outDoorTemp) * blueprint.emissivity) / 0.75) + blueprint.base_energy_need

    if effectiveEnergyIn > blueprint.base_energy_need:
        game_layer.adjust_energy_level((currentBuilding.X, currentBuilding.Y), effectiveEnergyIn)
    elif effectiveEnergyIn < blueprint.base_energy_need:
        game_layer.adjust_energy_level((currentBuilding.X, currentBuilding.Y), blueprint.base_energy_need + 0.01)
    else:
        print("you did it!")
        game_layer.wait()


def optimizeAvailableTiles():
    #hitta #utilities antal bästa platser i mitten av smeten och sätt de först, sätt allt runt dem i ordning så närmast är längst fram i listan
    pass


def build(structure):
    print("Building " + structure)
    state = game_layer.game_state
    global building_under_construction
    global rounds_between_energy
    for i in range(len(availableTiles)):
        if isinstance(availableTiles[i], tuple):
            game_layer.place_foundation(availableTiles[i], structure)
            for building in state.available_residence_buildings:
                if structure in building.building_name:
                    for j in range(len(state.residences)):
                        building = state.residences[j]
                        coords_to_check = (building.X, building.Y)
                        if coords_to_check == availableTiles[i]:
                            availableTiles[i] = building
                            building_under_construction = (building.X, building.Y, j)
                            rounds_between_energy = len(state.residences)+2
                            return True
            for building in state.available_utility_buildings:
                if structure in building.building_name:
                    for j in range(len(state.utilities)):
                        building = state.utilities[j]
                        coords_to_check = (building.X, building.Y)
                        if coords_to_check == availableTiles[i]:
                            availableTiles[i] = building
                            building_under_construction = (building.X, building.Y, j)
                            rounds_between_energy = len(state.residences)+2
                            return True
            return False


if __name__ == "__main__":
    main()
