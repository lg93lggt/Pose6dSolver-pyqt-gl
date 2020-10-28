
import enum
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
        K_tmp = np.array(camera_pars["intrin"])
        self.intrin.set_mat(K_tmp / K_tmp[2, 2])
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


class CAMERA_MOVEMENT(enum.Enum):
    FORWARD  = 1
    BACKWARD = 2
    LEFT     = 3
    RIGHT    = 4
    


import glm
from OpenGL.GLUT import *
class Camera3D:
    def __init__(
        self, 
        position=glm.vec3(0.0, 0.0, 0.0), 
        up=glm.vec3(0.0, 1.0, 0.0), 
        yaw=-90,
        pitch=0,
        front=glm.vec3(0.0, 0.0, -1.0), 
        movement_speed=50, 
        mouse_sensitivity=0.1, 
        zoom=45.0,
        keep_static=False
    ):
        self.position = position
        self.world_up = up
        self.yaw = yaw
        self.pitch = pitch
        self.front = front
        self.movement_speed = movement_speed
        self.mouse_sensitivity = mouse_sensitivity
        self.zoom = zoom
        self.camera_keep_static = keep_static
        self.__update_camera_vectors()

    def get_view_matrix(self):
        self.__update_camera_vectors()
        return glm.lookAt(self.position, self.position + self.front, self.world_up)

    # def process_keyboard(self, delta_time):
    #     if keys["escape"]:
    #         glutLeaveMainLoop()

    #     if keys["w"]:
    #         self.__process_keyboard(CAMERA_MOVEMENT.FORWARD, delta_time)

    #     if keys["s"]:
    #         self.__process_keyboard(CAMERA_MOVEMENT.BACKWARD, delta_time)

    #     if keys["a"]:
    #         self.__process_keyboard(CAMERA_MOVEMENT.LEFT, delta_time)

    #     if keys["d"]:
    #         self.__process_keyboard(CAMERA_MOVEMENT.RIGHT, delta_time)

    # def __process_keyboard(self, direction, deltaTime):
    #     velocity = self.movement_speed * deltaTime
    #     if direction == CAMERA_MOVEMENT.FORWARD:
    #         self.position += self.front * velocity
    #     if direction == CAMERA_MOVEMENT.BACKWARD:
    #         self.position -= self.front * velocity
    #     if direction == CAMERA_MOVEMENT.LEFT:
    #         self.position -= self.right * velocity
    #     if direction == CAMERA_MOVEMENT.RIGHT:
    #         self.position += self.right * velocity

    def process_mouse_movement(self, x_offset, y_offset, constrain_pitch=True):
        x_offset *= self.mouse_sensitivity
        y_offset *= self.mouse_sensitivity

        self.yaw += x_offset
        self.pitch += y_offset

        if constrain_pitch:
            if self.pitch > 89.0:
                self.pitch = 89.0
            if self.pitch < -89.0:
                self.pitch = -89.0

        self.__update_camera_vectors()

    def process_mouse_scroll(self, y_offset):
        if self.zoom >= 1.0 and self.zoom <= 45.0:
            self.zoom -= y_offset
        if self.zoom <= 1.0:
            self.zoom = 1.0
        if self.zoom >= 45.0:
            self.zoom = 45.0

    def __update_camera_vectors(self):
        front = glm.vec3(0)
        front.x = np.cos(glm.radians(self.yaw)) * np.cos(glm.radians(self.pitch))
        front.y = np.sin(glm.radians(self.pitch))
        front.z = np.sin(glm.radians(self.yaw)) * np.cos(glm.radians(self.pitch))
        self.front = glm.normalize(front)

        self.right = glm.normalize(glm.cross(self.front, self.world_up))


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

#     #ifndef CAMERA_H
# #define CAMERA_H

# #include <glad/glad.h>
# #include <glm/glm.hpp>
# #include <glm/gtc/matrix_transform.hpp>

# #include <vector>

# // Defines several possible options for camera movement. Used as abstraction to stay away from window-system specific input methods
# enum Camera_Movement {
#     FORWARD,
#     BACKWARD,
#     LEFT,
#     RIGHT
# };

# // Default camera values
# const float YAW         = -90.0f;
# const float PITCH       =  0.0f;
# const float SPEED       =  2.5f;
# const float SENSITIVITY =  0.1f;
# const float ZOOM        =  45.0f;


