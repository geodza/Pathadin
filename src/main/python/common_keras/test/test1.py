from sklearn.model_selection import train_test_split
import numpy as np
if __name__ == '__main__':
    X = ['1', '2', '3', '4']
    Y = [0, 1, 0, 1]
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.5)
    print(X_train)
