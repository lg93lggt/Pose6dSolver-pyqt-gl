

import argparse
import os
import sys
from typing import Tuple

import cv2
import numpy as np

sys.path.append("..")
from core import geometry as geo
from core import FileIO 


class CalibratorByDLT(object):
    def __init__(self, n_points=8, unit_length_meter=1) -> None:
        self.unit_length_meter = unit_length_meter
        self.n_points = n_points
        if   self.n_points == 8:
            self.points3d_unit_cube = np.array(
                [[0, 0, 0],
                 [1, 0, 0],
                 [1, 1, 0],
                 [0, 1, 0],
                 [0, 0, 1],
                 [1, 0, 1],
                 [1, 1, 1],
                 [0, 1, 1]],
                dtype=np.float
            )
        elif self.n_points == 7:
            self.points3d_unit_cube = np.array(
                [[0, 0, 0],
                 [1, 0, 0],
                 [1, 1, 0],
                #[0, 1, 0],
                 [0, 0, 1],
                 [1, 0, 1],
                 [1, 1, 1],
                 [0, 1, 1]],
                dtype=np.float
            )
        elif self.n_points == 6:
            self.points3d_unit_cube = np.array(
                [[0, 0, 0],
                 [1, 0, 0],
                #[1, 1, 0],
                #[0, 1, 0],
                 [0, 0, 1],
                 [1, 0, 1],
                 [1, 1, 1],
                 [0, 1, 1]],
                dtype=np.float
            )
        self.points3d_real = self.points3d_unit_cube * self.unit_length_meter
        
        self.solve_perspective_mat_3d_to_2d = geo.solve_projection_mat_3d_to_2d
        self.decomposition_intrin_extrin_from_projection_mat = geo.decomposition_intrin_extrin_from_projection_mat
        self.R2r = geo.R_to_r
        self.T2t = geo.T_to_t
        return

    def set_points3d(self, points3d: np.ndarray):
        self.points3d_real = points3d 
        return

    def set_points2d(self, points2d: np.ndarray):
        self.points2d_obj = points2d
        return
    
    def solve(self):
        L_ = self.solve_perspective_mat_3d_to_2d(self.points3d_real, self.points2d_obj, "ols")
        lamda = 1/np.linalg.norm(L_[2, :3])
        #L_ = L / lamda
        cx = lamda**2 * L_[0, :3].T @ L_[2, :3]
        cy = lamda**2 * L_[1, :3].T @ L_[2, :3]
        fx = lamda**2 * np.linalg.norm(np.cross(L_[0, :3], L_[2, :3]))
        fy = lamda**2 * np.linalg.norm(np.cross(L_[1, :3], L_[2, :3]))

        tx = lamda * (L_[0, 3] - cx) / fx
        ty = lamda * (L_[1, 3] - cy) / fy
        tz = lamda 

        r1 = lamda * (L_[0, :3] - cx * L_[2, :3]) / fx
        r2 = lamda * (L_[1, :3] - cy * L_[2, :3]) / fy
        r3 = np.cross(r1, r2)
        
        K = np.array([
            [fx,  0, cx, 0], 
            [ 0, fy, cy, 0],
            [ 0,  0,  1, 0],
            [ 0,  0,  0, 1]
        ])
        R = np.hstack([r1, r2, r3]).reshape((3, 3))
        RT = np.eye(4)
        RT[:3, :3] = R
        RT[:3,  3] = np.array([tx, ty, tz])

        [mat_intrin, mat_extrin] = self.decomposition_intrin_extrin_from_projection_mat(L)
        print( RT / RT[-1, -1])
        print(mat_extrin)
        rvec = self.R2r(mat_extrin)
        tvec = self.T2t(mat_extrin)
        self.camera_pars = {}
        self.camera_pars["intrin"] = mat_intrin
        self.camera_pars["extrin"] = mat_extrin
        self.camera_pars["rvec"]   = rvec
        self.camera_pars["tvec"]   = tvec
        return

    def outprint(self):
        print()
        print("intrin:\n", self.camera_pars["intrin"])
        print("extrin:\n", self.camera_pars["extrin"])
        print("rvec:\n", self.camera_pars["rvec"])
        print("tvec:\n", self.camera_pars["tvec"])
        print()
        return
    
    def run(self):
        print("\n开始标定...")
        self.solve()
        self.outprint()
        return

if __name__ == "__main__":
    
    fio = FileIO.FileIO()
    fio.load_project_from_filedir("C:/Users/Li/work/Pose6dSolver-pyqt-gl/姿态测量")
    p2d = fio.load_points2d("calib", 0, 0, 0)
    p3d = fio.loadz_points3d("calib", 0, 0, 0)["array"]
    calibrator = CalibratorByDLT()
    calibrator.set_points3d(p3d)
    calibrator.set_points2d(p2d)
    calibrator.run()
    calibrator.camera_pars
    
    

