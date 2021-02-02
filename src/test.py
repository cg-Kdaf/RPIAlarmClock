from os import system as os_system


def is_computer_on(host="kdaf"):
    response = os_system("ping -A -q -w 1 " + host + '> /dev/null')
    print(response)
    return (int(response) == 0)


print(is_computer_on())
