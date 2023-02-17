#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""

input: 

arg 1: /path/to/KITTI_odometry/sequences   (00  01  02  03  ...)
arg 2: /path/to/KITTI_odometry/groundtruth/poses   (00.txt  01.txt ...)
arg 3: /path/to/KITTI_raw_data_extract  (2011_09_26  2011_09_30 ...)

output:





Sequence to rawdata

Nr.     Sequence name     Start   End
---------------------------------------
00: 2011_10_03_drive_0027 000000 004540
01: 2011_10_03_drive_0042 000000 001100
02: 2011_10_03_drive_0034 000000 004660
03: 2011_09_26_drive_0067 000000 000800
04: 2011_09_30_drive_0016 000000 000270
05: 2011_09_30_drive_0018 000000 002760
06: 2011_09_30_drive_0020 000000 001100
07: 2011_09_30_drive_0027 000000 001100
08: 2011_09_30_drive_0028 001100 005170
09: 2011_09_30_drive_0033 000000 001590
10: 2011_09_30_drive_0034 000000 001200

"""

import os
import sys
import time
from datetime import datetime


KITTI_raw_data_extract_dir = "/data3/dataset/outdoor/KITTI_raw_data_extract"
KITTI_raw_data_sync_dir = "/data3/dataset/outdoor/KITTI_raw_data_extract"

sequence_names = [
    "00",
    "01",
    "02",
    # "03",
    "04",
    "05",
    "06",
    "07",
    "08",
    "09",
    "10",
]

sequence_to_rawdata = {
    "00": ("2011_10_03_drive_0027", 0, 4540),
    "01": ("2011_10_03_drive_0042", 0, 1100),
    "02": ("2011_10_03_drive_0034", 0, 4660),
    # "03": ("2011_09_26_drive_0067", 0, 800),
    "04": ("2011_09_30_drive_0016", 0, 270),
    "05": ("2011_09_30_drive_0018", 0, 2760),
    "06": ("2011_09_30_drive_0020", 0, 1100),
    "07": ("2011_09_30_drive_0027", 0, 1100),
    "08": ("2011_09_30_drive_0028", 1100, 5170),
    "09": ("2011_09_30_drive_0033", 0, 1590),
    "10": ("2011_09_30_drive_0034", 0, 1200),
}

def convert_to_ts(kitti_time_str):
    # "2011-09-30 12:08:25.922852150"
    # timearray = time.strptime(kitti_time_str, "%Y-%m-%d %H:%M:%S.%f")
    timearray = time.strptime(kitti_time_str[:-10], "%Y-%m-%d %H:%M:%S")
    return int(time.mktime(timearray)) * 1000000000 + int(kitti_time_str[-9:])

def load_timestamps(kitti_timestamps_file):
    ts_list = []
    with open(kitti_timestamps_file, "r") as stream:
        for line in stream:
            line = line.strip()
            if not line:
                continue
            ts_list.append(convert_to_ts(line))
    return ts_list

def load_imu_from_oxts_file(oxts_file):
    with open(oxts_file, "r") as stream:
        for line in stream:
            line = line.strip()
            if line:
                entries = line.split()
                ax = float(entries[11])
                ay = float(entries[12])
                az = float(entries[13])
                wx = float(entries[17])
                wy = float(entries[18])
                wz = float(entries[19])
                return wx, wy, wz, ax, ay, az

def get_rawdata_dir_for_sequence(sequence_name):
    subdir = sequence_to_rawdata[sequence_name][0] + "_extract"
    datedir = subdir[0:len("2011_09_30")]
    fulldir = os.path.join(KITTI_raw_data_extract_dir, datedir, subdir)
    return fulldir

def get_sync_rawdata_dir_for_sequence(sequence_name):
    subdir = sequence_to_rawdata[sequence_name][0] + "_sync"
    datedir = subdir[0:len("2011_09_30")]
    fulldir = os.path.join(KITTI_raw_data_sync_dir, datedir, subdir)
    return fulldir


def get_rawdata_dir_for_sequence(sequence_name):
    subdir = sequence_to_rawdata[sequence_name][0] + "_extract"
    datedir = subdir[0:len("2011_09_30")]
    fulldir = os.path.join(KITTI_raw_data_extract_dir, datedir, subdir)
    return fulldir

def imu_kitti_to_tum(sequence_name, savedir):
    rawdata_dir = get_rawdata_dir_for_sequence(sequence_name)
    sync_rawdata_dir = get_sync_rawdata_dir_for_sequence(sequence_name)
    start_frame = sequence_to_rawdata[sequence_name][1]
    end_frame = sequence_to_rawdata[sequence_name][2]
    img_ts_file = os.path.join(sync_rawdata_dir, "image_00", "timestamps.txt")
    img_ts_list = load_timestamps(img_ts_file)
    start_frame_ts = img_ts_list[start_frame]
    end_frame_ts = img_ts_list[end_frame]

    imu_ts_file = os.path.join(rawdata_dir, "oxts", "timestamps.txt")
    imu_ts_list = load_timestamps(imu_ts_file)
    imu_data_dir = os.path.join(rawdata_dir, "oxts", "data")
    imu_data = []
    items = os.listdir(imu_data_dir)
    items.sort()
    for item in items:
        if not item.endswith(".txt"):
            continue
        abs_item = os.path.join(imu_data_dir, item)
        idx = int(item[:-4])
        ts = imu_ts_list[idx]
        if ts < start_frame_ts or ts > end_frame_ts:
            continue
        wx, wy, wz, ax, ay, az = load_imu_from_oxts_file(abs_item)
        print("read imu data {}: {}".format(item, (ts, wx, wy, wz, ax, ay, az)))
        imu_data.append((ts, wx, wy, wz, ax, ay, az))

    with open(os.path.join(savedir, "{}_imu.csv".format(sequence_name)), "w") as stream:
        stream.write("#timestamp [ns],w_RS_S_x [rad s^-1],w_RS_S_y [rad s^-1],w_RS_S_z [rad s^-1],a_RS_S_x [m s^-2],a_RS_S_y [m s^-2],a_RS_S_z [m s^-2]\n")
        for ts, wx, wy, wz, ax, ay, az in imu_data:
            line = "{ts},{wx},{wy},{wz},{ax},{ay},{az}".format(
                ts = ts - start_frame_ts,
                wx = wx, wy = wy, wz = wz,
                ax = ax, ay = ay, az = az)
            print("write: {}".format(line))
            stream.write("{}\n".format(line))

if __name__ == "__main__":
    output_dir = "KITTI_odometry_imu_generated"
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    for sequence_name in sequence_names:
        imu_kitti_to_tum(sequence_name, output_dir)




