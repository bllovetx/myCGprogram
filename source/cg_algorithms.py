#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 本文件只允许依赖math库
import math

def noswitch(x, y):
    return (x, y)

def switch(x, y):
    return (y, x)

# walk by a
def ellipse_walk(amin, amax, bmin, bmax, loc):
    resulta = []
    asum = amin + amax; da = amax - amin; da_sq = da*da
    bsum = bmin + bmax; db = bmax - bmin; db_sq = db*db
    a = (int) ( (asum + 1) / 2 )
    b = bmax
    walk = True
    p_slope = da_sq*(2*b - bsum) - db_sq*(2*a - asum)
    p_elli = db_sq*( (2*a + 2 - asum)**2 ) + da_sq*(1 - 2*db)  # 2*a - asum = 1 or 0 = ()*()  | a+1, b-1/2
    while walk:
        resulta.append( loc(a, b)   )
        resulta.append( loc(a, bsum-b)  )
        resulta.append( loc(asum-a, b)  )
        resulta.append( loc(asum-a, bsum-b) )
        if p_elli < 0:
            a = a + 1
            b = b
            p_elli = p_elli + 4*db_sq*(2*a + 1 - asum)
            p_slope = p_slope - 2*db_sq
        else:
            a = a + 1
            b = b - 1
            p_elli = p_elli + 4*db_sq*(2*a + 1 - asum) - 4*da_sq*(2*b - bsum)
            p_slope = p_slope  - 2*da_sq - 2*db_sq
        assert( p_elli == db_sq*(2*a + 2 - asum)**2 + da_sq*(2*b - 1 - bsum)**2 - da_sq*db_sq )
        walk = (p_slope > 0)
    return resulta

def draw_line(p_list, algorithm):
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    if algorithm == 'Naive':
        if x0 == x1:
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            k = (y1 - y0) / (x1 - x0)
            for x in range(x0, x1 + 1):
                result.append((x, int(y0 + k * (x - x0))))
    elif algorithm == 'DDA':
        if abs(x1 - x0) > abs(y1 - y0): # walk by x
            loc = noswitch
            (a0, b0, a1, b1) = (x0, y0, x1, y1) if x0 < x1 else (x1, y1, x0, y0)
        else:           # walk by y (containing the special case)
            loc = switch
            (a0, b0, a1, b1) = (y0, x0, y1, x1) if y0 < y1 else (y1, x1, y0, x0)
        # s.t a0 <= a1 && abs(a1 - a0) >= abs(b1 - b0)
        if a0 == a1:    # special case: x0 = x1 && y0 = y1
            result.append( (x0, y0) )
        else:
            k = (b1 - b0) / (a1 - a0)
            for a in range(a0, a1 + 1):
                b = b0 + k * (a - a0)
                result.append( loc(a, b) )
    elif algorithm == 'Bresenham':
        if abs(x1 - x0) > abs(y1 - y0): # walk by x
            loc = noswitch
            (a0, b0, a1, b1) = (x0, y0, x1, y1) if x0 < x1 else (x1, y1, x0, y0)
        else:           # walk by y (containing the special case, but need not handle seperately in this alg)
            loc = switch
            (a0, b0, a1, b1) = (y0, x0, y1, x1) if y0 < y1 else (y1, x1, y0, x0)
        # s.t a0 <= a1 && abs(a1 - a0) >= abs(b1 - b0)
        da = a1 - a0
        db = b1 - b0
        flag = 1 if db > 0 else -1
        determination = - da    # determination at n, k equals 2*n*abs(db) - (2*k+1)*da
        a = a0
        b = b0
        while a != a1 + 1:
            if determination < 0:
                determination = determination + 2*flag*db
                # b = b
            else:
                determination = determination + 2*flag*db - 2*da
                b = b + flag
            result.append( loc(a, b) )
            a = a + 1
    return result


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    for i in range(len(p_list)):
        line = draw_line([p_list[i - 1], p_list[i]], algorithm)
        result += line
    return result


def draw_ellipse(p_list):
    """绘制椭圆（采用中点圆生成算法）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    (xmin, xmax) = (x0, x1) if x0 < x1 else (x1, x0)
    (ymin, ymax) = (y0, y1) if y0 < y1 else (y1, y0)
    return ellipse_walk(xmin, xmax, ymin, ymax, noswitch) \
         + ellipse_walk(ymin, ymax, xmin, xmax, switch)
        



def draw_curve(p_list, algorithm):
    """绘制曲线

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    pass


def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    pass


def rotate(p_list, x, y, r):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    pass


def scale(p_list, x, y, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    pass


def clip(p_list, x_min, y_min, x_max, y_max, algorithm):
    """线段裁剪

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """
    pass
