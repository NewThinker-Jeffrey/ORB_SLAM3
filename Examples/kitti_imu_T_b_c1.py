#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
import numpy


KITTI_raw_data_extract_dir = "/data3/dataset/outdoor/KITTI_raw_data_extract"

sequence_to_rawdata = {
    "00-02": "2011_10_03",
    "03": "2011_09_26",
    "04-12": "2011_09_30"
}

def load_T_velo_imu(calib_imu_to_velo_txt):
    R = None
    T = None
    print(">>> {}".format(calib_imu_to_velo_txt))
    with open(calib_imu_to_velo_txt, "r") as stream:
        for line in stream:
            line = line.strip()
            if not line:
                continue
            if line.startswith("R:"):
                print("R-line: {}".format(line[2:].strip()))
                R = numpy.mat(numpy.array(map(float, line[2:].strip().split())).reshape(3,3))
                # or R = R.T?
                print("R:\n{}".format(R))
            elif line.startswith("T:"):
                print("T-line: {}".format(line[2:].strip()))
                T = numpy.mat(numpy.array(map(float, line[2:].strip().split())).reshape(3,1))
                print("T':\n{}".format(T.T))
    mat = numpy.mat(numpy.identity(4))
    mat[0:3, 0:3] = R
    mat[0:3, 3:4] = T
    print("mat:\n{}".format(mat))
    print(list(numpy.array(mat).reshape(1,16)[0]))
    return mat


def load_T_cam_velo(calib_velo_to_cam_txt):
    return load_T_velo_imu(calib_velo_to_cam_txt)

def load_T_b_c1(rawdata_dir):
    T_v_i = load_T_velo_imu(os.path.join(rawdata_dir, "calib_imu_to_velo.txt"))
    T_c_v = load_T_cam_velo(os.path.join(rawdata_dir, "calib_velo_to_cam.txt"))
    T_c_i = T_c_v * T_v_i
    T_b_c1 = T_c_i.I
    return T_b_c1


if __name__ == "__main__":
    sequence_to_T_b_c1 = {}
    for sequence, datedir in sequence_to_rawdata.items():
        rawdata_dir = os.path.join(KITTI_raw_data_extract_dir, datedir)
        T_b_c1 = load_T_b_c1(rawdata_dir)
        sequence_to_T_b_c1 [sequence] = T_b_c1

    for sequence, T_b_c1 in sequence_to_T_b_c1.items():
        print("*** T_b_c1 for sequence {} ***".format(sequence))
        print(list(numpy.array(T_b_c1).reshape(1,16)[0]))




