import h5py
import sys

def check_hdf5(file_path_high, file_path_temp):
    try:
        f_high = h5py.File(file_path_high, 'r')
        f_temp = h5py.File(file_path_temp, 'r')
        print("High Temp T:", f_high['NH3']['T'][:])
        print("High Temp log(P):", f_high['NH3']['log(P)'][:])
        print("Temp T:", f_temp['N2O']['T'][:])
        print("Temp log(P):", f_temp['N2O']['log(P)'][:])
    except Exception as e:
        print(e)

if __name__ == "__main__":
    check_hdf5('/home/wsldasan/POSEIDON/inputs/opacity/Opacity_database_v1.3.hdf5', '/home/wsldasan/POSEIDON/inputs/opacity/Opacity_database_0.01cm-1_Temperate.hdf5')
