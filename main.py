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
# settings
time_until_run_ends = 70
utilities = 3
money_reserve_multiplier = 1.5
desiredTemperature = 21
#logresidence[i][x] = temperatur nr X i byggnad med index i (andra byggnaden), samma i som state.residences
logResidenceInfo = []
PID_Ivalues = []


def main():
    global EMA_temp, rounds_between_energy, building_under_construction, available_tiles, state, queue_timeout
    # global vars
    rounds_between_energy = 5
    EMA_temp = None
    building_under_construction = None
    available_tiles = []
    queue_timeout = 1


    game_layer.new_game(map_name)
    print("Starting game: " + game_layer.game_state.game_id)
    game_layer.start_game()
    # start timeout timer
    start_time = time.time()
    state = game_layer.game_state
    chart_map()

    while state.turn < state.max_turns:
        state = game_layer.game_state
        try:
            if EMA_temp is None:
                EMA_temp = state.current_temp
            ema_k_value = (2/(rounds_between_energy+1))
            EMA_temp = state.current_temp * ema_k_value + EMA_temp*(1-ema_k_value)
            take_turn()
            recordTempHistories(state.residences)
        except Exception:
            print(traceback.format_exc())
            game_layer.end_game()
            exit()
        time_diff = time.time() - start_time
        if time_diff > time_until_run_ends:
            game_layer.end_game()
            exit()
    print("Done with game: " + state.game_id)
    print("Final score was: " + str(game_layer.get_score()["finalScore"]))
    return (state.game_id, game_layer.get_score()["finalScore"])


def take_turn():
    global state
    # TODO Implement your artificial intelligence here.
    # TODO Take one action per turn until the game ends.
    # TODO The following is a short example of how to use the StarterKit
    if something_needs_attention():
        pass
    elif develop_society():
        pass
    else:
        game_layer.wait()

    # messages and errors for console log
    for message in state.messages:
        print(message)
    for error in state.errors:
        print("Error: " + error)

    #if (i == 0 or i%5 == 0)and i<26:
    #    game_layer.place_foundation(freeSpace[(i//5)+2], game_layer.game_state.available_residence_buildings[i//5].building_name)
    '''
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
        game_layer.place_foundation(freeSpace[5], game_layer.game_state.available_residence_buildings[1].building_name)
    the_third_residence = state.residences[2]
    if the_third_residence.build_progress < 100:
        game_layer.build(freeSpace[5])
    if len(state.residences) == 3:
        game_layer.place_foundation((4,4), game_layer.game_state.available_residence_buildings[4].building_name)
    the_fourth_residence = state.residences[3]
    if the_fourth_residence.build_progress < 100:
        game_layer.build((4,4))

    if len(state.residences) == 4:
        game_layer.place_foundation((4,5), game_layer.game_state.available_residence_buildings[3].building_name)
    the_fifth_residence = state.residences[4]
    if the_fifth_residence.build_progress < 100:
        game_layer.build((4,5))

    if len(state.residences) == 5:
        game_layer.place_foundation((4,6), game_layer.game_state.available_residence_buildings[4].building_name)
    the_sixth_residence = state.residences[5]
    if (the_sixth_residence.build_progress < 100) and game_layer.game_state.funds > 4000:
        game_layer.build((4,6))


    for i in range(len(state.residences)):
        if state.residences[i].health < 45:
            game_layer.maintenance(state.residences[i].X, state.residences[i].Y)

    for i in range(len(state.residences)):
        if game_layer.game_state.turn % ROUNDVARIABLE == i:
            adjustEnergy(the_first_residence)



    elif the_first_residence.health < :
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

    elif (game_layer.game_state.turn % rounds_between_energy == 0):
        adjustEnergy(the_first_residence)
    elif (game_layer.game_state.turn % rounds_between_energy == 1):
        adjustEnergy(the_second_residence)
    elif (game_layer.game_state.turn % rounds_between_energy == 2):
        adjustEnergy(the_third_residence)
    elif (game_layer.game_state.turn % rounds_between_energy == 3):
        adjustEnergy(the_fourth_residence)
    elif (game_layer.game_state.turn % rounds_between_energy == 4):
        adjustEnergy(the_fifth_residence)
    elif (game_layer.game_state.turn % rounds_between_energy == 5):
        adjustEnergy(the_sixth_residence)
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
        '''


