import main
number_of_launches = 4
result_list = []
for i in range(number_of_launches):
    result_list.append(main.main())
for result in result_list:
    print("Game " + result[0] + " had a score of: " + str(result[1]))
input("Press Enter to exit")