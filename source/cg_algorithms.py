#!/usr/bin/env python
# -*- coding:utf-8 -*-

#############################################
# This is the Algorithm part of MyCGProgram # 
# Updated June 2021                         #
# By zxzq(https://zxzq.me)                  #
# See my github for detail of this program  #
# https://github.com/bllovetx/myCGprogram   #
#############################################


# 本文件只允许依赖math库
import math

bezier_steps = 1000
curve_try = 1/1000
max_search_step = 1000
topCode = 0b1000
botCode = 0b0100
rigCode = 0b0010
lefCode = 0b0001

# ---------------------------
# assist funcs
def noswitch(x, y):
    return (x, y)

def switch(x, y):
    return (y, x)

# func: walk by a
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

# func: mix point with para
def mix_point(pA:list, pB:list, t:float):
    assert(len(pA) == len(pB))
    mixed = []
    for i in range(len(pA)):
        mixed.append(t*pA[i] + (1-t)*pB[i])
    return mixed

def bezier_cal(p_list, t):
    last_list = p_list
    while len(last_list) > 1:
        cnt_list = []
        for j in range(len(last_list)-1):
            cnt_list.append(mix_point(last_list[j], last_list[j+1], t))
        last_list = cnt_list
    return (round(last_list[0][0]), round(last_list[0][1]))

def Bspline_cal(p_list, t):
    # t = j + x
        # j = 3, 4, ..., len -1
        # x in [0, 1)
        # t in [3, len)
    # N_j-3 = (1-x)^3/6 = (-x^3+3x^2-3x+1)/6
    # N_j-2 = (3x^3 - 6x^2 + 4)/6
    # N_j-1 = (-3x^3+3x^2+3x+1)/6
    # N_j-0 = x^3 / 6
    # P(t) = N_j-3 * P_j-3 + ... + N_j-0 * P_j-0
    PNum = len(p_list)
    assert(t>=3 and t<PNum)
    j = math.floor(t)
    x = t - j
    xsq = x*x
    xcub = x*xsq
    Nj_3 = (-  xcub + 3*xsq - 3*x + 1)/6
    Nj_2 = ( 3*xcub - 6*xsq       + 4)/6
    Nj_1 = (-3*xcub + 3*xsq + 3*x + 1)/6
    Nj_0 =     xcub                   /6
    return (round(Nj_3*p_list[j-3][0] + Nj_2*p_list[j-2][0] + Nj_1*p_list[j-1][0] + Nj_0*p_list[j][0]),\
            round(Nj_3*p_list[j-3][1] + Nj_2*p_list[j-2][1] + Nj_1*p_list[j-1][1] + Nj_0*p_list[j][1]))
    

# ---------------------------
# algorithms
def draw_line(p_list, algorithm):
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    if not p_list:
        return []
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
    result = []
    controlPNum = len(p_list)
    # set depend on algorithm
    if algorithm == 'Bezier':
        if controlPNum == 1:
            return p_list
        start_t = 0
        stop_t = 1
        curve_cal = bezier_cal 
    elif algorithm == 'B-spline':
        if controlPNum < 4:
            return []
        start_t = 3
        stop_t = controlPNum
        curve_cal = Bspline_cal
    # calculate
    t = start_t
    result.append( curve_cal(p_list, t) )
    (cnt_x, cnt_y) = result[-1]
    step = curve_try
    do_while_flag = True
    search_step = 0
    last_search_state = "start"
    factor = 2
    while do_while_flag:
        temp_t = t + step
        (temp_x, temp_y) = curve_cal(p_list, temp_t)
        step_x = abs(temp_x - cnt_x)
        step_y = abs(temp_y - cnt_y)
        max_step = max(step_x, step_y)
        if max_step > 1:    # step too large
            if last_search_state == "small":    # flip - reduce factor
                factor = math.sqrt(factor)
            step = step / factor
            search_step = search_step + 1
            last_search_state = "large"
        elif max_step == 0: # step too small
            if last_search_state == "large":    # flip - reduce factor
                factor = math.sqrt(factor)
            step = step * factor
            search_step = search_step + 1
            last_search_state = "small"
        elif temp_t > stop_t:    # suitable but out of range
            do_while_flag = False
        else:               # find suitable - update
            # commit result
            t = temp_t
            cnt_x = temp_x
            cnt_y = temp_y
            result.append((cnt_x, cnt_y))
            # init search
            search_step = 0
            factor = 2
            last_search_state = "start"
        if search_step > max_search_step:   # check dead loop
            assert(0 and "curve search fall into dead loop!")
        if algorithm == 'B-spline' and temp_t + step >= stop_t:# out of range is not permitted when calculationg for 'B-spline'
            do_while_flag = False
    return result

