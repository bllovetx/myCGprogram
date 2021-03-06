#!/usr/bin/env python
# -*- coding:utf-8 -*-

#############################################
# This is the Gui part of MyCGProgram       # 
# Updated June 2021                         #
# By zxzq(https://zxzq.me)                  #
# See my github for detail of this program  #
# https://github.com/bllovetx/myCGprogram   #
#############################################

import sys

from PyQt5 import QtWidgets
import cg_algorithms as alg
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    qApp,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QListWidget,
    QHBoxLayout,
    QWidget,
    QStyleOptionGraphicsItem,
    QLabel,
    QLineEdit,
    QPushButton,
    QGridLayout,
    QColorDialog,
    QFileDialog,
    QInputDialog,
    QDialog)
from PyQt5.QtGui import QDoubleValidator, QPainter, QMouseEvent, QColor, QIcon, QImage, QIntValidator, QDesktopServices, QPolygonF, QPixmap, QMovie
from PyQt5.QtCore import QRect, QRectF, QUrl, QPointF, Qt, QSize, QPoint


class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.main_window = None
        self.list_widget = None
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        
        self.is_drawing = False
        self.is_moving = False
        self.is_scaling = False
        self.is_clipping = False
        self.edit_p_list = []
        self.setMouseTracking(True)
        self.pen_color = QColor(0, 0, 0)

    def start_draw_line(self, algorithm):
        self.status = 'line'
        self.temp_algorithm = algorithm
        self.start_draw()

    def start_draw_polygon(self, algorithm):
        self.status = 'polygon'
        self.temp_algorithm = algorithm
        self.start_draw()

    def start_draw_ellipse(self):
        self.status = 'ellipse'
        self.start_draw()

    def start_draw_curve(self, algorithm):
        self.status = 'curve'
        self.temp_algorithm = algorithm
        self.start_draw()

    def start_draw_arbitrary(self):
        self.status = 'arbitrary'
        self.start_draw()
    
    def start_clip(self, algorithm):
        assert(self.status == 'select')
        self.temp_algorithm = algorithm
        self.is_clipping = True
        self.edit_p_list = []

    # TODO: start_draw $other graphic$

    def start_draw(self):
        if self.temp_id == '':
            self.temp_id = self.main_window.get_id()

    def finish_draw(self):
        self.temp_id = self.main_window.get_id()
        self.is_drawing = False

    def clear_selection(self):
        if self.selected_id != '':
            assert(self.status == 'select')
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
            self.selected_id = ''
            self.status = ''
            self.is_drawing = False
            self.is_moving = False
            self.is_scaling = False
            self.is_clipping = False
            self.edit_p_list = []
        else:
            assert(self.status != 'select')

    def selection_changed(self, selected):
        self.clear_selection()
        if selected != '':
            self.selected_id = selected
            self.temp_item = self.item_dict[selected]
            self.temp_item.selected = True
            self.temp_item.update()
            self.status = 'select'
            self.main_window.statusBar().showMessage('图元选择： %s' % selected)
        self.updateScene([self.sceneRect()])

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        flag = event.button()   # no: 0; left: 1; right: 2; middle 4; side4: 16
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.is_drawing = True
            self.main_window.statusBar().showMessage('drawing line')
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.pen_color, self.temp_algorithm)
            self.scene().addItem(self.temp_item)
        elif self.status == 'polygon':
            if not self.is_drawing:               # start drawing
                self.is_drawing = True
                self.main_window.statusBar().showMessage('drawing polygon')
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y]], self.pen_color, self.temp_algorithm)
                self.scene().addItem(self.temp_item)
        elif self.status == 'ellipse':
            self.is_drawing = True
            self.main_window.statusBar().showMessage('drawing ellipse')
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.pen_color)
            self.scene().addItem(self.temp_item)
        elif self.status == 'curve':
            if not self.is_drawing:
                self.is_drawing = True
                self.main_window.statusBar().showMessage(f'drawing curve by {self.temp_algorithm}')
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y]], self.pen_color, self.temp_algorithm)
                self.scene().addItem(self.temp_item)
        elif self.status == 'arbitrary':
            self.is_drawing = True
            self.main_window.statusBar().showMessage('drawing arbitrarily')
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y]], self.pen_color)
            self.scene().addItem(self.temp_item)
        elif self.status == 'select':
            temp_RectF = self.temp_item.bound_Rect
            if self.is_clipping:    # NOTE:highest priority!!
                assert((not self.edit_p_list) and self.temp_item.item_type == 'line')
                self.temp_item.clippingRect = QRect(QPoint(x, y), QPoint(x, y))
                self.edit_p_list = [[x, y]] # [startP]
                self.main_window.statusBar().showMessage('Clipping line')
                self.temp_item.last_p_list = self.temp_item.p_list
            elif temp_RectF.contains(float(x), float(y)):
                self.is_moving = True
                self.main_window.statusBar().showMessage('translating')
                self.temp_item.last_p_list = self.temp_item.p_list
                self.edit_p_list = [[x, y]] # [startP]
            elif    self.temp_item.tr_RectF.contains(float(x), float(y))\
                 or self.temp_item.tl_RectF.contains(float(x), float(y))\
                 or self.temp_item.br_RectF.contains(float(x), float(y))\
                 or self.temp_item.bl_RectF.contains(float(x), float(y)):
                self.is_scaling = True
                self.main_window.statusBar().showMessage('scaling')
                self.temp_item.last_p_list = self.temp_item.p_list
                temp_center_x = temp_RectF.center().x()
                temp_center_y = temp_RectF.center().y()
                temp_signed_half_w = temp_RectF.width()/2  if (x>temp_center_x) else -temp_RectF.width()/2 
                temp_signed_half_h = temp_RectF.height()/2 if (y>temp_center_y) else -temp_RectF.height()/2
                temp_dis_x = (x-temp_center_x-temp_signed_half_w)
                temp_dis_y = (y-temp_center_y-temp_signed_half_h) 
                # [centerP, signed_halfWH, startReleventDisplace]
                self.edit_p_list = [[temp_center_x, temp_center_y], [temp_signed_half_w, temp_signed_half_h], [temp_dis_x, temp_dis_y]]
        # TODO: other status 
        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line' and self.is_drawing:
            self.temp_item.p_list[1] = [x, y]
        elif self.status == 'polygon' and self.is_drawing:
            self.temp_item.p_list[-1] = [x, y]
        elif self.status == 'ellipse' and self.is_drawing:
            self.temp_item.p_list[1] = [x, y]
        elif self.status == 'curve' and self.is_drawing:
            self.temp_item.p_list[-1] = [x, y]
        elif self.status == 'arbitrary' and self.is_drawing:
            self.temp_item.p_list.append([x, y])
        elif self.status == 'select':
            if self.is_clipping and self.edit_p_list:   # NOTE: clipping has highest priority
                self.temp_item.p_list = alg.clip(self.temp_item.last_p_list,\
                    min(self.edit_p_list[0][0], x), min(self.edit_p_list[0][1], y),\
                    max(self.edit_p_list[0][0], x), max(self.edit_p_list[0][1], y),\
                self.temp_algorithm)
                self.temp_item.clippingRect = QRect(QPoint(min(self.edit_p_list[0][0], x), min(self.edit_p_list[0][1], y)),\
                                                    QPoint(max(self.edit_p_list[0][0], x), max(self.edit_p_list[0][1], y)))
            elif self.is_moving:
                self.temp_item.p_list = alg.translate(self.temp_item.last_p_list, x - self.edit_p_list[0][0], y - self.edit_p_list[0][1])
            elif self.is_scaling:
                temp_sx = (x-self.edit_p_list[2][0]-self.edit_p_list[0][0])/self.edit_p_list[1][0]
                temp_sy = (y-self.edit_p_list[2][1]-self.edit_p_list[0][1])/self.edit_p_list[1][1]
                temp_s = temp_sx if (abs(temp_sx)>abs(temp_sy)) else temp_sy
                self.temp_item.p_list = alg.scale(self.temp_item.last_p_list, self.edit_p_list[0][0], self.edit_p_list[0][1], temp_s)

        # TODO: other status
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        flag = event.button()   # no: 0; left: 1; right: 2; middle 4; side4: 16
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.is_drawing = False
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status == 'polygon':
            if self.is_drawing:
                if flag == 2:   # right click: finish one polygon
                    self.item_dict[self.temp_id] = self.temp_item
                    self.list_widget.addItem(self.temp_id)
                    self.finish_draw()
                else:           # other click: add vertex
                    self.temp_item.p_list.append( [x, y] )
        elif self.status == 'ellipse':
            self.is_drawing = False
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status == 'curve':
            if self.is_drawing:
                if flag == 2:
                    self.item_dict[self.temp_id] = self.temp_item
                    self.list_widget.addItem(self.temp_id)
                    self.finish_draw()
                else:
                    self.temp_item.p_list.append( [x, y] )
        elif self.status == 'arbitrary':
            self.is_drawing = False
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status == 'select':
            if self.is_clipping and self.edit_p_list:
                self.edit_p_list = []
                self.temp_item.last_p_list = []
                self.temp_item.clippingRect = None
            elif self.is_moving:
                self.is_moving = False
                self.edit_p_list = []
                self.temp_item.last_p_list = []
            elif self.is_scaling:
                self.is_scaling = False
                self.edit_p_list = []
                self.temp_item.last_p_list = []
        # TODO: other status
        super().mouseReleaseEvent(event)

    def mycanvas_to_QImage(self):

        area = self.sceneRect()

        # Create image and painter to render
        temp_image = QImage(area.width(), area.height(), QImage.Format_ARGB32_Premultiplied)
        temp_painter = QPainter(temp_image)

        # Render area to image
        self.scene().render(temp_painter, QRectF(temp_image.rect()), area)
        temp_painter.end()

        return temp_image

    # Edit
    def mycanvas_translation(self, dx, dy):
        assert(self.status == 'select')
        self.temp_item.p_list = alg.translate(self.temp_item.p_list, dx, dy)

    def mycanvas_rotation(self, x, y, r):
        assert(self.status == 'select')
        self.temp_item.p_list = alg.rotate(self.temp_item.p_list, x, y, -r)
        # r is inverted since y is inverted
    
    def mycanvas_scaling(self, x, y, s):
        assert(self.status == 'select')
        self.temp_item.p_list = alg.scale(self.temp_item.p_list, x, y, s)

