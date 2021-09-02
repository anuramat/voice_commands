import json
import re
import copy

def parse(text, name_to_cmd):
    # TODO обсудить обработку ошибок
    # TODO сделать вариант для чисел больше 10 и дробей в read_number()
    # NOTE в этих командах не должно быть чисел в начале, иначе проблемы

    numbers_dict = set('одна две три четыре пять шесть семь восемь девять десять'.split())
    
    words = text.split() # разбитый на слова вход
    result = [] # список json-ов с командами, который возвращается в конце функции
    
    reading_number = False
    number_splitstring = []

    reading_cmd = False
    pos_names = []
    
    for word in words:

        # команды задержки
        if not reading_cmd and word in numbers_dict:
            if len(result) == 0:
                reading_number = False
                number_splitstring = []
                raise ValueError('некуда добавлять задержку')

            reading_number = True
            number_splitstring.append(word)
            continue

        if reading_number and word == 'секунд':
            number = read_number(number_splitstring)
            result[-1]['delay'] = number # TODO 
            reading_number = False
            number_splitstring = []
            continue
        
        # обычные команды
        if not pos_names:
            pos_names = list(name.split() for name in name_to_cmd.keys())
            pos_cmds = list(name_to_cmd.values())
            reading_cmd = True

        pos_names, pos_cmds = zip(*((name, cmd) for name, cmd in zip(pos_names, pos_cmds) if word==name[0]))
        
        for name in pos_names:
            del name[0]

        if len(pos_names) == 0:
            pos_names = []
            reading_cmd = False
            raise ValueError('команда не найдена')

        if len(pos_names) == 1 and len(pos_names[0]) == 0:
            result.append(pos_cmds[0])
            pos_names = []
            reading_cmd = False

    return result

def read_number(words):
    numbers_dict = 'одна две три четыре пять шесть семь восемь девять десять'.split()
    return (1 + numbers_dict.index(words[0])) * 1000 # ms

if __name__ == '__main__':
    test = 'едь вперёд выключи свет поверни налево шесть секунд едь назад пять секунд'
    print(f'<<< {test}')
    print()
    print(f'>>> {parse(test)}')