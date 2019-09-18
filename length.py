import csv
"""
Calculate the Length of csv
"""

def Length(filename):
    with open(filename) as file:
        data = csv.reader(file)
        next(data)
        all_data = list(data)
        length = len(all_data)
        print("Length: ", length)
        count = 0
        for _data in all_data:
            if _data[3] == '100.00%' or float(_data[4]) < 1:
                count += 1
        return length - count

filename = '/Users/lipenghao/Desktop/Apriori-master/support=20%,confidence=30%to90%/support=20%,confidence=90%.csv'
print(Length(filename))
