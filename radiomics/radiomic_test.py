features = [[1,2,3],
            [4,5,6],
            [7,8,9]]

labels = [0,0,1]

collection = list(zip(features, labels))


print(collection)
print(*zip(*collection))