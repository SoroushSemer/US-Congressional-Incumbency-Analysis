import numpy as np
import multiprocessing as mp

# define a function for the calculation
def square_me(num):
        result = int(np.square(num))
        return(result)


if __name__ == '__main__':
    # spawn a pool of parallel workers
    p = mp.Pool(processes=2)

    # using a pool of 40 parallel workers, loop over the values of 1 through 100 and apply the math function to each
    # using p.apply_async to enable the workers to work in parallel
    values = []
    for num in range(1,101):
            results = p.apply_async(square_me, [num])
            values.append((num, results.get()))

    # close the pool of workers
    p.close()
    print(values)

