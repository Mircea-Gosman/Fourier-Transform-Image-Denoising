import time
import numpy as np

import utils as Utils
import fourier_operations as Fourier


def run_fast_mode(image):
    f_transform = Fourier.fast_transform(image)
    Utils.plot_transform(image, f_transform)


def denoise(image, FREQ_THRESH=[np.pi * 0.1,  np.pi * 0.1]):
    f_transform        = Fourier.fast_transform(image)     
    filtered_transform = Fourier.filter_frequencies(f_transform, FREQ_THRESH, scheme="high_frequency")
    inverse_transform  = Fourier.fast_transform(filtered_transform, inverse=True)
    Utils.plot_images([image, inverse_transform], [1, 2])


def compress(image, factors = [ 0., 0.19, 0.38, 0.57, 0.76, 0.95 ], scheme="high_frequency"):
    f_transform  = Fourier.fast_transform(image)
    c_transforms = Fourier.compress(f_transform, factors, scheme)
    i_transforms = [ Fourier.fast_transform(c_transforms[i], inverse=True) for i in range(len(factors)) ]
    Utils.plot_images(i_transforms, [2, 3])


def plot(num_iterations=10, sizes=[2**5, 2**6, 2**7, 2**8,2**9,2**10]):
    np_times            = Utils.runtime(num_iterations, sizes)
    means               = np.average(np_times, axis=-1)
    standard_deviations = np.std(np_times, axis=-1)
    Utils.plot_statistics(sizes, means, standard_deviations, labels=["Naive", "Fast"])


def accuracy(image, TOLERANCE=-12):
    # Smaller Toy Data
    # image = np.array([
    #     [[1, 1, 1], [20,20,20] , [5,5,5], [1, 1, 1], [20,20,20] , [5,5,5], [10, 10, 10] , [7,7,7]],
    #     [[2, 2, 2], [10, 10, 10] , [7,7,7], [1, 1, 1], [20,20,20] , [5,5,5], [10, 10, 10] , [7,7,7]],
    # ])[:,:,0]

    # Results
    naive_transform = Fourier.normal_transform(image)
    fast_transform = Fourier.fast_transform(image)
    inverse_fast_transform = Fourier.fast_transform(fast_transform, inverse=True)

    # Numpy Results
    print("Checking Numpy Transforms...")
    np_fft = np.fft.fft2(image, axes=(0, 1))
    np_ifft = np.fft.ifft2(np_fft, axes=(0, 1))
    
    # RMSs & Tolerances
    rms = lambda y, z: np.sqrt(np.mean((y - z)**2))
    naive_tol = np.allclose(naive_transform, np_fft, rtol=0, atol=np.exp(TOLERANCE))
    fast_tol = np.allclose(fast_transform, np_fft, rtol=0, atol=np.exp(TOLERANCE))
    fast_inv_tol = np.allclose(naive_transform, np_fft, rtol=0, atol=np.exp(TOLERANCE))

    # Display
    print("Root mean squared errors between our transforms & Numpy's:")
    print(f"\tNaive transform is\t\t{rms(naive_transform, np_fft)}\t\t| Within 10^{TOLERANCE} tolerance:\t{naive_tol}")
    print(f"\tFast transform is\t\t{rms(fast_transform, np_fft)}\t\t| Within 10^{TOLERANCE} tolerance:\t{fast_tol}")
    print(f"\tFast inverse transform is\t{rms(inverse_fast_transform, np_ifft)}\t\t| Within 10^{TOLERANCE} tolerance:\t{fast_inv_tol}")


def find_FFT_REC_TRESHOLD(image):
    vals = np.concatenate((np.array([1]), np.array([ 10 * n for n in range(1, 25)])))

    times = []
    res = []
    np_res = []

    for val in vals:
        start = time.time()
        res.append(Fourier.fast_transform(image,FFT_REC_THRESHOLD=val))
        times.append(time.time() - start)
        np_res.append(np.fft.fft2(image))

    res_n = np.array(res)
    np_res_n = np.array(np_res)
    rms = lambda y, z: np.sqrt(np.mean((y - z)**2))
    acc = [rms(res_n[i], np_res_n[i]) for i in range(len(vals))]
    
    Utils.plot_statistics(vals, [acc], [np.zeros(vals.shape), np.zeros(vals.shape)], labels=["Accuracy"], axis_titles=["Threshold Values", "RMS"])
    Utils.plot_statistics(vals, [times], [np.zeros(vals.shape), np.zeros(vals.shape)], labels=["Runtime"], axis_titles=["Threshold Values", "Runtime (s)"])
 
    
if __name__ == "__main__":
    args = Utils.check_CLI()

    if args["mode"] == 1:
        run_fast_mode(args["image"])
    if args["mode"] == 2:
        denoise(args["image"])
    if args["mode"] == 3:
        compress(args["image"])
    if args["mode"] == 4:
        plot()
    if args["mode"] == 5:
        accuracy(args["image"])
    if args["mode"] == 6:
        find_FFT_REC_TRESHOLD(args["image"])