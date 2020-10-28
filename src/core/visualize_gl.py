
from OpenGL.GL import *    
from OpenGL.GLU import *    
from OpenGL.GLUT import *    
import numpy as np    

def draw_axis_gl():
    glBegin(GL_LINES)                    # 开始绘制线段（世界坐标系）    
    
    # 以红色绘制x轴    
    glColor4f(1.0, 0.0, 0.0, 1.0)        # 设置当前颜色为红色不透明    
    glVertex3f(0.0, 0.0, 0.0)           # 设置x轴顶点（x轴负方向）    
    glVertex3f(1.0, 0.0, 0.0)            # 设置x轴顶点（x轴正方向）    
    
    # 以绿色绘制y轴    
    glColor4f(0.0, 1.0, 0.0, 1.0)        # 设置当前颜色为绿色不透明    
    glVertex3f(0.0, 0.0, 0.0)           # 设置y轴顶点（y轴负方向）    
    glVertex3f(0.0, 1.0, 0.0)            # 设置y轴顶点（y轴正方向）    
    
    # 以蓝色绘制z轴    
    glColor4f(0.0, 0.0, 1.0, 1.0)        # 设置当前颜色为蓝色不透明    
    glVertex3f(0.0, 0.0, 0.0)           # 设置z轴顶点（z轴负方向）    
    glVertex3f(0.0, 0.0, 1.0)            # 设置z轴顶点（z轴正方向）  

    glEnd()                              # 结束绘制线段    
    return


def draw_obj_model_gl(model):
    glBegin(GL_POLYGON)                    # 开始绘制线段（世界坐标系）  
    for triangle in model:  
        
        # 以红色绘制x轴    
        glColor4f(0.0, 1.0, 0.0, 1)        # 设置当前颜色为红色不透明    
        glVertex3f(triangle[0][0] / 1000, triangle[0][1] / 1000, triangle[0][2] / 1000)           #
        glVertex3f(triangle[1][0] / 1000, triangle[1][1] / 1000, triangle[1][2] / 1000)           #
        glVertex3f(triangle[2][0] / 1000, triangle[2][1] / 1000, triangle[2][2] / 1000)           #
    glEnd()                              # 结束绘制线段    
    glutSwapBuffers()                    # 切换缓冲区，以显示绘制内容  
    return