class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """
    def __init__(self, item_id: str, item_type: str, p_list: list, pen_color: QColor, algorithm: str = '', parent: QGraphicsItem = None):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id           # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list        # 图元参数
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.selected = False
        self.item_pen_color = pen_color
        self.bound_color = QColor(224, 0, 123)
        self.arrow_color = QColor(117, 193, 246)# purple: QColor(67, 27, 107)
        self.select_color = QColor(40, 44, 52, 50)
        self.last_alpha = 50

        self.last_p_list = []       # used when editting
        self.clippingRect = None
        self.bound_Rect = QRectF()
        self.tr_RectF = QRectF()
        self.tl_RectF = QRectF()
        self.br_RectF = QRectF()
        self.bl_RectF = QRectF()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.setPen(self.item_pen_color)
                painter.drawPoint(*p)
            if self.last_p_list:    # is Editting
                last_item_pixels = alg.draw_line(self.last_p_list, self.algorithm)
                for p in last_item_pixels:
                    last_pen_color = QColor(self.item_pen_color)
                    last_pen_color.setAlpha(self.last_alpha)
                    painter.setPen(last_pen_color)
                    painter.drawPoint(*p)
            if self.clippingRect:
                painter.setPen(Qt.NoPen)
                painter.setBrush(self.select_color)
                painter.drawRect(self.clippingRect)
            if self.selected:
                self.myDrawBound(painter)
        elif self.item_type == 'polygon':
            item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.setPen(self.item_pen_color)
                painter.drawPoint(*p)
            if self.last_p_list:    # is Editting
                last_item_pixels = alg.draw_polygon(self.last_p_list, self.algorithm)
                for p in last_item_pixels:
                    last_pen_color = QColor(self.item_pen_color)
                    last_pen_color.setAlpha(self.last_alpha)
                    painter.setPen(last_pen_color)
                    painter.drawPoint(*p)
            if self.selected:
                self.myDrawBound(painter)
        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list)
            for p in item_pixels:
                painter.setPen(self.item_pen_color)
                painter.drawPoint(*p)
            if self.last_p_list:    # is Editting
                last_item_pixels = alg.draw_ellipse(self.last_p_list)
                for p in last_item_pixels:
                    last_pen_color = QColor(self.item_pen_color)
                    last_pen_color.setAlpha(self.last_alpha)
                    painter.setPen(last_pen_color)
                    painter.drawPoint(*p)
            if self.selected:
                self.myDrawBound(painter)
        elif self.item_type == 'curve':
            item_pixels = alg.draw_curve(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.setPen(self.item_pen_color)
                painter.drawPoint(*p)
            if self.last_p_list:    # is Editting
                last_item_pixels = alg.draw_curve(self.last_p_list, self.algorithm)
                for p in last_item_pixels:
                    last_pen_color = QColor(self.item_pen_color)
                    last_pen_color.setAlpha(self.last_alpha)
                    painter.setPen(last_pen_color)
                    painter.drawPoint(*p)
            if self.selected:
                self.myDrawBound(painter)
        elif self.item_type == 'arbitrary':
            item_pixels = []
            p_list_len = len(self.p_list)  
            if p_list_len < 2:
                item_pixels = self.p_list
            else:
                for i in range(p_list_len - 1):
                    item_pixels += alg.draw_line(self.p_list[i:i+2], 'Bresenham')
            for p in item_pixels:
                painter.setPen(self.item_pen_color)
                painter.drawPoint(*p)
            if self.last_p_list:    # is Editting
                last_item_pixels = []
                last_p_list_len = len(self.last_p_list)
                if last_p_list_len < 2:
                    last_item_pixels = self.p_list
                else:
                    for i in range(last_p_list_len - 1):
                        last_item_pixels += alg.draw_line(self.last_p_list[i:i+2], 'Bresenham')
                for p in last_item_pixels:
                    last_pen_color = QColor(self.item_pen_color)
                    last_pen_color.setAlpha(self.last_alpha)
                    painter.setPen(last_pen_color)
                    painter.drawPoint(*p)
            if self.selected:
                self.myDrawBound(painter)
        # TODO:    ??

    def boundingRect(self) -> QRectF:
        if not self.p_list:
            return QRectF()
        if self.item_type == 'line':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        # TODO:
        elif self.item_type == 'polygon':
            (xmin, ymin) = self.p_list[0]
            (xmax, ymax) = self.p_list[0]
            for (x, y) in self.p_list:
                if x < xmin:
                    xmin = x
                if x > xmax:
                    xmax = x
                if y < ymin:
                    ymin = y
                if y > ymax:
                    ymax = y
            w = xmax - xmin
            h = ymax - ymin
            return QRectF(xmin - 1, ymin - 1, w + 2, h + 2)

        elif self.item_type == 'ellipse':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'curve':
            all_pixels = alg.draw_curve(self.p_list, self.algorithm)
            if not all_pixels:
                (xmin, ymin) = self.p_list[0]
                (xmax, ymax) = self.p_list[0]
            else:
                (xmin, ymin) = all_pixels[0]
                (xmax, ymax) = all_pixels[0]
            for (x, y) in all_pixels:
                if x < xmin:
                    xmin = x
                if x > xmax:
                    xmax = x
                if y < ymin:
                    ymin = y
                if y > ymax:
                    ymax = y
            w = xmax - xmin
            h = ymax - ymin
            return QRectF(xmin - 1, ymin - 1, w + 2, h + 2)
        elif self.item_type == 'arbitrary':
            (xmin, ymin) = self.p_list[0]
            (xmax, ymax) = self.p_list[0]
            for (x, y) in self.p_list:
                if x < xmin:
                    xmin = x
                if x > xmax:
                    xmax = x
                if y < ymin:
                    ymin = y
                if y > ymax:
                    ymax = y
            w = xmax - xmin
            h = ymax - ymin
            return QRectF(xmin - 1, ymin - 1, w + 2, h + 2)

    def myDrawBound(self, painter: QPainter):
        if not self.p_list:
            return
        # draw bounding box
        painter.setPen(self.bound_color)
        self.bound_Rect = self.boundingRect()
        painter.drawRect(self.bound_Rect)
        # draw four arrow at each corner R/L: right/left, T/B: top/bottom
        painter.setPen(self.arrow_color)
        painter.setBrush(self.arrow_color)
        tr_startP = self.bound_Rect.topRight()    + QPointF( 5,-5)
        tl_startP = self.bound_Rect.topLeft()     + QPointF(-5,-5)
        br_startP = self.bound_Rect.bottomRight() + QPointF( 5, 5)
        bl_startP = self.bound_Rect.bottomLeft()  + QPointF(-5, 5)
        tr_endP = tr_startP + QPointF( 15,-15)
        tl_endP = tl_startP + QPointF(-15,-15)
        br_endP = br_startP + QPointF( 15, 15)
        bl_endP = bl_startP + QPointF(-15, 15)
        tr_p1 = tr_endP + QPointF(-5, 0)
        tl_p1 = tl_endP + QPointF( 5, 0)
        br_p1 = br_endP + QPointF(-5, 0)
        bl_p1 = bl_endP + QPointF( 5, 0)
        tr_p2 = tr_endP + QPointF( 0, 5)
        tl_p2 = tl_endP + QPointF( 0, 5)
        br_p2 = br_endP + QPointF( 0,-5)
        bl_p2 = bl_endP + QPointF( 0,-5)
        painter.drawLine(tr_startP, tr_endP)
        painter.drawLine(tl_startP, tl_endP)
        painter.drawLine(br_startP, br_endP)
        painter.drawLine(bl_startP, bl_endP)
        tr_polygon = (QPolygonF() << tr_endP << tr_p1 << tr_p2)
        tl_polygon = (QPolygonF() << tl_endP << tl_p1 << tl_p2)
        br_polygon = (QPolygonF() << br_endP << br_p1 << br_p2)
        bl_polygon = (QPolygonF() << bl_endP << bl_p1 << bl_p2)
        painter.drawPolygon(tr_polygon)
        painter.drawPolygon(tl_polygon)
        painter.drawPolygon(br_polygon)
        painter.drawPolygon(bl_polygon)
        self.tr_RectF = QRectF(tr_startP, tr_endP)
        self.tl_RectF = QRectF(tl_startP, tl_endP)
        self.br_RectF = QRectF(br_startP, br_endP)
        self.bl_RectF = QRectF(bl_startP, bl_endP)

class MainWindow(QMainWindow):
    """
    主窗口类
    """
    def __init__(self):
        super().__init__()
        self.item_cnt = 0

        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(200)

        # 使用QGraphicsView作为画布
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 600, 600)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(600+5, 600+5)
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget

        self.setStyleSheet("""
            QMainWindow {
                background-color: #282c34;
                color: #bbbbbb;
            }
        """)
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #383e4a;
                color: #bbbbbb;
                border-radius: 10px;
                border: 2px solid rgb(37, 39, 48);
                padding: 10px
            }
        """)
        self.statusBar().setStyleSheet("background-color: #8897b4")
        self.menuBar().setStyleSheet("background-color: #8897b4")


        # 设置菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        set_pen_act = file_menu.addAction('设置画笔')
        reset_canvas_act = file_menu.addAction('重置画布')
        save_canvas_act = file_menu.addAction('保存画布')
        exit_act = file_menu.addAction('退出')
        draw_menu = menubar.addMenu('&Draw')
        line_menu = draw_menu.addMenu('线段')
        line_naive_act = line_menu.addAction('Naive')
        line_dda_act = line_menu.addAction('DDA')
        line_bresenham_act = line_menu.addAction('Bresenham')
        polygon_menu = draw_menu.addMenu('多边形')
        polygon_dda_act = polygon_menu.addAction('DDA')
        polygon_bresenham_act = polygon_menu.addAction('Bresenham')
        ellipse_act = draw_menu.addAction('椭圆')
        curve_menu = draw_menu.addMenu('曲线')
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_b_spline_act = curve_menu.addAction('B-spline')
        arbitrary_act = draw_menu.addAction('Arbitrary')
        edit_menu = menubar.addMenu('&Edit')
        translate_act = edit_menu.addAction('平移')
        rotate_act = edit_menu.addAction('旋转')
        scale_act = edit_menu.addAction('缩放')
        clip_menu = edit_menu.addMenu('裁剪')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')
        cancel_select_act = edit_menu.addAction('Cancel Select')
        help_menu = menubar.addMenu('&Help')
        github_act = help_menu.addAction('Github')
        php_act = help_menu.addAction('About Me')

        # 连接信号和槽函数
        exit_act.triggered.connect(qApp.quit)
        set_pen_act.triggered.connect(self.set_pen_action)
        reset_canvas_act.triggered.connect(self.reset_canvas_action)
        save_canvas_act.triggered.connect(self.save_canvas_action)
        # Draw
        ## line funcs
        line_naive_act.triggered.connect(self.line_naive_action)
        line_dda_act.triggered.connect(self.line_dda_action)
        line_bresenham_act.triggered.connect(self.line_bresenham_action)
        ## polygon funcs
        polygon_dda_act.triggered.connect(self.polygon_dda_action)
        polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)
        ## ellipse funcs
        ellipse_act.triggered.connect(self.ellipse_action)
        ## curve funcs
        curve_bezier_act.triggered.connect(self.curve_bezier_action)
        curve_b_spline_act.triggered.connect(self.curve_b_spline_action)
        arbitrary_act.triggered.connect(self.arbitrary_action)
        # Edit
        translate_act.triggered.connect(self.translate_action)
        rotate_act.triggered.connect(self.rotate_action)
        scale_act.triggered.connect(self.scale_action)
        clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action)
        clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)
        cancel_select_act.triggered.connect(self.cancel_select_action)
        # TODO: other func link
            # select funcs
        # Help actions
        github_act.triggered.connect(self.open_github_page)
        php_act.triggered.connect(self.open_my_php)
        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)

        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(600, 600)
        self.setWindowTitle('CG application - by 曾许曌秋(https://zxzq.me)')
        self.setWindowIcon(QIcon("./pics/favicon.ico"))

    def get_id(self):
        _id = str(self.item_cnt)
        self.item_cnt += 1
        return _id

    # File action
    def set_pen_action(self):
        self.canvas_widget.pen_color = QColorDialog.getColor()
        self.statusBar().showMessage('Pen color selected: %s' % self.canvas_widget.pen_color.name())

    def reset_canvas_action(self):
        # reset size
        widthHeightPara = {}
        whDialogue = WidthHeightDialog(widthHeightPara)
        whDialogue.exec_()
        if widthHeightPara["confirm"] == True:
            temp_width = int(widthHeightPara["width"])
            temp_height = int(widthHeightPara["height"])
            temp_color = widthHeightPara["color"]
            self.canvas_widget.setStyleSheet(f'QWidget {{background-color: {temp_color};}}')
            self.scene.setSceneRect(0, 0, temp_width, temp_height)
            self.canvas_widget.setFixedSize(temp_width + 5, temp_height + 5)
            self.resize(temp_width, temp_height)
            self.statusBar().showMessage(f'Reset canvas to width: {temp_width}, height: {temp_height}, background Color: {temp_color}')
            # reset window para
            self.item_cnt = 0
            # reset canvas
            self.canvas_widget.clear_selection()
            self.canvas_widget.item_dict = {}
            self.canvas_widget.status = ''
            self.canvas_widget.temp_algorithm = ''
            self.canvas_widget.temp_id = ''
            self.canvas_widget.temp_item = None   
            self.canvas_widget.is_drawing = False
            self.canvas_widget.pen_color = QColor(0, 0, 0)
            # reset scene
            self.scene.clear()
            # reset list_widget
            self.list_widget.clear()

    def save_canvas_action(self):
        # select savepath
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")

        # if path is blank exit
        if save_path == "":
            return
        
        # get image and save
        self.canvas_widget.mycanvas_to_QImage().save(save_path)

    # Draw action
    def line_naive_action(self):
        myListClearSelection(self.list_widget)
        self.canvas_widget.clear_selection()
        self.canvas_widget.start_draw_line('Naive')
        self.statusBar().showMessage('Naive算法绘制线段')

    def line_dda_action(self):
        myListClearSelection(self.list_widget)
        self.canvas_widget.clear_selection()
        self.canvas_widget.start_draw_line('DDA')
        self.statusBar().showMessage('DDA算法绘制线段')

    def line_bresenham_action(self):
        myListClearSelection(self.list_widget)
        self.canvas_widget.clear_selection()
        self.canvas_widget.start_draw_line('Bresenham')
        self.statusBar().showMessage('Bresenham算法绘制线段')

    def polygon_dda_action(self):
        myListClearSelection(self.list_widget)
        self.canvas_widget.clear_selection()
        self.canvas_widget.start_draw_polygon('DDA')
        self.statusBar().showMessage('DDA算法绘制多边形，右键结束')

    def polygon_bresenham_action(self):
        myListClearSelection(self.list_widget)
        self.canvas_widget.clear_selection()
        self.canvas_widget.start_draw_polygon('Bresenham')
        self.statusBar().showMessage('Bresenham算法绘制多边形，右键结束')


    def ellipse_action(self):
        myListClearSelection(self.list_widget)
        self.canvas_widget.clear_selection()
        self.canvas_widget.start_draw_ellipse()
        self.statusBar().showMessage('绘制椭圆')

    def curve_bezier_action(self):
        myListClearSelection(self.list_widget)
        self.canvas_widget.clear_selection()
        self.canvas_widget.start_draw_curve('Bezier')
        self.statusBar().showMessage('Bezier曲线绘制,单击添加控制点，右键结束')

    def curve_b_spline_action(self):
        myListClearSelection(self.list_widget)
        self.canvas_widget.clear_selection()
        self.canvas_widget.start_draw_curve('B-spline')
        self.statusBar().showMessage('B-spline曲线绘制,单击添加控制点，右键结束')

    def arbitrary_action(self):
        myListClearSelection(self.list_widget)
        self.canvas_widget.clear_selection()
        self.canvas_widget.start_draw_arbitrary()
        self.statusBar().showMessage('自由绘制')
    # Edit action
    def translate_action(self):
        if self.canvas_widget.selected_id == '':    # item not selected
            self.statusBar().showMessage('Please select item in list widget first!')
            return
        translatePara = {}
        tslDialogue = TranslationDialog(translatePara)
        tslDialogue.exec_()
        if translatePara["confirm"] == True:
            temp_dx = int(translatePara["dx"])
            temp_dy = int(translatePara["dy"])
            self.canvas_widget.mycanvas_translation(temp_dx, temp_dy)
            self.statusBar().showMessage(f'Translation dx = {temp_dx}, dy = {temp_dy} succeed')
        else:
            self.statusBar().showMessage('Translation canceled')

    def rotate_action(self):
        temp_selected_id = self.canvas_widget.selected_id
        if temp_selected_id == '':    # item not selected
            self.statusBar().showMessage('Please select item in list widget first!')
            return
        temp_item = self.canvas_widget.item_dict[temp_selected_id]
        if temp_item.item_type == 'ellipse':
            self.statusBar().showMessage('ellipse should not be rotated!')
            return
        rotatePara = {}
        RectF_center_x = int(temp_item.bound_Rect.center().x())
        RectF_center_y = int(temp_item.bound_Rect.center().y())
        rotDialogue = RotationDialog(rotatePara, RectF_center_x, RectF_center_y)
        rotDialogue.exec_()
        if rotatePara["confirm"] == True:
            temp_x = int(rotatePara["x"])
            temp_y = int(rotatePara["y"])
            temp_r = int(rotatePara["r"])
            self.canvas_widget.mycanvas_rotation(temp_x, temp_y, temp_r)
            self.statusBar().showMessage(f'Rotation x = {temp_x}, y = {temp_y}, r = {temp_r}deg succeed')
        else:
            self.statusBar().showMessage('Rotation canceled')

    def scale_action(self):
        temp_selected_id = self.canvas_widget.selected_id
        if temp_selected_id == '':    # item not selected
            self.statusBar().showMessage('Please select item in list widget first!')
            return
        temp_item = self.canvas_widget.item_dict[temp_selected_id]
        scalePara = {}
        RectF_center_x = int(temp_item.bound_Rect.center().x())
        RectF_center_y = int(temp_item.bound_Rect.center().y())
        sDialogue = ScalingDialog(scalePara, RectF_center_x, RectF_center_y)
        sDialogue.exec_()
        if scalePara["confirm"] == True:
            temp_x = int(scalePara["x"])
            temp_y = int(scalePara["y"])
            temp_s = int(scalePara["s"])
            self.canvas_widget.mycanvas_scaling(temp_x, temp_y, temp_s)
            self.statusBar().showMessage(f'Scaling x = {temp_x}, y = {temp_y}, s = {temp_s} succeed')
        else:
            self.statusBar().showMessage('Scaling canceled')

    def clip_cohen_sutherland_action(self):
        temp_selected_id = self.canvas_widget.selected_id
        if temp_selected_id == '':   # item not selected
            self.statusBar().showMessage('Please select item in list widget first!')
            return
        temp_item = self.canvas_widget.item_dict[temp_selected_id]
        if temp_item.item_type != 'line':   # selected item invalid
            self.statusBar().showMessage('Only segment line can be clipped!')
            return
        self.canvas_widget.start_clip('Cohen-Sutherland')
        self.statusBar().showMessage('Start clip using Cohen-Sutherland algorithm')

    def clip_liang_barsky_action(self):
        temp_selected_id = self.canvas_widget.selected_id
        if temp_selected_id == '':   # item not selected
            self.statusBar().showMessage('Please select item in list widget first!')
            return
        temp_item = self.canvas_widget.item_dict[temp_selected_id]
        if temp_item.item_type != 'line':   # selected item invalid
            self.statusBar().showMessage('Only segment line can be clipped!')
            return
        self.canvas_widget.start_clip('Liang-Barsky')
        self.statusBar().showMessage('Start clip using Liang-Barsky algorithm')

    def cancel_select_action(self):
        myListClearSelection(self.list_widget)
        self.canvas_widget.clear_selection()
    # TODO: realise other action funcs

    # Help menu actions
    def open_github_page(self):
        QDesktopServices.openUrl(QUrl("https://github.com/bllovetx/myCGprogram"))

    def open_my_php(self):
        QDesktopServices.openUrl(QUrl("https://zxzq.me"))

