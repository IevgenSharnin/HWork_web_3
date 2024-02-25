from time import time

def factorize(*number):
    set_list_wo_remain = []
    for each_number in number:
        list_wo_remain = []
        for each in range (1,each_number+1):
            if each_number%each == 0:
                list_wo_remain.append (each)
        set_list_wo_remain.append (list_wo_remain)
    return set_list_wo_remain 

if __name__ == '__main__':
    start = time()
    a,b,c,d,e = factorize(128, 255, 99999, 10651060, 106510601)
    print (a)
    print (b)
    print (c)
    print (d)
    print (e)
    finish = time()
    print (f'Час роботи: {round(finish - start, 3)} сек')