from multiprocessing import Process
import os, requests


def do_stuff(l):
    print('Got', len(l), 'to go through')
    i = 0
    
    for version in l:
        link = f'http://testversionec.us.wizard101.com/WizPatcher/V_r{version}.WizardDev/Windows/LatestFileList.bin'
        if requests.get(link, headers={'User-Agent': 'Mozilla/5.0'}).status_code == 200:
            print(version)
        i += 1
        
        if i % 100 == 0:
            print(f'{i}/{len(l)} done')

if __name__ == '__main__':
    start = 701821
    end = 710000
    numbers = list(range(start, end))
    all_list = [[] for i in range(16)]
    length = len(all_list)

    i = 0

    while numbers:
        all_list[i].append(numbers.pop(0))
        i = (i + 1) % length

    processes = []
    
    for i, l in enumerate(all_list):
        p = Process(target=do_stuff, args=(l,))
        p.start()
        processes.append(p)
    
    for p in processes:
        p.join()