class WidthHeightDialog(QDialog):
    def __init__(self, para): 
        # para = {"width": width="600", "height": height="600", "color": Hex="#ffffff", "confirm": confirm = False}      
        super(WidthHeightDialog,self).__init__()

        self.para = para
        self.para["width"] = "600"
        self.para["height"] = "600"
        self.para["color"] = "#ffffff"
        self.para["confirm"] = False
        
        # set self theme
        self.setStyleSheet("""
            QWidget {
                background-color: #282c34;
                color: #bbbbbb;
            }
        """)
        self.setWindowTitle("Reset Size of Canvas")
        self.setWindowIcon(QIcon("./pics/favicon.ico"))

        self.widthLabel = QLabel("Width: ")
        self.heightLabel= QLabel("Height: ")
        self.colorLabel = QLabel("Color: ")

        self.widthEdit = QLineEdit()   
        self.widthEdit.setPlaceholderText("600")
        self.widthEdit.setValidator(QIntValidator())
        self.widthEdit.setStyleSheet("""
            QLineEdit {
                background-color: #383e4a;
                color: #bbbbbb;
                border-radius: 10px;
                border: 2px solid rgb(37, 39, 48);
                height: 30px;
                padding: 0px 10px
            }
        """)
        self.heightEdit = QLineEdit()   
        self.heightEdit.setPlaceholderText("600")
        self.heightEdit.setValidator(QIntValidator())
        self.heightEdit.setStyleSheet("""
            QLineEdit {
                background-color: #383e4a;
                color: #bbbbbb;
                border-radius: 10px;
                border: 2px solid rgb(37, 39, 48);
                height: 30px;
                padding: 0px 10px;
            }
        """)
        self.colorSelected = QLabel()
        self.colorSelected.setText("#ffffff")
        self.colorSelected.setStyleSheet("""
            QLabel {
                background-color: #383e4a;
                color: #bbbbbb;
                border-radius: 10px;
                border: 2px solid rgb(37, 39, 48);
                height: 30px;
                padding: 0px 10px;
            }
        """)

        self.confirmButton = QPushButton("Confirm")
        self.cancelButton = QPushButton("Cancel")
        self.confirmButton.clicked.connect(self.confirm_act)
        self.cancelButton.clicked.connect(self.cancel_act)
        self.getColorButton = QPushButton("Select")
        self.getColorButton.clicked.connect(self.getColor_act)

        self.right_pic = QPixmap('pics/wlop_bg.jpg')
        self.pic_widget = QtWidgets.QLabel()
        self.pic_widget.setPixmap(self.right_pic.scaled(260, 260, Qt.KeepAspectRatio))
        self.pic_widget.setMaximumSize(150, 150)


        mainLayout = QGridLayout()
        mainLayout.addWidget(self.widthLabel,      0, 0)
        mainLayout.addWidget(self.widthEdit,       0, 1, 1, 2)
        mainLayout.addWidget(self.heightLabel,     1, 0)
        mainLayout.addWidget(self.heightEdit,      1, 1, 1, 2)
        mainLayout.addWidget(self.colorLabel,      2, 0)
        mainLayout.addWidget(self.colorSelected,   2, 1)
        mainLayout.addWidget(self.getColorButton,  2, 2)
        mainLayout.setColumnMinimumWidth(1, 130)
        mainLayout.setColumnMinimumWidth(2, 130)
        mainLayout.addWidget(self.confirmButton,   3, 1)        
        mainLayout.addWidget(self.cancelButton,    3, 2)        
        mainLayout.setRowStretch(3, 1)
        mainLayout.setHorizontalSpacing(15)
        mainLayout.setVerticalSpacing(5)
        mainLayout.addWidget(self.pic_widget,      0, 3, 4, 3)
        self.setLayout(mainLayout)

    def getColor_act (self):
        self.colorSelected.setText(QColorDialog.getColor().name())

    def confirm_act (self):
        self.para["width"] = self.widthEdit.placeholderText() if (self.widthEdit.text() == '') else self.widthEdit.text()
        self.para["height"] = self.heightEdit.placeholderText() if (self.heightEdit.text() == '') else self.heightEdit.text()
        self.para["color"] = self.colorSelected.text()
        self.para["confirm"] = True
        self.close()

    def cancel_act (self):
        self.para["confirm"] = False
        self.close()

