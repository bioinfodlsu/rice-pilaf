from bs4 import BeautifulSoup
import re
import _pickle as cPickle
import sys
import argparse


def main(input):

    with open(input) as fp:
        soup = BeautifulSoup(fp, 'html.parser')
        print("Done")

    finalDict = {}

    sources = ["LOC_.*", "OsCMeo.*", "OsAzu.*", "OsKeNa.*", "OsARC.*", "OsPr106.*", "OsMH63.*", "OsIR64.*",
               "OsZS97.*", "OsLima.*", "OsKYG.*", "OsGoSa.*", "OsLiXu.*", "OsLaMu.*", "OsN22.*", "OsNaBo.*"]
    files = ["Nipponbare", "ChaoMeo", "Azucena", "KetanNangka", "ARC10497", "PR106", "Minghui63", "IR64",
             "Zhenshan97", "LIMA", "KhaoYaiGuang", "GobolSail", "LiuXu", "LarhaMugad", "N22", "NatelBoro"]

    for i, j in enumerate(sources):
        source = re.compile(j)

        def getText(inp):
            return inp.split("/")[-1]

        for link in soup.find_all('tr', role="row", style=False):
            tempKeys = []
            value = []
            children = link.findChildren("td")
            for x, child in enumerate(children):
                if x == 0:
                    value = child.a.contents[0]
                if x == 1:
                    continue
                if x == 2:
                    temp = re.findall('href="[A-z\:\/\.0-9\_]+"', str(child))
                    allEntries = list(map(getText, temp))
                    tempKeys = list(filter(source.match, allEntries))
                    break
            for key in tempKeys:
                key = key[:-1]
                if key not in finalDict.keys():
                    finalDict[key] = ""
                finalDict[key] += value

        # print(finalDict)
        print("Done Creating Dictionary")
        print(files[i] + '.pickle')
        with open(files[i] + '.pickle', 'wb') as handle:
            try:
                sys.setrecursionlimit(50000000)
                cPickle.dump(finalDict, handle, protocol=5)
            except cPickle.PicklingError as exc:
                print('Got pickling error: {0}'.format(exc))

        print("Done Writing Pickle")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    args = parser.parse_args()
    main(args.input)
