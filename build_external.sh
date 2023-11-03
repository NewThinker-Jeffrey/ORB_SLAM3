#!/usr/bin/env bash

PREFIX=$1
my_dir=$(cd $(dirname $0) && pwd)

if [ "${ORB_SLAM3_dir}" == "" ]; then
  ORB_SLAM3_dir=$my_dir
  # ORB_SLAM3_dir=$my_dir/src/ORB_SLAM3
fi

if ! [ -f $ORB_SLAM3_dir/Vocabulary/ORBvoc.txt.tar.gz && -f $ORB_SLAM3_dir/CMakeLists.txt ]; then
  echo "Can't find ORB_SLAM3 source code under '$ORB_SLAM3_dir'!!"
  echo "Please set the environment variable first:"
  echo "    - export ORB_SLAM3_dir=/path/to/your/ORB_SLAM3"
  exit 1
fi

echo "ORB_SLAM3_dir: $ORB_SLAM3_dir"

if [ "${PREFIX}" == "" ]; then
  PREFIX=$my_dir
else
  if [ -d ${PREFIX} ]; then
    # get the absolute path
    PREFIX=$(cd ${PREFIX} && pwd)
  else
    echo "Bad input: '${PREFIX}' is not a folder! Please create the folder and try again."
    exit 1
  fi
fi

echo
echo
echo "Build and install ORB_SLAM3 in '${PREFIX}'"
echo
echo


echo "Configuring and building Thirdparty/DBoW2 ..."
mkdir -p ${PREFIX}/Thirdparty/DBoW2/build
cd ${PREFIX}/Thirdparty/DBoW2/build
cmake $ORB_SLAM3_dir/Thirdparty/DBoW2 -DCMAKE_BUILD_TYPE=Release -DDBoW2_INSTALL_DIR=${PREFIX}/Thirdparty/DBoW2
make -j

echo "Configuring and building Thirdparty/g2o ..."
mkdir -p ${PREFIX}/Thirdparty/g2o/build
cd ${PREFIX}/Thirdparty/g2o/build
cmake $ORB_SLAM3_dir/Thirdparty/g2o -DCMAKE_BUILD_TYPE=Release -Dg2o_INSTALL_DIR=${PREFIX}/Thirdparty/g2o
make -j

echo "Configuring and building Thirdparty/Sophus ..."
mkdir -p ${PREFIX}/Thirdparty/Sophus/build
cd ${PREFIX}/Thirdparty/Sophus/build
cmake $ORB_SLAM3_dir/Thirdparty/Sophus -DCMAKE_BUILD_TYPE=Release -DSophus_INSTALL_DIR=${PREFIX}/Thirdparty/Sophus
make -j

echo "Uncompress vocabulary ..."
mkdir -p ${PREFIX}/Vocabulary
cd ${PREFIX}/Vocabulary
cp $ORB_SLAM3_dir/Vocabulary/ORBvoc.txt.tar.gz .
tar -xf ORBvoc.txt.tar.gz

echo "Configuring and building ORB_SLAM3 ..."
mkdir -p ${PREFIX}/build
cd ${PREFIX}/build
cmake $ORB_SLAM3_dir -DCMAKE_BUILD_TYPE=Release -DORB_SLAM3_INSTALL_DIR=${PREFIX}
# make -j4
make -j