class TranslationDialog(QDialog):
    def __init__(self, para): 
        # para = {"dx": dx="0", "dy": dy="0", "confirm": confirm = False}      
        super(TranslationDialog,self).__init__()

        self.para = para
        self.para["dx"] = "0"
        self.para["dy"] = "0"
        self.para["confirm"] = False
        
        # set self theme
        self.setStyleSheet("""
            QWidget {
                background-color: #282c34;
                color: #bbbbbb;
            }
        """)
        self.setWindowTitle("Translation")
        self.setWindowIcon(QIcon("./pics/favicon.ico"))

        self.dxLabel = QLabel("x displacement: ")
        self.dyLabel= QLabel("y displacement: ")

        self.dxEdit = QLineEdit()   
        self.dxEdit.setPlaceholderText("0")
        self.dxEdit.setValidator(QIntValidator())
        self.dxEdit.setStyleSheet("""
            QLineEdit {
                background-color: #383e4a;
                color: #bbbbbb;
                border-radius: 10px;
                border: 2px solid rgb(37, 39, 48);
                height: 30px;
                padding: 0px 10px
            }
        """)
        self.dyEdit = QLineEdit()   
        self.dyEdit.setPlaceholderText("0")
        self.dyEdit.setValidator(QIntValidator())
        self.dyEdit.setStyleSheet("""
            QLineEdit {
                background-color: #383e4a;
                color: #bbbbbb;
                border-radius: 10px;
                border: 2px solid rgb(37, 39, 48);
                height: 30px;
                padding: 0px 10px;
            }
        """)

        self.confirmButton = QPushButton("Confirm")
        self.cancelButton = QPushButton("Cancel")
        self.confirmButton.clicked.connect(self.confirm_act)
        self.cancelButton.clicked.connect(self.cancel_act)

        self.right_pic = QPixmap('pics/wlop_bg2.jpg')
        self.pic_widget = QtWidgets.QLabel()
        self.pic_widget.setPixmap(self.right_pic.scaled(130, 130, Qt.KeepAspectRatio))
        self.pic_widget.setMaximumSize(130, 110)

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.dxLabel,      0, 0)
        mainLayout.addWidget(self.dxEdit,       0, 1, 1, 2)
        mainLayout.addWidget(self.dyLabel,     1, 0)
        mainLayout.addWidget(self.dyEdit,      1, 1, 1, 2)
        mainLayout.setColumnMinimumWidth(1, 130)
        mainLayout.setColumnMinimumWidth(2, 130)
        mainLayout.addWidget(self.confirmButton,   2, 1)        
        mainLayout.addWidget(self.cancelButton,    2, 2)   
        mainLayout.addWidget(self.pic_widget,      0, 3, 4, 3)     
        mainLayout.setRowStretch(3, 1)
        mainLayout.setHorizontalSpacing(15)
        mainLayout.setVerticalSpacing(5)
        self.setLayout(mainLayout)

    def confirm_act (self):
        self.para["dx"] = self.dxEdit.placeholderText() if (self.dxEdit.text() == '') else self.dxEdit.text()
        self.para["dy"] = self.dyEdit.placeholderText() if (self.dyEdit.text() == '') else self.dyEdit.text()
        self.para["confirm"] = True
        self.close()

    def cancel_act (self):
        self.para["confirm"] = False
        self.close()