# // An abstract camera class that processes input and calculates the corresponding Euler Angles, Vectors and Matrices for use in OpenGL
# class Camera
# {
# public:
#     // camera Attributes
#     glm::vec3 Position;
#     glm::vec3 Front;
#     glm::vec3 Up;
#     glm::vec3 Right;
#     glm::vec3 WorldUp;
#     // euler Angles
#     float Yaw;
#     float Pitch;
#     // camera options
#     float MovementSpeed;
#     float MouseSensitivity;
#     float Zoom;

#     // constructor with vectors
#     Camera(glm::vec3 position = glm::vec3(0.0f, 0.0f, 0.0f), glm::vec3 up = glm::vec3(0.0f, 1.0f, 0.0f), float yaw = YAW, float pitch = PITCH) : Front(glm::vec3(0.0f, 0.0f, -1.0f)), MovementSpeed(SPEED), MouseSensitivity(SENSITIVITY), Zoom(ZOOM)
#     {
#         Position = position;
#         WorldUp = up;
#         Yaw = yaw;
#         Pitch = pitch;
#         updateCameraVectors();
#     }
#     // constructor with scalar values
#     Camera(float posX, float posY, float posZ, float upX, float upY, float upZ, float yaw, float pitch) : Front(glm::vec3(0.0f, 0.0f, -1.0f)), MovementSpeed(SPEED), MouseSensitivity(SENSITIVITY), Zoom(ZOOM)
#     {
#         Position = glm::vec3(posX, posY, posZ);
#         WorldUp = glm::vec3(upX, upY, upZ);
#         Yaw = yaw;
#         Pitch = pitch;
#         updateCameraVectors();
#     }

#     // returns the view matrix calculated using Euler Angles and the LookAt Matrix
#     glm::mat4 GetViewMatrix()
#     {
#         return glm::lookAt(Position, Position + Front, Up);
#     }

#     // processes input received from any keyboard-like input system. Accepts input parameter in the form of camera defined ENUM (to abstract it from windowing systems)
#     void ProcessKeyboard(Camera_Movement direction, float deltaTime)
#     {
#         float velocity = MovementSpeed * deltaTime;
#         if (direction == FORWARD)
#             Position += Front * velocity;
#         if (direction == BACKWARD)
#             Position -= Front * velocity;
#         if (direction == LEFT)
#             Position -= Right * velocity;
#         if (direction == RIGHT)
#             Position += Right * velocity;
#     }

#     // processes input received from a mouse input system. Expects the offset value in both the x and y direction.
#     void ProcessMouseMovement(float xoffset, float yoffset, GLboolean constrainPitch = true)
#     {
#         xoffset *= MouseSensitivity;
#         yoffset *= MouseSensitivity;

#         Yaw   += xoffset;
#         Pitch += yoffset;

#         // make sure that when pitch is out of bounds, screen doesn't get flipped
#         if (constrainPitch)
#         {
#             if (Pitch > 89.0f)
#                 Pitch = 89.0f;
#             if (Pitch < -89.0f)
#                 Pitch = -89.0f;
#         }

#         // update Front, Right and Up Vectors using the updated Euler angles
#         updateCameraVectors();
#     }

#     // processes input received from a mouse scroll-wheel event. Only requires input on the vertical wheel-axis
#     void ProcessMouseScroll(float yoffset)
#     {
#         Zoom -= (float)yoffset;
#         if (Zoom < 1.0f)
#             Zoom = 1.0f;
#         if (Zoom > 45.0f)
#             Zoom = 45.0f; 
#     }

# private:
#     // calculates the front vector from the Camera's (updated) Euler Angles
#     void updateCameraVectors()
#     {
#         // calculate the new Front vector
#         glm::vec3 front;
#         front.x = cos(glm::radians(Yaw)) * cos(glm::radians(Pitch));
#         front.y = sin(glm::radians(Pitch));
#         front.z = sin(glm::radians(Yaw)) * cos(glm::radians(Pitch));
#         Front = glm::normalize(front);
#         // also re-calculate the Right and Up vector
#         Right = glm::normalize(glm::cross(Front, WorldUp));  // normalize the vectors, because their length gets closer to 0 the more you look up or down which results in slower movement.
#         Up    = glm::normalize(glm::cross(Right, Front));
#     }
# };
# #endif