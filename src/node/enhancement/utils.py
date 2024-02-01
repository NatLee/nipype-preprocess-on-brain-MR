import numpy as np

from scipy.signal import medfilt

def denoise(volume:np.ndarray, kernel_size=3):
    return medfilt(volume, kernel_size)

def rescale_intensity(volume:np.ndarray, percentils=[0.5, 99.5], bins_num=256) -> np.ndarray:
    obj_volume = volume[np.where(volume > 0)]
    min_value = np.percentile(obj_volume, percentils[0])
    max_value = np.percentile(obj_volume, percentils[1])

    if bins_num == 0:
        obj_volume = (obj_volume - min_value) / (max_value - min_value).astype(np.float32)
    else:
        obj_volume = np.round((obj_volume - min_value) / (max_value - min_value) * (bins_num - 1))
        obj_volume[np.where(obj_volume < 1)] = 1
        obj_volume[np.where(obj_volume > (bins_num - 1))] = bins_num - 1

    volume = volume.astype(obj_volume.dtype)
    volume[np.where(volume > 0)] = obj_volume

    return volume

def equalize_hist(volume:np.ndarray, bins_num=256) -> np.ndarray:
    obj_volume = volume[np.where(volume > 0)]
    #hist, bins = np.histogram(obj_volume, bins_num, normed=True)
    hist, bins = np.histogram(obj_volume, bins_num)
    cdf = hist.cumsum()
    cdf = (bins_num - 1) * cdf / cdf[-1]

    obj_volume = np.round(np.interp(obj_volume, bins[:-1], cdf)).astype(obj_volume.dtype)
    volume[np.where(volume > 0)] = obj_volume
    return volume