class RotationDialog(QDialog):
    def __init__(self, para, default_x, default_y): 
        # para = {"x": center_x=RectF.center_x, "y": center_y=RectF.center_y, "r": radius = 0 deg, "confirm": confirm = False}      
        super(RotationDialog,self).__init__()

        self.para = para
        self.para["x"] = str(default_x)
        self.para["y"] = str(default_y)
        self.para["r"] = '0'
        self.para["confirm"] = False
        
        # set self theme
        self.setStyleSheet("""
            QWidget {
                background-color: #282c34;
                color: #bbbbbb;
            }
        """)
        self.setWindowTitle("Rotation")
        self.setWindowIcon(QIcon("./pics/favicon.ico"))

        self.descriptionLabel = QLabel("Default center is the center of bounding box")
        self.descriptionLabel.setStyleSheet("color: #68748a")
        self.xLabel = QLabel("center x: ")
        self.yLabel = QLabel("center y: ")
        self.rLabel = QLabel("deg(clockwise): ")

        self.xEdit = QLineEdit()   
        self.xEdit.setPlaceholderText(str(default_x))
        self.xEdit.setValidator(QIntValidator())
        self.xEdit.setStyleSheet("""
            QLineEdit {
                background-color: #383e4a;
                color: #bbbbbb;
                border-radius: 10px;
                border: 2px solid rgb(37, 39, 48);
                height: 30px;
                padding: 0px 10px
            }
        """)
        self.yEdit = QLineEdit()   
        self.yEdit.setPlaceholderText(str(default_y))
        self.yEdit.setValidator(QIntValidator())
        self.yEdit.setStyleSheet("""
            QLineEdit {
                background-color: #383e4a;
                color: #bbbbbb;
                border-radius: 10px;
                border: 2px solid rgb(37, 39, 48);
                height: 30px;
                padding: 0px 10px;
            }
        """)
        self.rEdit = QLineEdit()   
        self.rEdit.setPlaceholderText("0")
        self.rEdit.setValidator(QDoubleValidator())
        self.rEdit.setStyleSheet("""
            QLineEdit {
                background-color: #383e4a;
                color: #bbbbbb;
                border-radius: 10px;
                border: 2px solid rgb(37, 39, 48);
                height: 30px;
                padding: 0px 10px;
            }
        """)

        self.confirmButton = QPushButton("Confirm")
        self.cancelButton = QPushButton("Cancel")
        self.confirmButton.clicked.connect(self.confirm_act)
        self.cancelButton.clicked.connect(self.cancel_act)

        self.pic_widget = QtWidgets.QLabel()
        self.pic_widget.setMaximumSize(140, 180)
        self.megumin2 = QMovie('pics/megumin2.webp')
        self.megumin2.setScaledSize(QSize(140, 180))
        self.pic_widget.setMovie(self.megumin2)
        self.megumin2.start()

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.descriptionLabel,0, 0, 1, 3)
        mainLayout.addWidget(self.xLabel,          1, 0)
        mainLayout.addWidget(self.xEdit,           1, 1, 1, 2)
        mainLayout.addWidget(self.yLabel,          2, 0)
        mainLayout.addWidget(self.yEdit,           2, 1, 1, 2)
        mainLayout.addWidget(self.rLabel,          3, 0)
        mainLayout.addWidget(self.rEdit,           3, 1, 1, 2)
        mainLayout.setColumnMinimumWidth(1, 130)
        mainLayout.setColumnMinimumWidth(2, 130)
        mainLayout.addWidget(self.confirmButton,   4, 1)        
        mainLayout.addWidget(self.cancelButton,    4, 2) 
        mainLayout.addWidget(self.pic_widget,      0, 3, 5, 3)    
        mainLayout.setRowStretch(3, 1)
        mainLayout.setHorizontalSpacing(15)
        mainLayout.setVerticalSpacing(5)
        self.setLayout(mainLayout)

    def confirm_act (self):
        self.para["x"] = self.xEdit.placeholderText() if (self.xEdit.text() == '') else self.xEdit.text()
        self.para["y"] = self.yEdit.placeholderText() if (self.yEdit.text() == '') else self.yEdit.text()
        self.para["r"] = self.rEdit.placeholderText() if (self.rEdit.text() == '') else self.rEdit.text()
        self.para["confirm"] = True
        self.close()

    def cancel_act (self):
        self.para["confirm"] = False
        self.close()