def develop_society():
    global state, queue_timeout, available_tiles, utilities
    if queue_timeout > 1:
        queue_timeout -= 1


    # priority scores, 1 = very urgent, 0 = not urgent at all
    # queue modifier * funds modifier * existing houses modifier
    build_residence_score = (state.housing_queue / (15 * queue_timeout)) * (1 - (7500 / (1 + state.funds))) * (1 - (len(state.residences) / (1 + len(available_tiles) - utilities)))
    upgrade_residence_score = 0
    # existing houses modifier * funds modifier * existing utilities modifier
    build_utility_score = (len(state.residences) / (1 + len(available_tiles)-utilities)) * (1 - (16000 / (1 + state.funds))) * (1 - (len(state.utilities) / utilities))
    # turn modifier * funds modifier
    build_upgrade_score = (1 - (state.turn / 700)) * (2 - (15000 / (1 + state.funds)))

    if len(state.residences) < 1:
        build_residence_score = 100

    decision = [
        ('build_residence', build_residence_score),
        ('upgrade_residence', upgrade_residence_score),
        ('build_utility', build_utility_score),
        ('build_upgrade', build_upgrade_score)
    ]
    def sort_key(e):
        return e[1]
    decision.sort(reverse=True, key=sort_key)

    for i in range(4):
        if decision[0][0] == "build_residence":  # build housing
            queue_timeout = 5
            #if len(state.residences) < len(state.available_residence_buildings):
            #    return build(state.available_residence_buildings[len(state.residences)].building_name)
            #else:
            cbr = calculate_best_residence()
            if cbr:
                return build(cbr[1])
        if decision[0][0] == "build_utility":  # build utilities
            #return build("WindTurbine")
            pass
        if decision[0][0] == "upgrade_residence":  # build utilities
            pass
        if decision[0][0] == "build_upgrade":  # build upgrades
            for residence in state.residences:
                if state.available_upgrades[0].name not in residence.effects and (money_reserve_multiplier*3500 < state.funds) and ((total_income() - 6) > 50):
                    game_layer.buy_upgrade((residence.X, residence.Y), state.available_upgrades[0].name)
                    return True
                if state.available_upgrades[5].name not in residence.effects and (money_reserve_multiplier*1250 < state.funds):
                    game_layer.buy_upgrade((residence.X, residence.Y), state.available_upgrades[5].name)
                    return True
            gbp = get_best_upgrade()
            if gbp:
                game_layer.buy_upgrade((gbp[2].X, gbp[2].Y), gbp[1])
                return True
        del decision[0]

    return False



def something_needs_attention():
    global building_under_construction, edit_temp, maintain, state, rounds_between_energy

    # check if temp needs adjusting
    edit_temp = (False, 0)
    # check if need for maintenance
    maintain = (False, 0)
    for i in range(len(state.residences)):
        if state.residences[i].health < 35+rounds_between_energy*game_layer.get_residence_blueprint(state.residences[i].building_name).decay_rate:
            maintain = (True, i)
        if (state.turn % rounds_between_energy == i) and not state.residences[i].build_progress < 100:
            edit_temp = (True, i)

    if maintain[0]:  # check maintenance
        game_layer.maintenance((state.residences[maintain[1]].X, state.residences[maintain[1]].Y))
        return True
    elif edit_temp[0]:  # adjust temp of buildings
        return adjust_energy(state.residences[edit_temp[1]])
    elif building_under_construction is not None:  # finish construction
        if (len(state.residences)-1 >= building_under_construction[2]) and (state.residences[building_under_construction[2]].build_progress < 100):
            game_layer.build((building_under_construction[0], building_under_construction[1]))
            if not state.residences[building_under_construction[2]].build_progress < 100:
                building_under_construction = None
            return True
        elif (len(state.utilities)-1 >= building_under_construction[2]) and (state.utilities[building_under_construction[2]].build_progress < 100):
            game_layer.build((building_under_construction[0], building_under_construction[1]))
            if not state.residences[building_under_construction[2]].build_progress < 100:
                building_under_construction = None
            return True
        else:
            building_under_construction = None
            return False
    else:
        return False


def total_income():
    global state
    income = 0
    for residence in state.residences:
        income += game_layer.get_residence_blueprint(residence.building_name).income_per_pop * residence.current_pop
    return income


def get_best_upgrade():
    global state

    best_upgrade = []
    for residence in state.residences:
        cbu = calculate_best_upgrade(residence)
        if cbu is not False:
            score = cbu[0]
            upgrade = cbu[1]
            best_upgrade.append((score, upgrade, residence))

    def sort_key(e):
        return e[0]
    best_upgrade.sort(reverse=True, key=sort_key)
    if not best_upgrade:
        return False
    return best_upgrade[0]


