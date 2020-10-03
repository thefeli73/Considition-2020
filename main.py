# import api
import time
from sys import exit
from game_layer import GameLayer

api_key = "74e3998d-ed3d-4d46-9ea8-6aab2efd8ae3"
# The different map names can be found on considition.com/rules
map_name = "training1"  # TODO: You map choice here. If left empty, the map "training1" will be selected.

game_layer = GameLayer(api_key)
useTestStrategy = False


def main():
    #game_layer.force_end_game()
    game_layer.new_game(map_name)
    print("Starting game: " + game_layer.game_state.game_id)
    game_layer.start_game()
    # exit game after timeout
    start_time = time.time()
    while game_layer.game_state.turn < game_layer.game_state.max_turns:
        take_turn()
        time_diff = time.time() - start_time
        if time_diff > 5:
            game_layer.end_game()
            exit()
    print("Done with game: " + game_layer.game_state.game_id)
    print("Final score was: " + str(game_layer.get_score()["finalScore"]))



def take_turn():
    # TODO Implement your artificial intelligence here.
    # TODO Take one action per turn until the game ends.
    # TODO The following is a short example of how to use the StarterKit
    if not useTestStrategy:
        state = game_layer.game_state
        print("testrunda")
        # messages and errors for console log
        for message in game_layer.game_state.messages:
            print(message)
        for error in game_layer.game_state.errors:
            print("Error: " + error)


    # pre-made test strategy
    # which came with
    # starter kit
    if useTestStrategy:
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


if __name__ == "__main__":
    main()
