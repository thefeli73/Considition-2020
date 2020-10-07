import main
import clearGames
from multiprocessing import Pool

proc_running = 4  # MAX 4!!!


def run_main(n):
    result = main.main()
    return result


def launch(list):
    for result in list:
        print("Game " + result[0] + " had a score of: " + str(result[1]))
    input("Press Enter to exit")


if __name__ == '__main__':
    clearGames.clear_it()
    with Pool(proc_running) as p:
        results = p.map(run_main, range(proc_running))
    launch(results)