def calculate_best_upgrade(current_building):
    global state

    rounds_left = 700 - state.turn
    current_pop = current_building.current_pop
    blueprint = game_layer.get_blueprint(current_building.building_name)
    base_energy_need = blueprint.base_energy_need
    best_upgrade = []
    for upgrade in state.available_upgrades:
        effect = game_layer.get_effect(upgrade.effect)
        if (upgrade.name not in current_building.effects) and ((total_income() + effect.building_income_increase) > 50) and (money_reserve_multiplier*upgrade.cost < state.funds):
            average_outdoor_temp = (state.max_temp - state.min_temp)/2

            average_heating_energy = (((21 - average_outdoor_temp) * blueprint.emissivity * effect.emissivity_multiplier) / 0.75)
            old_average_heating_energy = (((21 - average_outdoor_temp) * blueprint.emissivity) / 0.75)

            lifetime_energy = (base_energy_need + effect.base_energy_mwh_increase + average_heating_energy - effect.mwh_production) * rounds_left
            old_lifetime_energy = (base_energy_need + old_average_heating_energy) * rounds_left


            upgrade_co2 = (effect.co2_per_pop_increase * 0.03) * current_pop * rounds_left + (0.1 * lifetime_energy / 1000)
            old_co2 = 0.03 * current_pop * rounds_left + (0.1 * old_lifetime_energy / 1000)
            co2 = upgrade_co2 - old_co2
            max_happiness = effect.max_happiness_increase * rounds_left

            score = max_happiness/10 - co2
            best_upgrade.append((score, upgrade.name))

    def sort_key(e):
        return e[0]
    best_upgrade.sort(reverse=True, key=sort_key)
    if not best_upgrade:
        return False
    return best_upgrade[0]


def calculate_best_residence():
    global state

    rounds_left = 700 - state.turn
    best_residence = []
    for residence_blueprint in state.available_residence_buildings:
        if state.turn >= residence_blueprint.release_tick and (money_reserve_multiplier*residence_blueprint.cost < state.funds):
            average_outdoor_temp = (state.max_temp - state.min_temp)/2
            average_heating_energy = ((0 - 0.04 * residence_blueprint.max_pop + (21 - average_outdoor_temp) * residence_blueprint.emissivity) / 0.75)
            lifetime_energy = (residence_blueprint.base_energy_need + average_heating_energy) * rounds_left

            co2 = 0.03 * residence_blueprint.max_pop * rounds_left + residence_blueprint.co2_cost + (0.1 * lifetime_energy / 1000)
            max_happiness = residence_blueprint.max_happiness * rounds_left

            score = residence_blueprint.max_pop*15 + max_happiness/10 - co2
            best_residence.append((score, residence_blueprint.building_name))

    def sort_key(e):
        return e[0]
    best_residence.sort(reverse=True, key=sort_key)
    if not best_residence:
        return False
    return best_residence[0]


def chart_map():
    global state
    for x in range(len(state.map) - 1):
        for y in range(len(state.map) - 1):
            if state.map[x][y] == 0:
                available_tiles.append((x, y))
    optimize_available_tiles()


def evaluateTile(tile):
    # score -1 för att ta bort själva tilen man checkar
    score = -1
    x = tile[0]
    y = tile[1]

    for i in range(5):
        for j in range(5):
            if state.map[x - 2 + i][y - 2 + i] and abs(i - 2) + abs(j - 2) <= 2:
                score += 1


def optimize_available_tiles():
    global average_x, average_y, score_list
    average_x = 0
    average_y = 0
    score_list = []
    for tile in available_tiles:  # calc average coordinates
        average_x += tile[0]
        average_y += tile[1]
    average_x /= len(available_tiles)
    average_y /= len(available_tiles)
    for tile in available_tiles:
        tile_score = abs(tile[0] - average_x) + abs(tile[1] - average_y)
        score_list.append((tile_score, tile))

    def sort_key(e):
        return e[0]
    score_list.sort(key=sort_key)
    for i in range(len(score_list)):
        available_tiles[i] = score_list[i][1]
    print("average x,y: " + str(average_x) + ", " + str(average_y))


def adjust_energy(current_building):
    global rounds_between_energy, EMA_temp, state
    blueprint = game_layer.get_residence_blueprint(current_building.building_name)
    base_energy = blueprint.base_energy_need
    if "Charger" in current_building.effects:
        base_energy += 1.8

    emissivity = blueprint.emissivity
    if "Insulation" in current_building.effects:
        emissivity *= 0.6

    outDoorTemp = state.current_temp * 2 - EMA_temp
    temp_acceleration = (2*(21 - current_building.temperature)/(rounds_between_energy))

    effectiveEnergyIn = ((temp_acceleration - 0.04 * current_building.current_pop + (current_building.temperature - outDoorTemp) * emissivity) / 0.75) + base_energy

    if effectiveEnergyIn > base_energy:
        game_layer.adjust_energy_level((current_building.X, current_building.Y), effectiveEnergyIn)
        return True
    elif effectiveEnergyIn < base_energy:
        game_layer.adjust_energy_level((current_building.X, current_building.Y), base_energy + 0.01)
        return True
    else:
        return False


