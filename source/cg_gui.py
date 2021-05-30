#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
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
from PyQt5.QtGui import QPainter, QMouseEvent, QColor, QIcon, QImage, QIntValidator, QDesktopServices, QPolygonF
from PyQt5.QtCore import QRectF, QUrl, QPointF


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
    
    # TODO: start_draw $other graphic$

    def start_draw(self):
        if self.temp_id == '':
            self.temp_id = self.main_window.get_id()

    def finish_draw(self):
        self.temp_id = self.main_window.get_id()
        self.is_drawing = False

    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''

    def selection_changed(self, selected):
        if selected == '':
            return
        self.main_window.statusBar().showMessage('图元选择： %s' % selected)
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
        self.selected_id = selected
        self.item_dict[selected].selected = True
        self.item_dict[selected].update()
        self.status = 'select'
        self.updateScene([self.sceneRect()])

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        flag = event.button()   # no: 0; left: 1; right: 2; middle 4; side4: 16
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.is_drawing = True
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.pen_color, self.temp_algorithm)
            self.scene().addItem(self.temp_item)
        elif self.status == 'polygon':
            if not self.is_drawing:               # start drawing
                self.is_drawing = True
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y]], self.pen_color, self.temp_algorithm)
                self.scene().addItem(self.temp_item)
        elif self.status == 'ellipse':
            self.is_drawing = True
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.pen_color)
            self.scene().addItem(self.temp_item)
        elif self.status == 'curve' and self.temp_algorithm == 'Bezier':
            if not self.is_drawing:
                self.is_drawing = True
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y]], self.pen_color, self.temp_algorithm)
                self.scene().addItem(self.temp_item)
        elif self.status == 'select':
            self.temp_item = self.item_dict[self.selected_id]
            temp_RectF = self.temp_item.bound_Rect
            if temp_RectF.contains(float(x), float(y)):
                self.is_moving = True
                self.temp_item.last_p_list = self.temp_item.p_list
                self.edit_p_list = [[x, y]] # [startP]
            elif    self.temp_item.tr_RectF.contains(float(x), float(y))\
                 or self.temp_item.tl_RectF.contains(float(x), float(y))\
                 or self.temp_item.br_RectF.contains(float(x), float(y))\
                 or self.temp_item.bl_RectF.contains(float(x), float(y)):
                self.is_scaling = True
                self.temp_item.last_p_list = self.temp_item.p_list
                temp_center_x = temp_RectF.center().x()
                temp_center_y = temp_RectF.center().y()
                temp_half_w = temp_RectF.width()/2
                temp_half_h = temp_RectF.height()/2
                temp_dis_x = (x-temp_center_x-temp_half_w) if (x>temp_center_x) else (x-temp_center_x+temp_half_w)
                temp_dis_y = (y-temp_center_y-temp_half_h) if (y>temp_center_y) else (y-temp_center_y+temp_half_h) 
                # [centerP, halfWH, startReleventDisplace]
                self.edit_p_list = [[temp_center_x, temp_center_y], [temp_half_w, temp_half_h], [temp_dis_x, temp_dis_y]]
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
        elif self.status == 'curve' and self.temp_algorithm == 'Bezier' and self.is_drawing:
            self.temp_item.p_list[-1] = [x, y]
        elif self.status == 'select':
            if self.is_moving:
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
        elif self.status == 'curve' and self.temp_algorithm == 'Bezier':
            if self.is_drawing:
                if flag == 2:
                    self.item_dict[self.temp_id] = self.temp_item
                    self.list_widget.addItem(self.temp_id)
                    self.finish_draw()
                else:
                    self.temp_item.p_list.append( [x, y] )
        elif self.status == 'select':
            if self.is_moving:
                self.is_moving = False
                self.edit_p_list = []
            elif self.is_scaling:
                self.is_scaling = False
                self.edit_p_list = []
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

        self.last_p_list = []       # used when editting
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
            if self.selected:
                self.myDrawBound(painter)
        elif self.item_type == 'polygon':
            item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.setPen(self.item_pen_color)
                painter.drawPoint(*p)
            if self.selected:
                self.myDrawBound(painter)
        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list)
            for p in item_pixels:
                painter.setPen(self.item_pen_color)
                painter.drawPoint(*p)
            if self.selected:
                self.myDrawBound(painter)
        elif self.item_type == 'curve':
            item_pixels = alg.draw_curve(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.setPen(self.item_pen_color)
                painter.drawPoint(*p)
            if self.selected:
                self.myDrawBound(painter)
        # TODO:    ??

    def boundingRect(self) -> QRectF:
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

    def myDrawBound(self, painter: QPainter):
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
        edit_menu = menubar.addMenu('&Edit')
        translate_act = edit_menu.addAction('平移')
        rotate_act = edit_menu.addAction('旋转')
        scale_act = edit_menu.addAction('缩放')
        clip_menu = edit_menu.addMenu('裁剪')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')
        help_menu = menubar.addMenu('&Help')
        github_act = help_menu.addAction('Github')
        php_act = help_menu.addAction('About Me')

        # 连接信号和槽函数
        exit_act.triggered.connect(qApp.quit)
        set_pen_act.triggered.connect(self.set_pen_action)
        reset_canvas_act.triggered.connect(self.reset_canvas_action)
        save_canvas_act.triggered.connect(self.save_canvas_action)
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
            # reset scene
            self.scene.clear()
            # reset canvas
            self.canvas_widget.item_dict = {}
            self.canvas_widget.selected_id = ''
            self.canvas_widget.status = ''
            self.canvas_widget.temp_algorithm = ''
            self.canvas_widget.temp_id = ''
            self.canvas_widget.temp_item = None   
            self.canvas_widget.is_drawing = False
            self.canvas_widget.pen_color = QColor(0, 0, 0)
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

    def line_naive_action(self):
        self.canvas_widget.start_draw_line('Naive')
        self.statusBar().showMessage('Naive算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_dda_action(self):
        self.canvas_widget.start_draw_line('DDA')
        self.statusBar().showMessage('DDA算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_bresenham_action(self):
        self.canvas_widget.start_draw_line('Bresenham')
        self.statusBar().showMessage('Bresenham算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_dda_action(self):
        self.canvas_widget.start_draw_polygon('DDA')
        self.statusBar().showMessage('DDA算法绘制多边形，右键结束')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_bresenham_action(self):
        self.canvas_widget.start_draw_polygon('Bresenham')
        self.statusBar().showMessage('Bresenham算法绘制多边形，右键结束')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()


    def ellipse_action(self):
        self.canvas_widget.start_draw_ellipse()
        self.statusBar().showMessage('绘制椭圆')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_bezier_action(self):
        self.canvas_widget.start_draw_curve('Bezier')
        self.statusBar().showMessage('Bezier曲线绘制,单击添加控制点，右键结束')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    # TODO: realise other action funcs

    # Help menu actions
    def open_github_page(self):
        QDesktopServices.openUrl(QUrl("https://github.com/bllovetx/myCGprogram"))

    def open_my_php(self):
        QDesktopServices.openUrl(QUrl("https://zxzq.me"))

class WidthHeightDialog(QDialog):
    def __init__(self, para): 
        # para = {"width": width=600, "height": height=600, "color": Hex="#ffffff", "confirm": confirm = False}      
        super(WidthHeightDialog,self).__init__()

        self.para = para
        self.para["width"] = 600
        self.para["height"] = 600
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
