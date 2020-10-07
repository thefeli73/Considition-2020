# import api
import time
import sys
from sys import exit
from game_layer import GameLayer
import game_state
import traceback
import random

api_key = "74e3998d-ed3d-4d46-9ea8-6aab2efd8ae3"
# The different map names can be found on considition.com/rules
map_name = "training1"  # TODO: You map choice here. If left empty, the map "training1" will be selected.
game_layer = GameLayer(api_key)
# settings
use_regulator = False
other_upgrade_threshold = 0.25
time_until_run_ends = 90
money_reserve_multiplier = 0


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


def develop_society():
    global state, queue_timeout, available_tiles, money_reserve_multiplier
    queue_reset = 1
    if queue_timeout > 1:
        queue_timeout -= 1

    best_residence = calculate_best_residence()
    best_utility = calculate_best_utility()
    best_upgrade = get_best_upgrade()
    build_residence_score = 0
    build_utility_score = 0
    build_upgrade_score = 0
    # priority scores, 1 = very urgent, 0 = not urgent at all
    if len(state.residences) < 1:
        build_residence_score = 1000
    elif (current_tot_pop() - max_tot_pop() + state.housing_queue) < 0:
        build_residence_score = 0
    elif (current_tot_pop() - max_tot_pop() + state.housing_queue) > 15 and queue_timeout <= 0:
        build_residence_score = 1000
    elif best_residence:
        build_residence_score = best_residence[0] # * (state.housing_queue / (15 * queue_timeout))
    #
    upgrade_residence_score = 0
    #
    if best_utility:
        build_utility_score = best_utility[0]
    #
    if best_upgrade:
        build_upgrade_score = best_upgrade[0]


    decision = [
        ('build_residence', build_residence_score),
        ('upgrade_residence', upgrade_residence_score),
        ('build_utility', build_utility_score),
        ('build_upgrade', build_upgrade_score)
    ]
    def sort_key(e):
        return e[1]
    decision.sort(reverse=True, key=sort_key)
    # print(decision)

    if decision[0][1] >= 0:
        if decision[0][0] == "build_residence":  # build housing
            if best_residence:
                queue_timeout = queue_reset
                return build(best_residence[1])
        if decision[0][0] == "build_utility":  # build utilities
            if best_utility:
                return build_place(best_utility[1], best_utility[2])
        if decision[0][0] == "upgrade_residence":  # upgrade housing
            pass
        if decision[0][0] == "build_upgrade":  # build upgrades
            if random.random() < other_upgrade_threshold:
                for residence in state.residences:
                    if state.available_upgrades[0].name not in residence.effects and (money_reserve_multiplier*3500 < state.funds) and ((total_income() - 6) > 50):
                        game_layer.buy_upgrade((residence.X, residence.Y), state.available_upgrades[0].name)
                        return True
                    if use_regulator and state.available_upgrades[5].name not in residence.effects and (money_reserve_multiplier*1250 < state.funds):
                        game_layer.buy_upgrade((residence.X, residence.Y), state.available_upgrades[5].name)
                        return True
            if best_upgrade:
                game_layer.buy_upgrade((best_upgrade[2].X, best_upgrade[2].Y), best_upgrade[1])
                return True
    return False



def something_needs_attention():
    global building_under_construction, edit_temp, maintain, state, rounds_between_energy

    # check if temp needs adjusting
    edit_temp = (False, 0)
    # check if need for maintenance
    maintain = (False, 0)
    for i in range(len(state.residences)):
        blueprint = game_layer.get_residence_blueprint(state.residences[i].building_name)
        if state.residences[i].health < 40+(max(((blueprint.maintenance_cost- state.funds) / (1+total_income())), 1) * blueprint.decay_rate):
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
            if not state.utilities[building_under_construction[2]].build_progress < 100:
                building_under_construction = None
            return True
        else:
            building_under_construction = None
            return False
    else:
        return False


def max_tot_pop():
    global state
    max_pop = 0
    for residence in state.residences:
        max_pop += game_layer.get_blueprint(residence.building_name).max_pop
    return max_pop


def current_tot_pop():
    global state
    current_pop = 0
    for residence in state.residences:
        current_pop += residence.current_pop
    return current_pop


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
    global state, money_reserve_multiplier

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
            max_happiness = effect.max_happiness_increase * current_pop * rounds_left

            score = max_happiness/10 - co2
            # score = score / upgrade.cost
            best_upgrade.append((score, upgrade.name))

    def sort_key(e):
        return e[0]
    best_upgrade.sort(reverse=True, key=sort_key)
    if not best_upgrade:
        return False
    return best_upgrade[0]


def calculate_best_utility():
    global state, money_reserve_multiplier

    rounds_left = 700 - state.turn
    best_utility = []
    for utility_blueprint in state.available_utility_buildings:
        if state.turn >= utility_blueprint.release_tick and (money_reserve_multiplier*utility_blueprint.cost < state.funds):
            for i in range(len(available_tiles)):
                if isinstance(available_tiles[i], tuple):
                    score = 0
                    cost = utility_blueprint.cost
                    for effect_name in utility_blueprint.effects:
                        effect = game_layer.get_effect(effect_name)
                        affected_people = tile_score(available_tiles[i], effect.radius)[0]
                        affected_buildings = tile_score(available_tiles[i], effect.radius)[1]
                        cost -= effect.building_income_increase * rounds_left
                        happiness_increase = affected_people * effect.max_happiness_increase * rounds_left
                        co2 = affected_people * effect.co2_per_pop_increase * rounds_left - effect.mwh_production * affected_buildings
                        score = happiness_increase / 10 - co2
                    # score = score / cost
                    best_utility.append((score, utility_blueprint.building_name, i))



    def sort_key(e):
        return e[0]
    best_utility.sort(reverse=True, key=sort_key)
    if not best_utility:
        return False
    return best_utility[0]


def calculate_best_residence():
    global state, money_reserve_multiplier

    rounds_left = 700 - state.turn
    best_residence = []
    for residence_blueprint in state.available_residence_buildings:
        if state.turn >= residence_blueprint.release_tick and (money_reserve_multiplier*residence_blueprint.cost < state.funds):
            average_outdoor_temp = (state.max_temp - state.min_temp)/2
            average_heating_energy = ((0 - 0.04 * residence_blueprint.max_pop + (21 - average_outdoor_temp) * residence_blueprint.emissivity) / 0.75)
            lifetime_energy = (residence_blueprint.base_energy_need + average_heating_energy) * rounds_left

            co2 = 0.03 * residence_blueprint.max_pop * rounds_left + residence_blueprint.co2_cost + (0.1 * lifetime_energy / 1000)
            max_happiness = residence_blueprint.max_happiness * residence_blueprint.max_pop * rounds_left

            score = residence_blueprint.max_pop*15 + max_happiness/10 - co2
            # score = score / residence_blueprint.cost
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


def tile_score(tile, radius):
    global state
    affected_people = 0
    affected_buildings = 0
    # send back # of max people in radius
    for residence in state.residences:
        delta_x = abs(tile[0] - residence.X)
        delta_y = abs(tile[1] - residence.Y)
        distance = delta_x + delta_y
        if (distance <= radius) and not ("Park", "WindTurbine", "Mall.2" in residence.effects):
            affected_people += residence.current_pop
            affected_buildings += 1
    return affected_people, affected_buildings


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


def build_place(structure, i):
    global building_under_construction, rounds_between_energy, state
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
                        return True
            return False


def build(structure):
    global building_under_construction, rounds_between_energy, state
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
                            return True
            return False


if __name__ == "__main__":
    main()