def build(structure):
    global building_under_construction, rounds_between_energy, state
    # print("Building " + structure)
    for i in range(len(available_tiles)):
        if isinstance(available_tiles[i], tuple):
            game_layer.place_foundation(available_tiles[i], structure)
            for building in state.available_residence_buildings:
                if structure in building.building_name:
                    for j in range(len(state.residences)):
                        building = state.residences[j]
                        coords_to_check = (building.X, building.Y)
                        if coords_to_check == available_tiles[i]:
                            available_tiles[i] = building
                            building_under_construction = (building.X, building.Y, j)
                            rounds_between_energy = len(state.residences)+2
                            return True
            for building in state.available_utility_buildings:
                if structure in building.building_name:
                    for j in range(len(state.utilities)):
                        building = state.utilities[j]
                        coords_to_check = (building.X, building.Y)
                        if coords_to_check == available_tiles[i]:
                            available_tiles[i] = building
                            building_under_construction = (building.X, building.Y, j)
                            rounds_between_energy = len(state.residences)+2
                            return True
            return False


def check_energies(buildings):
    for building in enumerate(buildings):
        if not 19 < building[1].temperature < 23:
            adjust_energy_PID(building[0], building[1])
    return False


def adjust_energy_PID(index, current_building):
    newEnergy = 0
    blueprint = game_layer.get_residence_blueprint(current_building.building_name)
    base_energy = blueprint.base_energy_need
    global state, desiredTemperature, PID_Ivalues
    KP, KI, KD = getBuildingConstants(current_building.building_name)

    P = (desiredTemperature - current_building.temperature) * KP
    I = current_building.I + (
                desiredTemperature - current_building.temperature) * KI  # TODO fixa current_bulding.I PID_Ivalues listan
    D = calcCurrentD(logResidenceInfo[index]) * KD  # jag är genius

    newEnergy = P + I + D

    if newEnergy + base_energy < base_energy:
        game_layer.adjust_energy_level((current_building.X, current_building.Y), base_energy + 0.01)
        return True
    elif newEnergy + base_energy > base_energy:
        game_layer.adjust_energy_level((current_building.X, current_building.Y), newEnergy + base_energy)
        return True
    else:
        return False


def calcCurrentD(tmp_history):
    # måste hitta necessaryDenominator för nytt nrDerivativeDots
    ans = 0
    consts = [-2, -1, 0, 1, 2]
    nrDerivativeDots = 5  # endast udda antal
    necessaryDenominator = 10
    # for currDerivativeConstant in (range(-1*(nrDerivativeDots//2), (nrDerivativeDots//2)+1)):   #+1 pga non-inclusive
    for i in range(5):
        ans += tmp_history[i] * consts[i]

    return ans / necessaryDenominator


def recordTempHistories(buildings):
    global logResidenceInfo, PID_Ivalues
    while len(logResidenceInfo) < len(buildings):
        logResidenceInfo.append([])
    while len(PID_Ivalues) < len(buildings):
        PID_Ivalues.append(3)  # nu blir 3 I värdets start value på alla byggnader

    for building in enumerate(buildings):
        logResidenceInfo[building[0]].append(building[1].temperature)

    # testHouse = buildings[0]
    # testHouse.a = 1
    # logResidenceInfo[0].append(testHouse.temperature)

    # for building in buildings:
    #    building.tmp_History.append(building.temperature)

    # f  = open("tempLog.txt", "a+")
    # f.write(str(game_layer.game_state.turn))
    # f.write("; ")
    # f.write(str(logResidenceInfo[0][-1]))
    # f.write("; ")
    # f.write(str(game_layer.game_state.current_temp))
    # f.write("; ")
    # if game_layer.game_state.turn > 5:
    #    d = calcCurrentD(logResidenceInfo[0][-5:])
    #    f.write(str(d))
    # f.write("\r")
    # f.close()

    # if state.turn == 30:
    #    print(logResidenceInfo[0])
    # for building in buildings:
    #    building.tmp_History.append(building.temperature)


def getBuildingConstants(building_name):
    valuesDict = {"Apartments": (0.1, 0.3, 0.3), "ModernApartments": (0.1, 0.3, 0.3), "Cabin": (0.1, 0.3, 0.3),
                  "EnvironmentalHouse": (0.1, 0.3, 0.3), "HighRise": (0.1, 0.3, 0.3),
                  "LuxuryResidence": (0.1, 0.3, 0.3)}
    return valuesDict.get(building_name)
if __name__ == "__main__":
    main()