def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = []
    for point in p_list:
        result.append((point[0]+dx, point[1]+dy))
    return result

def rotate(p_list, x, y, r):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = []
    rad = r*math.pi/180
    sine = math.sin(rad)
    cosine = math.cos(rad)
    for p in p_list:
        result.append( (round(x + (p[0]-x)*cosine + (p[1]-y)*sine  ),\
                        round(y - (p[0]-x)*sine   + (p[1]-y)*cosine) \
            ) )
    return result


def scale(p_list, x, y, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = []
    for p in p_list:
        result.append( (round(x+(p[0]-x)*s),\
                        round(y+(p[1]-y)*s) \
            ))
    return result


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
    assert(x_min<=x_max and y_min<=y_max)
    if not p_list:
        return p_list
    (start, end) = p_list
    if algorithm == 'Cohen-Sutherland':
        # region: Coding EndPoint
        startCode = 0b0000
        endCode   = 0b0000
        if start[0] < x_min:
            startCode |= lefCode
        elif start[0] > x_max:
            startCode |= rigCode
        if start[1] < y_min:
            startCode |= botCode
        elif start[1] > y_max:
            startCode |= topCode
        if end[0] < x_min:
            endCode |= lefCode
        elif end[0] > x_max:
            endCode |= rigCode
        if end[1] < y_min:
            endCode |= botCode
        elif end[1] > y_max:
            endCode |= topCode
        #endregion
        if not (startCode|endCode): # both EndPoint in region 0b0000: trival accept
            return p_list
        if startCode&endCode:   # at both side: trival reject(TODO: Check gui)
            return []
        # non trival case:
            # find one out points
            # calculate nearest intersect
            # reduce to sub problem
        (outP, tarP) = (start, end) if startCode else (end, start)
        t_list = []
        delta_x = tarP[0] - outP[0]
        delta_y = tarP[1] - outP[1]
        if delta_x:
            tx_min = (x_min - outP[0]) / delta_x
            if tx_min > 0:
                t_list.append(tx_min)
            tx_max = (x_max - outP[0]) / delta_x
            if tx_max > 0:
                t_list.append(tx_max)
        if delta_y:
            ty_min = (y_min - outP[1]) / delta_y
            if ty_min > 0:
                t_list.append(ty_min)
            ty_max = (y_max - outP[1]) / delta_y
            if ty_max > 0:
                t_list.append(ty_max)
        assert(t_list)
        t_intersect = min(t_list)
        intP = [int(outP[0]+t_intersect*delta_x), int(outP[1]+t_intersect*delta_y)]
        return clip([intP, tarP], x_min, y_min, x_max, y_max, algorithm)
        
    elif algorithm == 'Liang-Barsky':
        p = [0, 0, 0, 0]
        p[0] = - (end[0] - start[0])
        p[1] = - p[0]
        p[2] = - (end[1] - start[1])
        p[3] = - p[2]
        q = [0, 0, 0, 0]
        q[0] = start[0] - x_min
        q[1] = x_max - start[0]
        q[2] = start[1] - y_min
        q[3] = y_max - start[1]
        for i in range(4):
            if (not p[i]) and (q[i] < 0):   # parralell and start is outside
                return []   # trival reject
        u1 = 0
        u2 = 1
        for i in range(4):
            if p[i] < 0:
                u1 = max(u1, q[i]/p[i])
            elif p[i] > 0:
                u2 = min(u2, q[i]/p[i])
        if u1 > u2:
            return []   # reject
        return [[int(start[0] + u1*p[1]), int(start[1] + u1*p[3])],\
                [int(start[0] + u2*p[1]), int(start[1] + u2*p[3])]]

