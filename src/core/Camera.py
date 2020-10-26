
from typing import Dict
import numpy as np
import cv2

class Intrinsic(object):
    def __init__(self) -> None:
        self.mat = np.eye(3)
        self._update()
        return
    
    def _update(self) -> None:
        self.fx = self.mat[0, 0]
        self.fy = self.mat[1, 1]
        self.cx = self.mat[0, 2]
        self.cy = self.mat[1, 2]
        self.s  = self.mat[0, 1]
        return

    def set_mat(self, mat: np.ndarray) -> None:
        self.mat = mat
        self._update()
        return

class Extrinsic(object):
    def __init__(self) -> None:
        self.mat   = np.eye(4)
        self.mat_R = np.eye(4)
        self.mat_T = np.eye(4)
        self._update()
        return
    
    def _update(self) -> None:
        self.mat_R[:3, :3] = self.mat[:3, :3]
        self.mat_T[:3,  3] = self.mat[:3,  3]
        self.rvec = cv2.Rodrigues(self.mat[:3, :3])[0].flatten()
        self.tvec = self.mat[:3,  3].flatten()
        return

    def set_mat(self, mat: np.ndarray) -> None:
        self.mat = mat
        self._update()
        return

    def set_vecs(self, rvec: np.ndarray=np.zeros(3), tvec: np.ndarray=np.zeros(3)) -> None:
        self.mat_R[:3, :3] = cv2.Rodrigues(rvec)[0]
        self.mat_T[:3,  3] = tvec.reshape((-1, 1))
        self.mat = self.mat_T @ self.mat_R
        self._update()
        return

class Distortion(object):
    def __init__(self):
        self.mat = np.zeros(5)
        return


class Camera(object):
    def __init__(self) -> None:
        self.intrin  = Intrinsic()
        self.extrin  = Extrinsic()
        self.distort = Distortion()
        return

    def set_image_shape(self, height: int, width: int):
        class Shape:
            height = 0
            width  = 0
        self.shape_image = Shape
        self.shape_image.height = height
        self.shape_image.width  = width
        return

    def set_camera_pars(self, camera_pars: Dict) -> None:
        self.intrin.set_mat(np.array(camera_pars["intrin"]))
        self.extrin.set_mat(np.array(camera_pars["extrin"]))
        return

    def to_modelview_gl(self) -> np.ndarray:
        """
        """
        Rx = np.diag(np.array([1, -1, -1, 1]))
        modelview = Rx @ self.extrin.mat
        return modelview.T.flatten()

    def to_projection_gl(self, near_plane: float=0.01, far_plane: float=100.0) -> np.ndarray:
        P = np.zeros(shape=(4, 4), dtype=np.float32)
        
        P[0, 0] = 2 * self.intrin.fx / self.shape_image.width
        P[1, 1] = 2 * self.intrin.fy / self.shape_image.height
        P[2, 0] = 1 - 2 *  self.intrin.cx / self.shape_image.width
        P[2, 1] = 2 *  self.intrin.cy / self.shape_image.height - 1
        P[2, 2] = -(far_plane + near_plane) / (far_plane - near_plane)
        P[2, 3] = -1.0
        P[3, 2] = - (2 * far_plane * near_plane) / (far_plane - near_plane)

        return P.T.flatten()


if __name__ == "__main__":
    cam = Camera()
    import  json
    with open("/home/veily/桌面/LiGan/Pose6dSolver-pyqt-gl/姿态测量/results_calib/cam_1/camera_pars.json") as f:
        data = json.load(f)
        cam.set_camera_pars(data)
    cam.set_image_shape(480, 640)
    M = cam.to_modelview_gl()
    P = cam.to_projection_gl()
    print ()