class ScalingDialog(QDialog):
    def __init__(self, para, default_x, default_y): 
        # para = {"x": center_x=RectF.center_x, "y": center_y=RectF.center_y, "s": scale = 1, "confirm": confirm = False}      
        super(ScalingDialog,self).__init__()

        self.para = para
        self.para["x"] = str(default_x)
        self.para["y"] = str(default_y)
        self.para["s"] = '1'
        self.para["confirm"] = False
        
        # set self theme
        self.setStyleSheet("""
            QWidget {
                background-color: #282c34;
                color: #bbbbbb;
            }
        """)
        self.setWindowTitle("Scaling")
        self.setWindowIcon(QIcon("./pics/favicon.ico"))

        self.descriptionLabel = QLabel("Default center is the center of bounding box")
        self.descriptionLabel.setStyleSheet("color: #68748a")
        self.xLabel = QLabel("center x: ")
        self.yLabel = QLabel("center y: ")
        self.sLabel = QLabel("scale ratio: ")

        self.xEdit = QLineEdit()   
        self.xEdit.setPlaceholderText(str(default_x))
        self.xEdit.setValidator(QIntValidator())
        self.xEdit.setStyleSheet("""
            QLineEdit {
                background-color: #383e4a;
                color: #bbbbbb;
                border-radius: 10px;
                border: 2px solid rgb(37, 39, 48);
                height: 30px;
                padding: 0px 10px
            }
        """)
        self.yEdit = QLineEdit()   
        self.yEdit.setPlaceholderText(str(default_y))
        self.yEdit.setValidator(QIntValidator())
        self.yEdit.setStyleSheet("""
            QLineEdit {
                background-color: #383e4a;
                color: #bbbbbb;
                border-radius: 10px;
                border: 2px solid rgb(37, 39, 48);
                height: 30px;
                padding: 0px 10px;
            }
        """)
        self.sEdit = QLineEdit()   
        self.sEdit.setPlaceholderText("1")
        self.sEdit.setValidator(QDoubleValidator())
        self.sEdit.setStyleSheet("""
            QLineEdit {
                background-color: #383e4a;
                color: #bbbbbb;
                border-radius: 10px;
                border: 2px solid rgb(37, 39, 48);
                height: 30px;
                padding: 0px 10px;
            }
        """)


        self.confirmButton = QPushButton("Confirm")
        self.cancelButton = QPushButton("Cancel")
        self.confirmButton.clicked.connect(self.confirm_act)
        self.cancelButton.clicked.connect(self.cancel_act)

        self.right_pic = QPixmap('pics/YDIYA.jpg')
        self.pic_widget = QtWidgets.QLabel()
        self.pic_widget.setPixmap(self.right_pic.scaled(230, 260, Qt.KeepAspectRatio))
        self.pic_widget.setMaximumSize(130, 180)

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.descriptionLabel,0, 0, 1, 3)
        mainLayout.addWidget(self.xLabel,          1, 0)
        mainLayout.addWidget(self.xEdit,           1, 1, 1, 2)
        mainLayout.addWidget(self.yLabel,          2, 0)
        mainLayout.addWidget(self.yEdit,           2, 1, 1, 2)
        mainLayout.addWidget(self.sLabel,          3, 0)
        mainLayout.addWidget(self.sEdit,           3, 1, 1, 2)
        mainLayout.setColumnMinimumWidth(1, 130)
        mainLayout.setColumnMinimumWidth(2, 130)
        mainLayout.addWidget(self.confirmButton,   4, 1)        
        mainLayout.addWidget(self.cancelButton,    4, 2)  
        mainLayout.addWidget(self.pic_widget,      0, 3, 5, 3) 
        mainLayout.setRowStretch(3, 1)
        mainLayout.setHorizontalSpacing(15)
        mainLayout.setVerticalSpacing(5)
        self.setLayout(mainLayout)

    def confirm_act (self):
        self.para["x"] = self.xEdit.placeholderText() if (self.xEdit.text() == '') else self.xEdit.text()
        self.para["y"] = self.yEdit.placeholderText() if (self.yEdit.text() == '') else self.yEdit.text()
        self.para["s"] = self.sEdit.placeholderText() if (self.sEdit.text() == '') else self.sEdit.text()
        self.para["confirm"] = True
        self.close()

    def cancel_act (self):
        self.para["confirm"] = False
        self.close()


def myListClearSelection(myListWidget:QListWidget):
    """
    QListWidget.clearSelection do not change current item
    and current Text consequently, which cause 'currentTextChanged'
    not triggered when reselecting the same item!
    """
    myListWidget.clearSelection()
    myListWidget.setCurrentItem(None)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
